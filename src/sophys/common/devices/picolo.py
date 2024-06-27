from ophyd import Device, Component, EpicsSignal, EpicsSignalWithRBV, \
    DynamicDeviceComponent, EpicsSignalRO


class PicoloChannel(Device):

    enable = Component(EpicsSignal, "Enable")
    value = Component(EpicsSignal, "EngValue", kind="hinted")
    saturated = Component(EpicsSignal, "Saturated")
    range = Component(EpicsSignalWithRBV, "Range")
    auto_range = Component(EpicsSignal, "AutoRange")
    acquire_mode = Component(EpicsSignalWithRBV, "AcquireMode")
    state = Component(EpicsSignalRO, "State")


class Picolo(Device):

    range = Component(EpicsSignal, "Range")
    auto_range = Component(EpicsSignal, "AutoRange")
    acquisition_time = Component(EpicsSignalWithRBV, "AcquisitionTime")
    sample_rate = Component(EpicsSignalWithRBV, "SampleRate")
    acquire_mode = Component(EpicsSignal, "AcquireMode")
    continuous_mode = DynamicDeviceComponent({
        "ch1": (PicoloChannel, "Current1:", {}),
        "ch2": (PicoloChannel, "Current2:", {}),
        "ch3": (PicoloChannel, "Current3:", {}),
        "ch4": (PicoloChannel, "Current4:", {})
    })