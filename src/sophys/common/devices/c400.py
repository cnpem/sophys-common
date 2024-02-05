import logging

from ophyd import (
    Component,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    Kind,
    SingleTrigger,
)
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.plugins import ImagePlugin

from ..utils import HDF5PluginWithFileStore


class C400Cam(CamBase):
    burst_size = Component(
        EpicsSignalWithRBV, "BURST_SIZE", lazy=True, kind=Kind.config
    )
    dead_time = Component(EpicsSignalWithRBV, "DEAD_TIME", lazy=True, kind=Kind.config)
    encoder = Component(EpicsSignalRO, "ENCODER_RBV", lazy=True, kind=Kind.config)
    system_ipmode = Component(
        EpicsSignalWithRBV, "SYSTEM_IPMODE", lazy=True, kind=Kind.config
    )

    trigger_polarity = Component(
        EpicsSignalWithRBV, "TRIGGER_POLARITY", lazy=True, kind=Kind.config
    )
    trigger_start = Component(
        EpicsSignalWithRBV, "TRIGGER_START", lazy=True, kind=Kind.config
    )
    trigger_stop = Component(
        EpicsSignalWithRBV, "TRIGGER_STOP", lazy=True, kind=Kind.config
    )
    trigger_pause = Component(
        EpicsSignalWithRBV, "TRIGGER_PAUSE", lazy=True, kind=Kind.config
    )

    pulser_period = Component(
        EpicsSignalWithRBV, "PULSER_PERIOD", lazy=True, kind=Kind.config
    )
    pulser_width = Component(
        EpicsSignalWithRBV, "PULSER_WIDTH", lazy=True, kind=Kind.config
    )

    dac_ch1 = Component(EpicsSignalWithRBV, "DAC_ch1", lazy=True, kind=Kind.config)
    dac_ch2 = Component(EpicsSignalWithRBV, "DAC_ch2", lazy=True, kind=Kind.config)
    dac_ch3 = Component(EpicsSignalWithRBV, "DAC_ch3", lazy=True, kind=Kind.config)
    dac_ch4 = Component(EpicsSignalWithRBV, "DAC_ch4", lazy=True, kind=Kind.config)

    dhi_ch1 = Component(EpicsSignalWithRBV, "DHI_ch1", lazy=True, kind=Kind.config)
    dhi_ch2 = Component(EpicsSignalWithRBV, "DHI_ch2", lazy=True, kind=Kind.config)
    dhi_ch3 = Component(EpicsSignalWithRBV, "DHI_ch3", lazy=True, kind=Kind.config)
    dhi_ch4 = Component(EpicsSignalWithRBV, "DHI_ch4", lazy=True, kind=Kind.config)

    dlo_ch1 = Component(EpicsSignalWithRBV, "DLO_ch1", lazy=True, kind=Kind.config)
    dlo_ch2 = Component(EpicsSignalWithRBV, "DLO_ch2", lazy=True, kind=Kind.config)
    dlo_ch3 = Component(EpicsSignalWithRBV, "DLO_ch3", lazy=True, kind=Kind.config)
    dlo_ch4 = Component(EpicsSignalWithRBV, "DLO_ch4", lazy=True, kind=Kind.config)

    hivo_volts_ch1 = Component(
        EpicsSignalWithRBV, "HIVO_VOLTS_ch1", lazy=True, kind=Kind.config
    )
    hivo_volts_ch2 = Component(
        EpicsSignalWithRBV, "HIVO_VOLTS_ch2", lazy=True, kind=Kind.config
    )
    hivo_volts_ch3 = Component(
        EpicsSignalWithRBV, "HIVO_VOLTS_ch3", lazy=True, kind=Kind.config
    )
    hivo_volts_ch4 = Component(
        EpicsSignalWithRBV, "HIVO_VOLTS_ch4", lazy=True, kind=Kind.config
    )

    hivo_enable_ch1 = Component(
        EpicsSignalWithRBV, "HIVO_ENABLE_ch1", lazy=True, kind=Kind.config
    )
    hivo_enable_ch2 = Component(
        EpicsSignalWithRBV, "HIVO_ENABLE_ch2", lazy=True, kind=Kind.config
    )
    hivo_enable_ch3 = Component(
        EpicsSignalWithRBV, "HIVO_ENABLE_ch3", lazy=True, kind=Kind.config
    )
    hivo_enable_ch4 = Component(
        EpicsSignalWithRBV, "HIVO_ENABLE_ch4", lazy=True, kind=Kind.config
    )

    polarity_ch1 = Component(
        EpicsSignalWithRBV, "POLARITY_ch1", lazy=True, kind=Kind.config
    )
    polarity_ch2 = Component(
        EpicsSignalWithRBV, "POLARITY_ch2", lazy=True, kind=Kind.config
    )
    polarity_ch3 = Component(
        EpicsSignalWithRBV, "POLARITY_ch3", lazy=True, kind=Kind.config
    )
    polarity_ch4 = Component(
        EpicsSignalWithRBV, "POLARITY_ch4", lazy=True, kind=Kind.config
    )


class C400Detector(DetectorBase):
    cam = Component(C400Cam, "cam1:")


class C400(SingleTrigger, C400Detector):
    """This is a C400 (Four-channel Pulse Counting Detector Controller) device using an AreaDetector-based IOC."""

    image = Component(ImagePlugin, "image1:")
    hdf5 = Component(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template="/tmp",
        read_attrs=[],
    )

    def __init__(self, *args, name, write_path=None, **kwargs):
        super(C400, self).__init__(*args, name=name, **kwargs)
        self.hdf5.write_path_template = write_path

    def stage(self):
        self.hdf5.warmup()

        super().stage()


class C400ROIs(Device):
    roi1_rbv = Component(EpicsSignalRO, "ROIStat1:1:Net_RBV")
    roi2_rbv = Component(EpicsSignalRO, "ROIStat1:2:Net_RBV")
    roi3_rbv = Component(EpicsSignalRO, "ROIStat1:3:Net_RBV")
    roi4_rbv = Component(EpicsSignalRO, "ROIStat1:4:Net_RBV")

    hints = {"fields": []}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hints["fields"] = [self.name + "_roi1_rbv"]


class OldC400:
    exposure_time = Component(EpicsSignal, ":PERIOD", kind="config")
    reading = Component(EpicsSignal, ":COUNT_ch1", kind="normal")
    acquire = Component(EpicsSignal, ":ACQUIRE", kind="omitted", put_complete=True)

    def stage(self):
        logging.warn(
            "This C400 device is deprecated! Please consider using the new AreaDetector-based version."
        )
        self.initial_enabled_state = 0
        self.acquire.set(1).wait()
        return super().stage()

    def unstage(self):
        ret = super().unstage()
        self.acquire.set(self.initial_enabled_state).wait()
        return ret
