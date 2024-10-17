from typing import List
from sophys.common.utils import EpicsSignalMon
from ophyd import PVPositionerIsClose, EpicsSignal, Component, EpicsSignalRO


class EpicsSignalWithRBSP(EpicsSignal):
    """
    A simple Signal with a similar logic of EpicsSignalWithRBV, but
    pvname is -RB and write_pv is -SP.
    """

    def __init__(self, prefix, **kwargs):
        super().__init__(prefix + "-RB", write_pv=prefix + "-SP", **kwargs)


class HVPS(PVPositionerIsClose):
    """
    A High-Voltage Power Supply (HVPS) device, since the HVPS has no done PV,
    the implementation uses a PositionerIsClose with a configurable absolute
    tolerance (default is 2V).
    """

    setpoint = Component(EpicsSignalWithRBSP, "VoltageSetpoint", kind="config")
    readback = Component(EpicsSignalMon, "Voltage", kind="hinted")
    actuate = Component(EpicsSignal, "VoltageSetpoint-Cmd", kind="omitted")

    current_limit = Component(EpicsSignalWithRBSP, "CurrentLimit", kind="config")
    current_trip = Component(EpicsSignalWithRBSP, "CurrentTrip", kind="config")

    operation_status = Component(EpicsSignalMon, "OperationStatus", kind="config")

    enable = Component(EpicsSignal, "OutputEnable-Cmd", kind="config")
    disable = Component(EpicsSignal, "OutputDisable-Cmd", kind="config")

    # For low voltages this does not work well, but this is not the common use-case
    atol = 2  # Set 2V as the absolute tolerance
    actuate_value = 2
    limits = (0, 3000)
    egu = "V"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs["enable"] = 1
        self.done.kind = "omitted"
