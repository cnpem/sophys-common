import logging
from typing import Optional

from ophyd import (
    ADComponent,
    Device,
    EpicsSignal,
    EpicsSignalWithRBV,
    EpicsSignalNoValidation,
    Kind,
    SingleTrigger,
)
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.plugins import (
    TransformPlugin_V34 as TransformPlugin,
    ROIPlugin_V34 as ROIPlugin,
    ROIStatPlugin_V34 as ROIStatPlugin,
    ROIStatNPlugin_V25 as ROIStatNPlugin,
)
from ophyd.signal import Signal, InternalSignal
from ophyd.utils.errors import WaitTimeoutError

from ..utils import HDF5PluginWithFileStore, EpicsSignalWithCustomReadoutRBV
from .cam import CamBase_V33


class MobipixError(Exception): ...


class MobipixMissingConfigurationError(MobipixError): ...


class MobipixCam(CamBase_V33): ...


class MobipixBackend(Device):
    num_exposures = ADComponent(EpicsSignalWithRBV, "num_exposures")

    acquire = ADComponent(EpicsSignal, "acquire")
    """
    The Backend 'acquire' signal. This will tell the Backend to make an image.

    It is an error to set the signal without first activating 'cam.Acquire', as
    that creates the connection between the driver and the backend.
    """

    acquire_time = ADComponent(
        EpicsSignalWithCustomReadoutRBV,
        "acquire_time",
        tolerance=1e-5,
        enforce_type=float,
    )  # NOTE: It is a String on the .db, for some reason...
    acquire_period = ADComponent(
        EpicsSignalWithCustomReadoutRBV,
        "acquire_period",
        tolerance=1e-5,
        enforce_type=float,
    )  # NOTE: It is a String on the .db, for some reason...

    enable_num_images = ADComponent(EpicsSignal, "EnableNumImages")
    read_matrix = ADComponent(
        EpicsSignalWithCustomReadoutRBV, "read_matrix", string=True
    )
    """Force the Backend to make an image, usually to get around a first-off spurious image."""

    equalization = ADComponent(EpicsSignal, "equalization_RBV", write_pv="Equalization")
    trigger_mode = ADComponent(EpicsSignalNoValidation, "TriggerMode")
    set_dynamic_range = ADComponent(EpicsSignalWithRBV, "SetDynamicRange")

    def stage(self):
        super(MobipixBackend, self).stage()

        # Get first, spurious, image out
        self.read_matrix.set("", expected_readout="Done").wait()


class MobipixDetector(DetectorBase):
    cam = ADComponent(MobipixCam, "cam:")
    backend = ADComponent(MobipixBackend, "Backend:")

    acquire = ADComponent(EpicsSignal, "cam:Acquire_RBV", write_pv="acquire")
    num_exposures = ADComponent(EpicsSignal, "num_exposures")


class Mobipix(SingleTrigger, MobipixDetector):
    class MobipixROIStatPlugin(ROIStatPlugin):
        stat_1 = ADComponent(ROIStatNPlugin, "1:")

    hdf5 = ADComponent(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template="/tmp",
        read_attrs=[],
    )
    plugin_transform = ADComponent(TransformPlugin, "Trans1:")
    plugin_roi_1 = ADComponent(ROIPlugin, "ROI1:")
    plugin_roi_stat_1 = ADComponent(MobipixROIStatPlugin, "ROIStat1:")

    num_images = ADComponent(Signal, name="num_images", value=1, kind=Kind.config)
    acquire_time = ADComponent(Signal, name="acquire_time", value=0.1, kind=Kind.config)

    def __init__(
        self, name, prefix, *, save_hdf_file=True, enable_num_images=False, **kwargs
    ):
        """
        This is a Mobipix device using an AreaDetector-based IOC.

        Parameters
        ----------
        name : str
            The human-readable device's name. It will be used by visualization tools and similar.
        prefix : str
            The PV prefix for the detector. It needs a trailing separator, usually ':'.
        save_hdf_file : bool, optional
            Whether to setup the NDFileHDF5 plugin to save images from the detector. Defaults to True.
        enable_num_images : bool, optional
            Whether to enable the NumImages field or not. Defaults to False.

            Note that enabling this option is mostly a performance optimization, and shouldn't be
            very useful at low framerates. Due to some issues with the IOC, keeping it disabled is the safest option.

        Attributes
        ----------
        acquisition_time : Signal
            Time taken to acquire a single image (disconsidering control overheads).
        num_images : Signal
            Total number of images to take.
        num_exposures : int
            Number of images to take for each trigger signal.
        hdf_file_name : str, optional
            Name of the HDF5 to save. It will be formatted into 'hdf_file_template'. Defaults to the UUID of the run.
        hdf_file_path : str, optional
            Path to save the HDF5 file to. Defaults to '/tmp'.
        hdf_file_template : str, optional
            Value of the FileTemplate PV in the HDF5 plugin. Defaults to '%s%s_%3.3d.h5'.
        """

        super(Mobipix, self).__init__(prefix, name=name, **kwargs)

        self.__logger = logging.getLogger(str(self.__class__))
        self.__enable_num_images = enable_num_images

        self._acquisition_signal = self.acquire

        self.cam.stage_sigs["array_callbacks"] = 1
        self.cam.stage_sigs["trigger_mode"] = 0
        self.backend.stage_sigs["enable_num_images"] = enable_num_images

        if save_hdf_file:
            self.hdf5.enable_on_stage()
            self.hdf5.stage_sigs["auto_save"] = 1
        else:
            self.hdf5.disable_on_stage()
            self.hdf5.stage_sigs["capture"] = 0

        self.plugin_roi_stat_1.stat_1.net.kind = Kind.hinted
        self.read_attrs = ["plugin_roi_stat_1.stat_1.net"]

    def stage(self):
        super(Mobipix, self).stage()

        # NOTE: num_images is ignored when enable_num_images is not set
        _num_images = self.num_images.get()
        if self.__enable_num_images:
            if _num_images <= 0:
                raise MobipixMissingConfigurationError(
                    "You must set the number of images to a positive integer."
                )

            self.cam.num_images.set(_num_images).wait()
        self.hdf5.num_capture.set(_num_images).wait()

        _acquire_time = self.acquire_time.get()
        if _acquire_time <= 0:
            raise MobipixMissingConfigurationError(
                "You must set the acquisition time to a positive number."
            )

        self.backend.acquire_time.set(_acquire_time).wait()
        self.backend.acquire_period.set(0).wait()

        if "/tmp" in self.hdf5.file_path.get():
            self.__logger.warning("The HDF5 file path is set to '/tmp'.")

    def trigger(self):
        # NOTE: 2.0 is an arbitrary value that should cover every scenario.
        timeout_time = self.acquire_time.get() + 2.0

        trigger_status = super().trigger()
        try:
            trigger_status.wait(timeout_time)
        except WaitTimeoutError:
            # Fallback for when Acquire_RBV gets stuck after making an image.
            # In this case, we manually tell the IOC to stop acquiring, which
            # corrects the RBV value, and proceed as normal.
            self.__logger.debug(
                "Trigger has stuck the RBV value. Manually correcting it."
            )

            # When num_images is enabled, putting 0 in the acquire signal will close the
            # service <-> IOC connection, reverting the performance optimization from that mode.
            if not self.__enable_num_images:
                self._acquisition_signal.set(0).wait()

            new_status = self._status_type(self)
            new_status.set_finished()
            return new_status
        return trigger_status

    @property
    def hdf_file_name(self):
        return self.hdf5.stage_sigs.get("file_name", None)

    @hdf_file_name.setter
    def hdf_file_name(self, value: Optional[str]):
        if value is not None:
            self.hdf5.stage_sigs["file_name"] = value

    @property
    def hdf_file_path(self):
        return self.hdf5.stage_sigs.get("file_path", None)

    @hdf_file_path.setter
    def hdf_file_path(self, value: Optional[str]):
        if value is not None:
            self.hdf5.stage_sigs["file_path"] = value

    @property
    def hdf_file_template(self):
        return self.hdf5.stage_sigs.get("file_template", None)

    @hdf_file_template.setter
    def hdf_file_template(self, value: Optional[str]):
        if value is not None:
            self.hdf5.stage_sigs["file_template"] = value


