from typing import List
from sophys.common.utils import EpicsSignalMon, EpicsSignalWithRBSP, EpicsSignalCmd
from ophyd import PVPositionerIsClose, EpicsSignal, Component


class HVPS(PVPositionerIsClose):
    """
    A High-Voltage Power Supply (HVPS) device, since the HVPS has no done PV,
    the implementation uses a PositionerIsClose with a configurable absolute
    tolerance (default is 2V). The absolute tolerance does not work well for
    low voltages (e.g. < 50V), but this is not a common use case for HVPS.
    """

    setpoint = Component(EpicsSignalWithRBSP, "VoltageSetpoint", kind="config")
    readback = Component(EpicsSignalMon, "Voltage", kind="hinted")
    actuate = Component(EpicsSignalCmd, "VoltageSetpoint", kind="omitted")

    current_limit = Component(EpicsSignalWithRBSP, "CurrentLimit", kind="config")
    current_trip = Component(EpicsSignalWithRBSP, "CurrentTrip", kind="config")

    operation_status = Component(EpicsSignalMon, "OperationStatus", kind="config")

    enable = Component(EpicsSignalCmd, "OutputEnable", kind="config")
    disable = Component(EpicsSignalCmd, "OutputDisable", kind="config")

    atol = 2  # Set 2V as the absolute tolerance
    actuate_value = 2
    limits = (0, 3000)
    egu = "V"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs["enable"] = 1
        self.done.kind = "omitted"
