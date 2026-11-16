from ophyd import (
    Device,
    EpicsSignal,
    EpicsSignalRO,
    FormattedComponent,
)


class Lakeshore336_LoopControl(Device):
    """Loop control and general parameter configuration on the Lakeshore336"""

    temp = FormattedComponent(EpicsSignalRO, "{prefix}TEMP{loop_number}")

    temp_sp = FormattedComponent(EpicsSignal, "{prefix}TEMP{loop_number}:SP")
    temp_sp_rbv = FormattedComponent(EpicsSignalRO, "{prefix}TEMP{loop_number}:SP:RBV")

    heater = FormattedComponent(
        EpicsSignalRO,
        "{prefix}HEATER{loop_number}:OUTPUT",
        auto_monitor=True,
        kind="normal"
    )
    heater_range_sp = FormattedComponent(
        EpicsSignal,
        "{prefix}HEATER{loop_number}:RANGE:SP",
        auto_monitor=True,
        string=True,
    )
    heater_range_rbv = FormattedComponent(
        EpicsSignalRO,
        "{prefix}HEATER{loop_number}:RANGE:SP:RBV",
        auto_monitor=True,
        string=True,
        )

    #Lakeshore configuration
    pid_P_sp = FormattedComponent(
        EpicsSignal, "{prefix}P{loop_number}:SP", kind="config"
    )
    pid_P_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}P{loop_number}:SP:RBV", kind="config"
    )

    pid_I_sp = FormattedComponent(
        EpicsSignal, "{prefix}I{loop_number}:SP", kind="config"
    )
    pid_I_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}I{loop_number}:SP:RBV", kind="config"
    )

    pid_D_sp = FormattedComponent(
        EpicsSignal, "{prefix}D{loop_number}:SP", kind="config"
    )
    pid_D_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}D{loop_number}:SP:RBV", kind="config"
    )

    ramp_rate_sp = FormattedComponent(
        EpicsSignal, "{prefix}RAMP_RATE{loop_number}:SP"
    )
    ramp_rate_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}RAMP_RATE{loop_number}:SP:RBV"
    )

    ramp_on_sp = FormattedComponent(
        EpicsSignal, "{prefix}RAMP_ON{loop_number}:SP"
    )
    ramp_on_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}RAMP_ON{loop_number}:SP:RBV"
    )

    control_sp = FormattedComponent(
        EpicsSignal, "{prefix}CTRL_IN{loop_number}:SP", kind="config"
    )
    control_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}CTRL_IN{loop_number}:SP:RBV", kind="config"
    )

    manual_sp = FormattedComponent(
        EpicsSignal, "{prefix}MANUAL_OUT{loop_number}:SP"
    )
    manual_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}MANUAL_OUT{loop_number}:SP:RBV"
    )

    mode_sp = FormattedComponent(
        EpicsSignal, "{prefix}OUT_MODE{loop_number}:SP", kind="config"
    )
    mode_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}OUT_MODE{loop_number}:SP:RBV", kind="config"
    )

    def __init__(self, prefix, loop_number, **kwargs):
        self.loop_number = loop_number
        super().__init__(prefix=prefix, **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        else:
            self._settle_time = value

    def pause(self):
        """Change setpoint to current position."""
        self.temp_sp.put(self.temp)


class Lakeshore336(Device):
    """
    An *ophyd* device for the Lakeshore336, designed to control loop configurations
    and general parameters. This Lakeshore model allows for the instantiation of up to
    4 control loops; however, at most beamlines, only 2 of these loops are actually used.
    """

    loop1 = FormattedComponent(Lakeshore336_LoopControl, "{prefix}", loop_number=1)
    loop2 = FormattedComponent(Lakeshore336_LoopControl, "{prefix}", loop_number=2)
