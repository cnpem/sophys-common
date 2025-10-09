from time import time
from ophyd import (
    Device,
    Component,
    FormattedComponent,
    EpicsSignal,
    EpicsSignalWithRBV,
    DynamicDeviceComponent,
    EpicsSignalRO,
)
from ophyd.flyers import FlyerInterface
from ophyd.signal import DEFAULT_WRITE_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT
from ophyd.status import SubscriptionStatus, StatusBase, Status

from ..utils.status import PremadeStatus
from ..utils.interfaces import IEnumValidator


class EnumAcquisitionTimeValidator(IEnumValidator):
    """Validates acquisition time based on predefined enum values."""

    def __init__(self, enum_string):
        self._enums = [float(item.replace(" ms", "")) / 1000 for item in enum_string]

    def format_to_enum(self, value):
        ms_value = value * 1000  # Convert seconds to milliseconds

        if ms_value == int(ms_value):
            return f"{int(ms_value)} ms"
        else:
            return f"{ms_value} ms"

    def validate_and_format(self, acquisition_time: float):
        """Validate and format acquisition time."""
        if not self.is_valid(acquisition_time):
            raise ValueError(
                f"The acquisition time '{acquisition_time}' ms is not a valid option."
            )
        return self.format_to_enum(acquisition_time)

    def is_valid(self, enum_value: float) -> bool:
        return enum_value in self._enums


