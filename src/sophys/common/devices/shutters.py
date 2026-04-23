from ophyd import EpicsSignal, EpicsSignalRO, FormattedComponent, Device
from ophyd.pv_positioner import PVPositionerComparator
from ..utils.status import PremadeStatus
from ophyd.status import AndStatus, SubscriptionStatus


class ShutterToggle(PVPositionerComparator):
    """
    Abstraction layer for shutters with one actuation PV (OPENCLOSE) and one readback PV (PG_STATUS). There's an optional parameter for a permission PV.

    Parameters
    ----------
    prefix: str
        Prefix for the shutter's PVs.

    setpoint_suffix: str
        Suffix for the actuation PV. NOTE: This should be place/location of the shutter, e.g. OEA/FOE.
        The PV will be formatted as "{prefix}{setpoint_suffix}OPENCLOSE".

    readback_suffix: str
        Suffix for the readback PV, e.g. PG_STATUS

    permission_suffix: str, optional
        Permission PV string, if it exists.

    NOTE
    ----
    This implemantation considers that the value of the `readback` signal is 0 for an open shutter and 1 for a closed shutter.
    This is not so intuitive, so the `set` method considers that 1 is for opening and 0 for closing the shutter.

    Usage Example
    -------------
    >>> shutter = ShutterOpenClose(prefix="prefix", setpoint_suffix="setpoint_suffix", readback="readback_suffix", name="shutter")
    >>> shutter.set(0).wait() # for closing
    >>> shutter.set(1).wait() # for opening
    """

    real_setpoint = None
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}{setpoint_suffix}OPENCLOSE", kind="config"
    )
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}{readback_suffix}", kind="hinted"
    )

    def __init__(
        self,
        *args,
        setpoint_suffix: str,
        readback_suffix: str,
        permission_pv: str = None,
        **kwargs,
    ):
        self.setpoint_suffix = setpoint_suffix
        self.readback_suffix = readback_suffix
        self.permission_pv = permission_pv
        super().__init__(*args, **kwargs)
        if self.permission_pv is not None:
            self.permission = EpicsSignalRO(f"{self.permission_pv}", name="permission")
            self.permission_flag = True
        else:
            self.permission_flag = False

    def set(self, value, *args, **kwargs):
        if self.permission_flag:
            try:
                if not self.permission.get(connection_timeout=2, **kwargs):
                    raise PremadeStatus(
                        success=False,
                        exception=PermissionError(
                            f"Shutter open permission is denied: {self.permission.pvname} {self.permission.get()}"
                        ),
                    )
            except TimeoutError:
                raise
        if (
            value == self.readback.get()
        ):  # Since we're swapping the readback values (0 for closing and 1 for opening), we actuate when value == readback
            self.real_setpoint = 1 if value == 0 else 0
            return super().set(1, *args, **kwargs)
        else:
            return PremadeStatus(success=True)

    def done_comparator(self, readback, setpoint):
        return self.real_setpoint == readback


class ShutterOpenClose(Device):
    """
    Abstraction layer for shutters with two actuation PV (OPEN and CLOSE) and two readback PV (PS_STATUS and GS_STATUS). There's an optional parameter for a permission PV.

    Parameters
    ----------
    prefix: str
        Prefix for the shutter's PVs.

    shutter_suffix: str
        Suffix for the OPEN and CLOSE PVs. NOTE: This should be place/location of the shutter, e.g. OEA/FOE.
        The PVs will be formatted as "{prefix}{shutter_suffix}OPEN" and "{prefix}{shutter_suffix}CLOSE".

    ps_suffix: str
        Suffix for one readback PVs, e.g. PS_STATUS

    gs_suffix: str
        Suffix for the second readback PV, e.g. GS_STATUS

    permission_pv: str, optional
        Permission PV string, if it exists.

    NOTES
    -----
    This implemantation considers that the value of the `readback` signal is 0 for an open shutter and 1 for a closed shutter.
    This is not so intuitive, so the `set` method considers that 1 is for openig and 0 for closing the shutter.

    The `return` of the `set` method is an `AndStatus` with both `readback` signals.

    There's a `done_comparator` method that returns the state of the shutter, based in the two `readback` PVs. This method is
    used as the `callback` for both `readback` signals.

    Usage Example
    -------------
    >>> shutter = ShutterToggle(prefix="prefix", open_suffix="open_suffix", close_suffix="close_suffix", ps_suffix="ps_suffix", gs_suffix="gs_suffix", name="shutter")
    >>> shutter.set(0).wait() # for closing
    >>> shutter.set(1).wait() # for opening
    """

    setpoint = None
    photon_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{ps_suffix}", kind="hinted"
    )
    gamma_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{gs_suffix}", kind="hinted"
    )
    open = FormattedComponent(
        EpicsSignal, "{prefix}{shutter_suffix}OPEN", kind="config"
    )
    close = FormattedComponent(
        EpicsSignal, "{prefix}{shutter_suffix}CLOSE", kind="config"
    )

    def __init__(
        self,
        *args,
        shutter_suffix: str,
        ps_suffix: str,
        gs_suffix: str,
        permission_pv: str = None,
        **kwargs,
    ):
        self.shutter_suffix = shutter_suffix
        self.ps_suffix = ps_suffix
        self.gs_suffix = gs_suffix
        self.permission_pv = permission_pv
        super().__init__(*args, **kwargs)
        if self.permission_pv is not None:
            self.permission = EpicsSignalRO(f"{self.permission_pv}", name="permission")
            self.permission_flag = True
        else:
            self.permission_flag = False

    def set(self, value, *args, **kwargs):
        if self.permission_flag:
            try:
                if not self.permission.get(connection_timeout=2, **kwargs):
                    raise PremadeStatus(
                        success=False,
                        exception=PermissionError(
                            f"Shutter open permission is denied: {self.permission.pvname} {self.permission.get()}"
                        ),
                    )
            except TimeoutError:
                raise

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
            SubscriptionStatus(self.photon_status, self.done_comparator, settle_time=3),
            SubscriptionStatus(self.gamma_status, self.done_comparator, settle_time=3),
            timeout=15,
        )

    def done_comparator(self, value, **kwargs):
        is_closed = (
            self.photon_status.get() == 1 and self.gamma_status.get() == 1
        )  # NOTE: if one of the status is equal to zero, the shutter can be partially open
        return is_closed if self.setpoint == 0 else not is_closed
