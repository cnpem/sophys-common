from enum import IntEnum
from ophyd import (
    Device,
    Component,
    FormattedComponent,
    EpicsSignal,
    EpicsSignalRO,
    PVPositionerIsClose,
    Kind,
)
from ..utils.signals import EpicsSignalMon


class EpicsSignalIDs(PVPositionerIsClose):
    setpoint = Component(EpicsSignal, "-SP")
    readback = Component(EpicsSignalMon, "")


class PhaseEpicsSignal(PVPositionerIsClose):
    setpoint = Component(EpicsSignal, "Phase-SP")
    readback = Component(EpicsSignalMon, "Phase")
    actuate = Component(EpicsSignal, "DevCtrl-Cmd")
    actuate_value = 3


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
        "DevCtrl-Cmd",
        
        kind=Kind.omitted,
    )
    state_hw = Component(EpicsSignalMon, "StateHw",  kind=Kind.omitted)
    state = Component(EpicsSignalMon, "State",  kind=Kind.omitted)

    is_operational = Component(
        EpicsSignalMon, "IsOperational",  kind=Kind.omitted
    )
    is_motors_on = Component(
        EpicsSignalMon, "MotorsEnbld",  kind=Kind.omitted
    )
    is_alarm_set = Component(EpicsSignalMon, "Alarm",  kind=Kind.omitted)
    is_moving_set = Component(EpicsSignalMon, "Moving",  kind=Kind.omitted)

    is_remote = Component(EpicsSignalMon, "IsRemote",  kind=Kind.omitted)
    interface = Component(EpicsSignalMon, "Interface",  kind=Kind.omitted)

    home_axis = Component(EpicsSignal, "HomeAxis-Sel",  kind=Kind.omitted)

    phase = Component(PhaseEpicsSignal, "",  kind=Kind.hinted, atol=0.01)

    phase_speed = Component(
        EpicsSignalIDs,
        "PhaseSpeed",
        
        kind=Kind.config,
    )
    phase_max_speed = Component(
        EpicsSignalRO,
        "MaxPhaseSpeed-RB",
        
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

    phase_alarm = Component(EpicsSignalMon, "AlrmPhase",  kind=Kind.omitted)
    # Reference:
    # https://infosys.beckhoff.com/english.php?content=../content/1033/tcncerrcode2/index.html
    phase_alarm_errid = Component(
        EpicsSignalMon, "AlrmPhaseErrID",  kind=Kind.omitted
    )
    phase_alarm_sdw = Component(
        EpicsSignalMon, "AlrmPhaseSttDW",  kind=Kind.omitted
    )
    phase_alarm_state = Component(
        EpicsSignalMon, "AlrmPhaseStt",  kind=Kind.omitted
    )
    rack_alarm_estop = Component(
        EpicsSignalMon, "AlrmRackEStop",  kind=Kind.omitted
    )
    rack_alarm_kill = Component(
        EpicsSignalMon, "AlrmRackKill",  kind=Kind.omitted
    )
    rack_alarm_kill_disabled = Component(
        EpicsSignalMon, "AlrmRackKillDsbld",  kind=Kind.omitted
    )
    rack_alarm_power_disabled = Component(
        EpicsSignalMon, "AlrmRackPwrDsbld",  kind=Kind.omitted
    )

    # Interlock
    interlock_in_stop = Component(
        EpicsSignalMon, "IntlkInStop",  kind=Kind.omitted
    )
    interlock_in_open_gap = Component(
        EpicsSignalMon, "IntlkInEOpnGap",  kind=Kind.omitted
    )
    interlock_out_gap_opened = Component(
        EpicsSignalMon, "IntlkOutGapStt",  kind=Kind.omitted
    )
    interlock_out_status_ok = Component(
        EpicsSignalMon, "IntlkOutStsOk",  kind=Kind.omitted
    )
    interlock_out_ccps_enabled = Component(
        EpicsSignalMon, "IntlkOutCCPSEnbld",  kind=Kind.omitted
    )
    interlock_out_power_enabled = Component(
        EpicsSignalMon, "IntlkOutPwrEnbld",  kind=Kind.omitted
    )

    # Beamline control
    beamline_control_status = Component(
        EpicsSignalRO, "BeamLineCtrlEnbl-Sts",  kind=Kind.omitted
    )