class PicoloAcquisitionTimeMixin:
    """A mix-in class for handling acquisition time configuration.

    This mix-in assumes the presence of a base interface that provides
    the methods `wait_for_connection` and `set`, which are expected to be
    inherited from another class. Upon initialization, it ensures a connection
    is established and validates acquisition time values using an
    enumeration-based validator before passing them to the base `set` method.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_for_connection(DEFAULT_CONNECTION_TIMEOUT)
        self._time_base_validator = EnumAcquisitionTimeValidator(self.enum_strs)

    def set(self, acquisition_time: float, *args, **kwargs):
        try:
            formatted_time = self._time_base_validator.validate_and_format(
                acquisition_time
            )
        except ValueError as e:
            return PremadeStatus(
                False,
                exception=e,
            )
        return super().set(formatted_time, *args, **kwargs)


class PicoloAcquisitionTime(PicoloAcquisitionTimeMixin, EpicsSignal):
    """PicoloAcquisitionTime using EpicsSignal."""

    pass


class PicoloAcquisitionTimeWithRBV(PicoloAcquisitionTimeMixin, EpicsSignalWithRBV):
    """PicoloAcquisitionTime using EpicsSignalWithRBV."""

    pass


class PicoloChannel(Device):
    """
    Device for one of the channels in the Picolo picoammeter.
    """

    data = Component(EpicsSignalRO, "Data", kind="hinted")
    scaled_data = Component(EpicsSignalRO, "ScaledData", kind="hinted")

    value = FormattedComponent(EpicsSignalRO, "{continuous_value}", kind="hinted")
    scaled_value = Component(EpicsSignalRO, "ScaledValue", kind="hinted")

    enable = Component(EpicsSignalWithRBV, "Enable", kind="config")
    engvalue = Component(EpicsSignal, "EngValue", kind="hinted")
    saturated = Component(EpicsSignal, "Saturated", kind="config")
    range = Component(EpicsSignalWithRBV, "Range", string=True, kind="config")
    auto_range = Component(EpicsSignalWithRBV, "AutoRange", kind="omitted")
    acquire_mode = Component(
        EpicsSignalWithRBV, "AcquireMode", string=True, kind="config"
    )
    state = Component(EpicsSignalRO, "State", string=True, kind="config")
    analog_bw = Component(EpicsSignalRO, "BW_RBV", kind="omitted")
    acquisition_time = Component(
        PicoloAcquisitionTimeWithRBV, "AcquisitionTime", string=True, kind="config"
    )
    sample_rate = Component(
        EpicsSignalWithRBV, "SampleRate", string=True, kind="config"
    )
    user_offset = Component(EpicsSignalWithRBV, "UserOffset", kind="config")
    exp_offset = Component(EpicsSignalWithRBV, "ExpOffset", kind="config")
    set_zero = Component(EpicsSignal, "SetZero", kind="omitted")

    def __init__(self, prefix, **kwargs):
        self.continuous_value = prefix[:-1]
        super().__init__(prefix=prefix, **kwargs)


class Picolo(Device):
    """Device for the 4 channel Picolo picoammeter."""

    class DataResetSignal(EpicsSignal):
        def set(self, value, *, timeout=DEFAULT_WRITE_TIMEOUT, settle_time=None):
            _s = Status()
            _s.set_finished()
            if value == 0:
                return _s

            parent = self.parent

            past_acquire_mode = parent.acquire_mode.get()

            parent.acquire_mode.set(0, timeout=timeout).wait()  # Set continuous mode
            super().set(value, timeout=timeout, settle_time=settle_time).wait()
            parent.acquire_mode.set(past_acquire_mode, timeout=timeout).wait()

            return _s

    range = Component(EpicsSignal, "Range", string=True, kind="config")
    auto_range = Component(EpicsSignal, "AutoRange", kind="omitted")
    acquire_mode = Component(EpicsSignal, "AcquireMode", string=True, kind="config")
    samples_per_trigger = Component(EpicsSignalWithRBV, "NumAcquire", kind="config")
    data_reset = Component(DataResetSignal, "DataReset", kind="omitted")
    data_acquired = Component(EpicsSignal, "DataAcquired", kind="config")
    triggering = Component(EpicsSignal, "Triggering", kind="omitted")
    enable = Component(EpicsSignal, "Enable", kind="omitted")
    common_sample_rate = Component(
        EpicsSignal, "SampleRate", string=True, kind="omitted"
    )

    acquisition_time = Component(
        PicoloAcquisitionTime, "AcquisitionTime", string=True, kind="omitted"
    )

    continuous_mode = DynamicDeviceComponent(
        {"start_acq": (EpicsSignal, "Start", {}), "stop_acq": (EpicsSignal, "Stop", {})}
    )

    ch1 = Component(PicoloChannel, "Current1:")
    ch2 = Component(PicoloChannel, "Current2:")
    ch3 = Component(PicoloChannel, "Current3:")
    ch4 = Component(PicoloChannel, "Current4:")


class PicoloFlyScan(Picolo, FlyerInterface):

    # 1 week timeout
    complete_timeout = 604800

    def kickoff(self):
        sts = StatusBase()
        sts.set_finished()
        return sts

    def _fly_scan_complete(self, **kwargs):
        """
        Wait for the Picolo device to acquire and save the predetermined quantity
        of values.
        """
        num_exposures = self.samples_per_trigger.get()
        data_acquired = self.data_acquired.get()
        if data_acquired != num_exposures:
            return False

        for channel in [self.ch1, self.ch2, self.ch3, self.ch4]:
            num_points_saved = len(channel.data.get())
            if channel.enable.get() and num_exposures != num_points_saved:
                return False
        return True

    def complete(self):
        return SubscriptionStatus(
            self, callback=self._fly_scan_complete, timeout=self.complete_timeout
        )

    def describe_collect(self):
        descriptor = {"picolo": {}}
        for channel in [self.ch1, self.ch2, self.ch3, self.ch4]:
            if channel.enable.get():
                descriptor["picolo"].update(channel.data.describe())
        return descriptor

    def collect(self):
        data = {}
        timestamps = {}
        for channel in [self.ch1, self.ch2, self.ch3, self.ch4]:
            if channel.enable.get():
                device_data = channel.data
                dev_name = device_data.name
                dev_info = device_data.read()[dev_name]
                data.update({dev_name: dev_info["value"]})
                timestamps.update({dev_name: dev_info["timestamp"]})

        return [{"time": time(), "data": data, "timestamps": timestamps}]
