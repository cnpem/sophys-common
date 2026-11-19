from ophyd import (  # numpydoc ignore=GL08
    Component,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    FormattedComponent,
)
from ophyd.pv_positioner import PVPositionerIsClose


class Lakeshore336LoopControl(PVPositionerIsClose):
    """
    Temperature loop control for a Lakeshore 336.

    Parameters
    ----------
    prefix : str
        The prefix for the EPICS PVs.
    loop_number : int
        The loop number (1 or 2).
    settle_time : float, optional
        The time to wait for the temperature to settle after a setpoint change, in seconds.
    **kwargs : dict
        Additional keyword arguments to pass to the parent class.
    """

    setpoint = FormattedComponent(
        EpicsSignal,
        "{prefix}TEMP{loop_number}:SP:RBV",
        write_pv="{prefix}TEMP{loop_number}:SP",
    )

    readback = FormattedComponent(
        EpicsSignalRO,
        "{prefix}TEMP{loop_number}",
        kind="hinted",
    )

    atol = 0.1  # in Kelvin

    heater = FormattedComponent(
        EpicsSignalRO,
        "{prefix}HEATER{loop_number}:OUTPUT",
        kind="normal",
    )

    heater_range = FormattedComponent(
        EpicsSignal,
        "{prefix}HEATER{loop_number}:RANGE:SP:RBV",
        write_pv="{prefix}HEATER{loop_number}:RANGE:SP",
        string=True,
        kind="config",
    )

    pid_P = FormattedComponent(
        EpicsSignal,
        "{prefix}P{loop_number}:SP:RBV",
        write_pv="{prefix}P{loop_number}:SP",
        kind="config",
    )

    pid_I = FormattedComponent(
        EpicsSignal,
        "{prefix}I{loop_number}:SP:RBV",
        write_pv="{prefix}I{loop_number}:SP",
        kind="config",
    )

    pid_D = FormattedComponent(
        EpicsSignal,
        "{prefix}D{loop_number}:SP:RBV",
        write_pv="{prefix}D{loop_number}:SP",
        kind="config",
    )

    ramp_rate = FormattedComponent(
        EpicsSignal,
        "{prefix}RAMP_RATE{loop_number}:SP:RBV",
        write_pv="{prefix}RAMP_RATE{loop_number}:SP",
        kind="config",
    )

    ramp_on = FormattedComponent(
        EpicsSignal,
        "{prefix}RAMP_ON{loop_number}:SP:RBV",
        write_pv="{prefix}RAMP_ON{loop_number}:SP",
        kind="config",
    )

    control = FormattedComponent(
        EpicsSignal,
        "{prefix}CTRL_IN{loop_number}:SP:RBV",
        write_pv="{prefix}CTRL_IN{loop_number}:SP",
        kind="config",
    )

    manual_out = FormattedComponent(
        EpicsSignal,
        "{prefix}MANUAL_OUT{loop_number}:SP:RBV",
        write_pv="{prefix}MANUAL_OUT{loop_number}:SP",
        kind="config",
    )

    mode = FormattedComponent(
        EpicsSignal,
        "{prefix}OUT_MODE{loop_number}:SP:RBV",
        write_pv="{prefix}OUT_MODE{loop_number}:SP",
        kind="config",
    )

    def __init__(
        self,
        prefix: str,
        loop_number: int,
        settle_time: float = 0.0,
        **kwargs,
    ):
        """
        Initialize the Lakeshore336LoopControl device.

        Parameters
        ----------
        prefix : str
            The prefix for the EPICS PVs.
        loop_number : int
            The loop number (1 or 2).
        settle_time : float, optional
            The time to wait for the temperature to settle after a setpoint change, in seconds.
        **kwargs : dict
            Additional keyword arguments to pass to the parent class.
        """

        if loop_number not in (1, 2):
            raise ValueError("loop_number must be 1 or 2.")

        self.loop_number = loop_number
        self._paused_setpoint: float | None = None

        super().__init__(prefix=prefix, settle_time=settle_time, **kwargs)

    def pause(self):
        """Hold the current temperature by setting the loop setpoint to the current readback value."""
        current_sp = self.setpoint.get()
        current_temp = self.readback.get()
        self._paused_setpoint = current_sp
        return self.set(current_temp)

    def resume(self):
        """
        Restore the setpoint saved by `pause()`.

        Returns
        -------
        Status
            The status object returned by `set()`.
        """
        if self._paused_setpoint is None:
            raise RuntimeError("No paused setpoint stored. Call pause() first.")
        return self.set(self._paused_setpoint)


class Lakeshore336(Device):
    """Lakeshore336 temperature controller ophyd device."""

    loop1 = Component(Lakeshore336LoopControl, "", loop_number=1)
    loop2 = Component(Lakeshore336LoopControl, "", loop_number=2)
