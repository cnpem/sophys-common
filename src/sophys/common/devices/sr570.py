from enum import Enum  # numpydoc ignore=GL08

from ophyd import Component, Device, EpicsSignal

SR570_SCALES = [
    "1pA/V",
    "2pA/V",
    "5pA/V",
    "10pA/V",
    "20pA/V",
    "50pA/V",
    "100pA/V",
    "200pA/V",
    "500pA/V",
    "1nA/V",
    "2nA/V",
    "5nA/V",
    "10nA/V",
    "20nA/V",
    "50nA/V",
    "100nA/V",
    "200nA/V",
    "500nA/V",
    "1uA/V",
    "2uA/V",
    "5uA/V",
    "10uA/V",
    "20uA/V",
    "50uA/V",
    "100uA/V",
    "200uA/V",
    "500uA/V",
]


class GainUnits(int, Enum):
    """Gain units for the SR570 pre-amplifier."""

    PA_V = 0
    NA_V = 1
    UA_V = 2
    MA_V = 3


class GainModes(str, Enum):
    """Gain modes for the SR570 pre-amplifier."""

    HIGH_BW = "HIGH BW"
    LOW_NOISE = "LOW NOISE"
    LOW_DRIFT = "LOW DRIFT"


class SR570(Device):
    """Stanford SR570 pre-amplifier ophyd device."""

    sensitivity_value = Component(EpicsSignal, "sens_num", kind="normal", string=True)
    sensitivity_unit = Component(EpicsSignal, "sens_unit", kind="normal", string=True)

    offset_on = Component(EpicsSignal, "offset_on", kind="normal", string=True)
    offset_sign = Component(EpicsSignal, "offset_sign", kind="normal", string=True)
    offset_value = Component(EpicsSignal, "offset_num", kind="normal", string=True)
    offset_unit = Component(EpicsSignal, "offset_unit", kind="normal", string=True)
    offset_fine = Component(EpicsSignal, "off_u_put", kind="normal", string=True)
    offset_cal = Component(EpicsSignal, "offset_cal", kind="normal", string=True)

    set_all = Component(EpicsSignal, "init.PROC", kind="normal")

    bias_value = Component(EpicsSignal, "bias_put", kind="normal", string=True)
    bias_on = Component(EpicsSignal, "bias_on", kind="normal", string=True)

    filter_type = Component(EpicsSignal, "filter_type", kind="normal", string=True)
    filter_lowpass = Component(EpicsSignal, "low_freq", kind="normal", string=True)
    filter_highpass = Component(EpicsSignal, "high_freq", kind="normal", string=True)

    gain_mode = Component(EpicsSignal, "gain_mode", kind="normal", string=True)
    invert = Component(EpicsSignal, "invert_on", kind="normal", string=True)
    blank = Component(EpicsSignal, "blank_on", kind="normal", string=True)
