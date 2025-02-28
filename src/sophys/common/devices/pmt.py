from ophyd import Device, Component, EpicsSignal, EpicsSignalRO


class Photomultiplier(Device):

    voltage = Component(EpicsSignal, "getVoltageDAC", write_pv="setVoltageDAC")
    current = Component(EpicsSignal, "getCurrentDAC", write_pv="setCurrentDAC")
    voltage_ramp = Component(
        EpicsSignal, "getVoltageRampDAC", write_pv="setVoltageRampDAC"
    )
    status = Component(EpicsSignalRO, "Status")
    stop = Component(EpicsSignalRO, "Stop")