class MobipixEnergyThresholdSetter(Device):
    img_chip_number_id = ADComponent(
        EpicsSignalWithRBV, "ImgChipNumberID", kind=Kind.config
    )
    dac_threshold_energy_0 = ADComponent(
        EpicsSignalWithCustomReadoutRBV,
        "DAC_ThresholdEnergy0",
        enforce_type=int,
        kind=Kind.config,
    )
    dac_threshold_energy_1 = ADComponent(
        EpicsSignalWithCustomReadoutRBV,
        "DAC_ThresholdEnergy1",
        enforce_type=int,
        kind=Kind.config,
    )

    nrg = ADComponent(InternalSignal, kind=Kind.hinted)

    def __init__(self, mobipix: Mobipix):
        super(MobipixEnergyThresholdSetter, self).__init__(
            prefix=mobipix.backend.prefix,
            name="{} -- Energy Threshold Setter".format(mobipix.name),
        )

        self.__low_threshold_adjust = []
        self.__low_threshold_adjust.append(lambda nrg: 9.63 * nrg + 5.64)
        self.__low_threshold_adjust.append(lambda nrg: 9.62 * nrg + 5.68)
        self.__low_threshold_adjust.append(lambda nrg: 8.88 * nrg + 6.28)
        self.__low_threshold_adjust.append(lambda nrg: 9.22 * nrg + 6.43)

        self.__high_threshold_adjust = []
        # no defaults

        self.read_attrs = ["nrg"]

    def set(self, nrg, timeout=None):
        original_chip = self.img_chip_number_id.get()

        for i in range(4):
            self.img_chip_number_id.set(i).wait(timeout=timeout)

            if len(self.low_threshold_adjust) > i:
                self.dac_threshold_energy_0.set(
                    int(self.low_threshold_adjust[i](nrg))
                ).wait(timeout=timeout)
            if len(self.high_threshold_adjust) > i:
                self.dac_threshold_energy_1.set(
                    int(self.high_threshold_adjust[i](nrg))
                ).wait(timeout=timeout)

        self.nrg.set(nrg, internal=True).wait()
        return self.img_chip_number_id.set(original_chip)

    @property
    def low_threshold_adjust(self):
        return self.__low_threshold_adjust

    @low_threshold_adjust.setter
    def low_threshold_adjust(self, adjust_functions: list):
        assert (
            len(adjust_functions) == 4
        ), "The adjust functions must have 4 elements (one for each chip)"
        assert all(
            isinstance(i, callable) for i in adjust_functions
        ), "The adjust functions must be callable"

        self.__low_threshold_adjust = adjust_functions

    @property
    def high_threshold_adjust(self):
        return self.__high_threshold_adjust

    @high_threshold_adjust.setter
    def high_threshold_adjust(self, adjust_functions: list):
        assert (
            len(adjust_functions) == 4
        ), "The adjust functions must have 4 elements (one for each chip)"
        assert all(
            isinstance(i, callable) for i in adjust_functions
        ), "The adjust functions must be callable"

        self.__high_threshold_adjust = adjust_functions
