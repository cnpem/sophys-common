from ophyd import EpicsSignal, EpicsSignalRO, FormattedComponent, Device
from ophyd.pv_positioner import PVPositionerComparator
from ..utils.status import PremadeStatus
from ophyd.status import AndStatus, SubscriptionStatus


class ShutterOpenClose(PVPositionerComparator):
    """
    Abstraction layer for shutters with one actuation PV (OPENCLOSE) and one readback PV (PG_STATUS). There's an optional parameter for a permission PV.

    Parameters
    ----------
    prefix: str
        Prefix for the shutter's PVs.

    setpoint_suffix: str
        Suffix for the actuation PV, e.g. OPENCLOSE

    readback_suffix: str
        Suffix for the readback PV, e.g. PG_STATUS

    permission_suffix: str, optional
        Suffix for a open permssion PV, if it exists.

    NOTE
    ----
    This implemantation considers that the value of the `readback` signal is 0 for an open shutter and 1 for a closed shutter.
    This is not so intuitive, so the `set` method considers that 1 is for opennig and 0 for closing the shutter.

    Usage Example
    -------------
    >>> shutter = ShutterOpenClose(prefix="prefix", setpoint_suffix="setpoint_suffix", readback="readback_suffix", name="shutter")
    >>> from bluesky.plans_stubs import mv
    >>> RE(mv(shutter, 0)) # for closing
    >>> RE(mv(shutter, 1)) # for opennig
    """

    real_setpoint = None
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}{setpoint_suffix}", kind="config"
    )
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}{readback_suffix}", kind="hinted"
    )
    permission = FormattedComponent(
        EpicsSignalRO, "{permission_pv}", string=True, kind="config"
    )

    def __init__(
        self, *args, setpoint_suffix, readback_suffix, permission_suffix, **kwargs
    ):
        self.setpoint_suffix = setpoint_suffix
        self.readback_suffix = readback_suffix
        self.permission_suffix = permission_suffix
        super().__init__(*args, **kwargs)

    def set(self, value, *args, **kwargs):
        if self.permission.connected:
            if not self.permission.get():
                raise PremadeStatus(
                    success=False,
                    exception=PermissionError(
                        f"Shutter open permission is denied: {self.permission.pvname} {self.permission.get()}"
                    ),
                )

        if (
            value == self.readback.get()
        ):  # Since we're swapping the readback values (o for closing and 1 for opennig), we actuate when value == readback
            self.real_setpoint = 1 if value == 0 else 0
            return super().set(1, *args, **kwargs)
        else:
            return PremadeStatus(success=True)

    def done_comparator(self, readback, setpoint):
        return self.real_setpoint == readback


class ShutterToggle(Device):
    """
    Abstraction layer for shutters with two actuation PV (OPEN and CLOSE) and two readback PV (PS_STATUS and GS_STATUS). There's an optional parameter for a permission PV.

    Parameters
    ----------
    prefix: str
        Prefix for the shutter's PVs.

    open_suffix: str
        Suffix for the open actuation PV, e.g. OPEN

    close_suffix: str
        Suffix for the close actuation PV, e.g. CLOSE

    ps_suffix: str
        Suffix for one readback PVs, e.g. PS_STATUS

    close_suffix: str
        Suffix for the second readback PV, e.g. GS_STATUS

    permission_suffix: str, optional
        Suffix for a open permssion PV, if it exists.

    NOTES
    -----
    This implemantation considers that the value of the `readback` signal is 0 for an open shutter and 1 for a closed shutter.
    This is not so intuitive, so the `set` method considers that 1 is for opennig and 0 for closing the shutter.

    The `return` of the `set` method is an `AndStatus` with both `readback` signals.

    There's a `done_comparator` method that returns the state of the shutter, based in the two `readback` PVs. This method is
    used as the `callback` for both `readback` signals.

    Usage Example
    -------------
    >>> shutter = ShutterToggle(prefix="prefix", open_suffix="open_suffix", close_suffix="close_suffix", ps_suffix="ps_suffix", gs_suffix="gs_suffix", name="shutter")
    >>> from bluesky.plans_stubs import mv
    >>> RE(mv(shutter, 0)) # for closing
    >>> RE(mv(shutter, 1)) # for opennig
    """

    setpoint = None
    photon_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{ps_suffix}", kind="hinted"
    )
    gamma_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{gs_suffix}", kind="hinted"
    )
    open = FormattedComponent(EpicsSignal, "{prefix}{open_suffix}", kind="config")
    close = FormattedComponent(EpicsSignal, "{prefix}{close_suffix}", kind="config")
    permission = FormattedComponent(
        EpicsSignalRO, "{permission_pv}", string=True, kind="config"
    )

    def __init__(
        self,
        *args,
        open_suffix,
        close_suffix,
        ps_suffix,
        gs_suffix,
        permission_suffix,
        **kwargs,
    ):
        self.open_suffix = open_suffix
        self.close_suffix = close_suffix
        self.ps_suffix = ps_suffix
        self.gs_suffix = gs_suffix
        self.permission_suffix = permission_suffix
        super().__init__(*args, **kwargs)

    def set(self, value, *args, **kwargs):
        if self.permission.connected:
            if not self.permission.get():
                raise PremadeStatus(
                    success=False,
                    exception=PermissionError(
                        f"Shutter open permission is denied: {self.permission.pvname} {self.permission.get()}"
                    ),
                )

        if value == 0:
            self.close.set(1, *args, **kwargs).wait()

        elif value == 1:
            self.open.set(1, *args, **kwargs).wait()

        else:
            raise PremadeStatus(
                success=False,
                exception=Exception(f"The value {value} is not a valid option!"),
            )

        self.setpoint = value

        return AndStatus(
            SubscriptionStatus(self.phton_status, self.done_comparator, settle_time=3),
            SubscriptionStatus(self.gamma_status, self.done_comparator, settle_time=3),
            timeout=15,
        )

    def done_comparator(self, value, **kwargs):
        is_closed = (
            self.phton_status.get() == 1 and self.gamma_status.get() == 1
        )  # NOTE: if one of the status is equal to zero, the shutter can be partially open
        return is_closed if self.setpoint == 0 else not is_closed
