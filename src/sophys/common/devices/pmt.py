from ophyd import Device, Component, EpicsSignalRO
from sophys.common.utils import EpicsSignalWithGetSet


class Photomultiplier(Device):
    """
    Photomultiplier device developed by the group GIE.
    """

    voltage = Component(EpicsSignalWithGetSet, "", ssuffix="VoltageDAC")
    current = Component(EpicsSignalWithGetSet, "", ssuffix="CurrentDAC")
    voltage_ramp = Component(EpicsSignalWithGetSet, "", ssuffix="VoltageRampDAC")
    status = Component(EpicsSignalRO, "Status")
    stop_pmt = Component(EpicsSignalRO, "Stop")
