from ophyd import (  # numpydoc ignore=GL08
    Device,
    EpicsSignal,
    EpicsSignalRO,
    FormattedComponent,
)


class Lakeshore336LoopControl(Device):
    """
    Loop control and general parameter configuration on the Lakeshore336.

    Parameters
    ----------
    prefix : str
        The EPICS prefix for the Lakeshore336.
    loop_number : int
        The loop number to control (1 or 2).
    **kwargs : dict
        Additional keyword arguments are passed to the Device constructor.
    """

    temp = FormattedComponent(EpicsSignalRO, "{prefix}TEMP{loop_number}")

    temp_sp = FormattedComponent(EpicsSignal, "{prefix}TEMP{loop_number}:SP")
    temp_sp_rbv = FormattedComponent(EpicsSignalRO, "{prefix}TEMP{loop_number}:SP:RBV")

    heater = FormattedComponent(
        EpicsSignalRO,
        "{prefix}HEATER{loop_number}:OUTPUT",
        auto_monitor=True,
        kind="normal",
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

    # Lakeshore configuration
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

    ramp_rate_sp = FormattedComponent(EpicsSignal, "{prefix}RAMP_RATE{loop_number}:SP")
    ramp_rate_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}RAMP_RATE{loop_number}:SP:RBV"
    )

    ramp_on_sp = FormattedComponent(EpicsSignal, "{prefix}RAMP_ON{loop_number}:SP")
    ramp_on_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}RAMP_ON{loop_number}:SP:RBV"
    )

    control_sp = FormattedComponent(
        EpicsSignal, "{prefix}CTRL_IN{loop_number}:SP", kind="config"
    )
    control_rbv = FormattedComponent(
        EpicsSignalRO, "{prefix}CTRL_IN{loop_number}:SP:RBV", kind="config"
    )

    manual_sp = FormattedComponent(EpicsSignal, "{prefix}MANUAL_OUT{loop_number}:SP")
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
        """
        Initialize the Lakeshore336LoopControl device.

        Parameters
        ----------
        prefix : str
            The EPICS prefix for the Lakeshore336.
        loop_number : int
            The loop number to control (1 or 2).
        **kwargs : dict
            Additional keyword arguments are passed to the Device constructor.
        """

        self.loop_number = loop_number
        super().__init__(prefix=prefix, **kwargs)
        self._settle_time = 0

    @property
    def settle_time(self):
        """Settle time in seconds to wait after a setpoint change before reading the temperature."""

        return self._settle_time

    @settle_time.setter
    def settle_time(self, value):
        """
        Settle time in seconds to wait after a setpoint change before reading the temperature.

        Parameters
        ----------
        value : float
            The settle time in seconds. Must be greater than or equal to 0.
        """
        if value < 0:
            raise ValueError("Settle value needs to be >= 0.")
        self._settle_time = value

    def pause(self):
        """Change setpoint to current position."""

        self.temp_sp.put(self.temp)


class Lakeshore336(Device):
    """Lakeshore336 temperature controller ophyd device."""

    loop1 = FormattedComponent(Lakeshore336LoopControl, "{prefix}", loop_number=1)
    loop2 = FormattedComponent(Lakeshore336LoopControl, "{prefix}", loop_number=2)
