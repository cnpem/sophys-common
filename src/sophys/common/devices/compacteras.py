import logging
import typing

from os import environ

from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO, Kind
from ophyd.signal import ConnectionTimeoutError


class Scale(Device):
    analog_bw = Cpt(EpicsSignal, "AnalogBW", kind=Kind.config)
    calibration_offset = Cpt(EpicsSignal, "CalibrationOffset", kind=Kind.config)
    gain_correction = Cpt(EpicsSignal, "GainCorrection", kind=Kind.config)


class Channel(Device):
    """A CompactERAS channel. It is directly tied to a corresponding ERAS channel."""

    measurement_type = Cpt(EpicsSignal, "MeasurementType", kind=Kind.config)
    voltage = Cpt(EpicsSignalRO, "Voltage", kind=Kind.hinted)
    current = Cpt(EpicsSignalRO, "Current", kind=Kind.hinted)

    current_full_scale_label = Cpt(EpicsSignalRO, "GetCurrentFSLbl", kind=Kind.config)
    current_sensitivity_label = Cpt(EpicsSignalRO, "GetCurrentSTLbl", kind=Kind.config)

    serial_number = Cpt(EpicsSignal, "SN", kind=Kind.omitted)
    voltage_full_scale = Cpt(EpicsSignal, "VoltFS", kind=Kind.omitted)
    user_voltage_offset = Cpt(EpicsSignal, "UserVoltageOffset", kind=Kind.omitted)
    user_current_offset = Cpt(EpicsSignal, "UserCurrentOffset", kind=Kind.omitted)
    voltage_scale_factor = Cpt(EpicsSignal, "VoltageSF", kind=Kind.omitted)

    associated_voltage_channel = Cpt(
        EpicsSignalRO, "AssociatedVoltageChannel", kind=Kind.omitted
    )

    SC0 = Cpt(Scale, "SC0:", lazy=True, kind=Kind.omitted)
    SC1 = Cpt(Scale, "SC1:", lazy=True, kind=Kind.omitted)
    SC2 = Cpt(Scale, "SC2:", lazy=True, kind=Kind.omitted)
    SC3 = Cpt(Scale, "SC3:", lazy=True, kind=Kind.omitted)
    SC4 = Cpt(Scale, "SC4:", lazy=True, kind=Kind.omitted)
    SC5 = Cpt(Scale, "SC5:", lazy=True, kind=Kind.omitted)
    SC6 = Cpt(Scale, "SC6:", lazy=True, kind=Kind.omitted)
    SC7 = Cpt(Scale, "SC7:", lazy=True, kind=Kind.omitted)

    def getScale(self, scale: int):
        return getattr(self, f"SC{scale}")


class CompactERAS(Device):
    """
    A CompactERAS Soft IOC Ophyd device.

    The channels can be accessed via the `CH{0..4}` attributes.
    """

    version = Cpt(EpicsSignalRO, "Version", string=True)

    sampling_rate = Cpt(EpicsSignalRO, "SamplingRate")
    acquisition_bandwidth = Cpt(EpicsSignalRO, "AcquisitionBandwidth")

    supported_devices = Cpt(EpicsSignalRO, "DevicesUsed", string=True)
    permanent_device_prefix = Cpt(EpicsSignalRO, "VoltageReaderPrefix", string=True)
    permanent_device_card = Cpt(EpicsSignalRO, "VoltageCard", string=True)
    variable_device_prefix = Cpt(EpicsSignalRO, "ScaleSwitcherPrefix", string=True)

    CH1 = Cpt(Channel, "CH1:", lazy=True)
    CH2 = Cpt(Channel, "CH2:", lazy=True)
    CH3 = Cpt(Channel, "CH3:", lazy=True)
    CH4 = Cpt(Channel, "CH4:", lazy=True)

    def verifyVersion(
        self,
        minimum_version: str,
        maximum_version: typing.Optional[str] = None,
        logger: typing.Optional[logging.Logger] = None,
    ) -> bool:
        """
        Verifies that the soft IOC is running / in the correct version.

        Parameters
        ----------
        minimum_version : str
            The minimum version to consider as a good version,
            in the simple semantic versioning schema (major.minor.patch).
        maximum_version : str, optional
            The maximum version to consider as a good version,
            in the simple semantic versioning schema (major.minor.patch).

            If `None` (default), the maximum version will be the next major version,
            relative to `minimum_version`.
        logger : logging.Logger, optional
            A custom logger to use for the error messages. Defaults to the root logger.

        Returns
        -------
        bool
            True if the IOC is connected (regardless of the version), False otherwise.
        """
        if logger is None:
            logger = logging.getLogger()

        try:
            soft_ioc_version = self.version.get()
        except ConnectionTimeoutError:
            logger.error(
                "Could not connect to the SoftIOC (Version PV: {}). Is it running?".format(
                    self.version.pvname
                )
            )
            logger.debug(
                "EPICS_CA_ADDR_LIST: {}".format(
                    environ.get("EPICS_CA_ADDR_LIST", "Not set")
                )
            )
            return False

        min_major_version, min_minor_version, *_ = map(int, minimum_version.split("."))
        if maximum_version is None:
            maximum_version = f"{min_major_version + 1}.0.0"
        max_major_version, max_minor_version, *_ = map(int, maximum_version.split("."))

        major_version, minor_version, *_ = map(int, soft_ioc_version.split("."))

        lower = major_version < min_major_version or (
            major_version == min_major_version and minor_version < min_minor_version
        )
        higher = major_version > max_major_version or (
            major_version == max_major_version and minor_version > max_minor_version
        )

        if lower or higher:
            logger.warning(
                "SoftIOC has an incompatible major version, so things might be broken! (Expected: {}.{} - {}.{}, Got: {})".format(
                    min_major_version,
                    min_minor_version,
                    max_major_version,
                    max_minor_version,
                    soft_ioc_version,
                )
            )

        return True

    def getSupportedDevices(self):
        """Gets from the Soft IOC the list of supported devices of it."""
        return self.supported_devices.get().split(" ")
