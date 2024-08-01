from ophyd import EpicsSignal, EpicsSignalRO, Component, Device
from ophyd.pv_positioner import PVPositionerIsClose

class EpicsSignalIDs(PVPositionerIsClose):
    setpoint = Component(EpicsSignal, "-SP")
    readback = Component(EpicsSignalRO, "-Mon")

class Apu22(Device):
    kx = Component(EpicsSignalIDs, "Kx")
    phase = Component(EpicsSignalIDs, "Phase")
    phase_speed = Component(EpicsSignalIDs, "PhaseSpeed")
    control = Component(EpicsSignalRO, "DevCtrl-Cmd", string=True)
    moving = Component(EpicsSignalRO, "Moving-Mon")
    enabled = Component(EpicsSignalRO, "MotorsEnbld-Mon")