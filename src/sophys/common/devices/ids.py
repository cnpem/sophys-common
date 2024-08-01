
from enum import IntEnum

from ophyd import (
    Device,
    Component,
    EpicsSignal,
    EpicsSignalRO,
    PVPositionerIsClose,
    Kind,
)

class EpicsSignalMon(EpicsSignalRO):
    
    def __init__(self, prefix, **kwargs):
        super().__init__(prefix=prefix+"-Mon", **kwargs)

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


# Reference:
# https://cnpemcamp.sharepoint.com/:x:/s/Comissionamento/Eabdu5JQhm1Oh8xjo25QNkEBeA8lLoRFrrTI0nVYT6t9aw?e=JnWNx9
class UndulatorKymaAPU(Device):
    """Ophyd device for the Kyma APU Undulator."""

    # Control registers and flags
    class Command(IntEnum):
        No = 0
        Stop = 1
        Reset = 2
        Start = 3
        CalibTilt = 4
        Standby = 5
        Home = 10

    class StateHW(IntEnum):
        Off = 0x00
        HWInit = 0x01
        ConfigError = 0x02
        Init = 0x03
        Alarm = 0x04
        Warning = 0x08
        BusyPositiveAlarm = 0x14
        BusyPositiveWarning = 0x18
        BusyPositive = 0x1C
        BusyNegativeAlarm = 0x28
        BusyNegativeWarning = 0x24
        BusyNegative = 0x2C
        ReadyAlarm = 0x34
        ReadyWarning = 0x38
        Ready = 0x3C
        OpAlarm = 0x44
        OpWarning = 0x48
        Op = 0x4C

    class State(IntEnum):
        Na = 0
        Op = 1
        Start = 2
        Jog = 3
        Standby = 4
        CalibTilt = 5
        Backup = 6
        Restore = 7
        BackupEncoders = 8
        RestoreEncoders = 9
        ForceNewPosition = 10
        Home = 11
        Error = 12
        Reset = 13
        Stop = 14
        ErrorStop = 15
        PowerOff = 16
        Init = 17
        ConfigError = 18

    command = Component(
        EpicsSignal,
        read_pv="LastDevCtrlCmd-Mon",
        write_pv="DevCtrl-Cmd",
        lazy=True,
        kind=Kind.omitted,
    )
    state_hw = Component(EpicsSignalRO, "StateHw-Mon", lazy=True, kind=Kind.omitted)
    state = Component(EpicsSignalRO, "State-Mon", lazy=True, kind=Kind.omitted)

    is_operational = Component(
        EpicsSignalRO, "IsOperational-Mon", lazy=True, kind=Kind.omitted
    )
    is_motors_on = Component(
        EpicsSignalRO, "MotorsEnbld-Mon", lazy=True, kind=Kind.omitted
    )
    is_alarm_set = Component(EpicsSignalRO, "Alarm-Mon", lazy=True, kind=Kind.omitted)
    is_moving_set = Component(EpicsSignalRO, "Moving-Mon", lazy=True, kind=Kind.omitted)

    is_remote = Component(EpicsSignalRO, "IsRemote-Mon", lazy=True, kind=Kind.omitted)
    interface = Component(EpicsSignalRO, "Interface-Mon", lazy=True, kind=Kind.omitted)

    home_axis = Component(
        EpicsSignal, write_pv="HomeAxis-Sel", lazy=True, kind=Kind.omitted
    )

    # Motion
    class _Phase(PVPositionerIsClose):
        setpoint = Component(EpicsSignal, "Phase-SP")
        readback = Component(EpicsSignalRO, "Phase-Mon")

    phase = Component(
        _Phase,
        "",
        lazy=True,
        kind=Kind.hinted,
    )

    phase_speed = Component(
        EpicsSignal,
        read_pv="PhaseSpeed-Mon",
        write_pv="PhaseSpeed-SP",
        lazy=True,
        kind=Kind.config,
    )
    phase_max_speed = Component(
        EpicsSignalRO,
        "MaxPhaseSpeed-RB",
        lazy=True,
        kind=Kind.config,
    )

    # Status
    class PhaseAlarm(IntEnum):
        DriveError = 0
        PowerOff = 1
        Lag = 2
        Overload = 3
        InputInvalid = 4
        EncodeError = 5
        Disabled = 6
        NotHomed = 7
        KillSwitchLow = 8

    class PhaseAlarmState(IntEnum):
        Off = 0x00
        HWInit = 0x01
        ConfigError = 0x02
        Init = 0x03
        Alarm = 0x04
        Warning = 0x08
        BusyPositiveAlarm = 0x14
        BusyPositiveWarning = 0x18
        BusyPositive = 0x1C
        BusyNegativeAlarm = 0x28
        BusyNegativeWarning = 0x24
        BusyNegative = 0x2C
        ReadyAlarm = 0x34
        ReadyWarning = 0x38
        Ready = 0x3C
        OpAlarm = 0x44
        OpWarning = 0x48
        Op = 0x4C

    phase_alarm = Component(
        EpicsSignalRO, "AlrmPhase-Mon", lazy=True, kind=Kind.omitted
    )
    # Reference:
    # https://infosys.beckhoff.com/english.php?content=../content/1033/tcncerrcode2/index.html
    phase_alarm_errid = Component(
        EpicsSignalRO, "AlrmPhaseErrID-Mon", lazy=True, kind=Kind.omitted
    )
    phase_alarm_sdw = Component(
        EpicsSignalRO, "AlrmPhaseSttDW-Mon", lazy=True, kind=Kind.omitted
    )
    phase_alarm_state = Component(
        EpicsSignalRO, "AlrmPhaseStt-Mon", lazy=True, kind=Kind.omitted
    )
    rack_alarm_estop = Component(
        EpicsSignalRO, "AlrmRackEStop-Mon", lazy=True, kind=Kind.omitted
    )
    rack_alarm_kill = Component(
        EpicsSignalRO, "AlrmRackKill-Mon", lazy=True, kind=Kind.omitted
    )
    rack_alarm_kill_disabled = Component(
        EpicsSignalRO, "AlrmRackKillDsbld-Mon", lazy=True, kind=Kind.omitted
    )
    rack_alarm_power_disabled = Component(
        EpicsSignalRO, "AlrmRackPwrDsbld-Mon", lazy=True, kind=Kind.omitted
    )

    # Interlock
    interlock_in_stop = Component(
        EpicsSignalRO, "IntlkInStop-Mon", lazy=True, kind=Kind.omitted
    )
    interlock_in_open_gap = Component(
        EpicsSignalRO, "IntlkInEOpnGap-Mon", lazy=True, kind=Kind.omitted
    )
    interlock_out_gap_opened = Component(
        EpicsSignalRO, "IntlkOutGapStt-Mon", lazy=True, kind=Kind.omitted
    )
    interlock_out_status_ok = Component(
        EpicsSignalRO, "IntlkOutStsOk-Mon", lazy=True, kind=Kind.omitted
    )
    interlock_out_ccps_enabled = Component(
        EpicsSignalRO, "IntlkOutCCPSEnbld-Mon", lazy=True, kind=Kind.omitted
    )
    interlock_out_power_enabled = Component(
        EpicsSignalRO, "IntlkOutPwrEnbld-Mon", lazy=True, kind=Kind.omitted
    )

    # Beamline control
    beamline_control_status = Component(
        EpicsSignalRO, "BeamLineCtrlEnbl-Sts", lazy=True, kind=Kind.omitted
    )