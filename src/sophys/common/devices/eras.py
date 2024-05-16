from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, EpicsSignalNoValidation


class ERAS(Device):
    name = Component(EpicsSignal, "GetDev", write_pv="SetDev")
    location = Component(EpicsSignal, "GetLoc", write_pv="SetLoc")
    version = Component(EpicsSignalRO, "GetVer")

    reset = Component(EpicsSignalNoValidation, "Reset")
