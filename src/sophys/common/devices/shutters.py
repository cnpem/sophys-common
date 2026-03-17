from ophyd import EpicsSignal, EpicsSignalRO, FormattedComponent, Device
from ophyd.pv_positioner import PVPositionerComparator
from ..utils.status import PremadeStatus
from ophyd.status import AndStatus, SubscriptionStatus


class ShutterOpenClose(PVPositionerComparator):
    real_setpoint = None
    setpoint = FormattedComponent(EpicsSignal, "{prefix}{setpoint_suffix}")
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}{readback_suffix}", kind="hinted"
    )
    permission = FormattedComponent(
        EpicsSignalRO, "{prefix}{permission_suffix}", string=True
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

        if value == self.readback.get():
            self.real_setpoint = 1 if value == 0 else 0
            return super().set(1, *args, **kwargs)
        else:
            return PremadeStatus(success=True)

    def done_comparator(self, readback, setpoint):
        return self.real_setpoint == readback


class ShutterToggle(Device):
    setpoint = None
    phton_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{ps_suffix}", kind="hinted"
    )
    gamma_status = FormattedComponent(
        EpicsSignalRO, "{prefix}{gs_suffix}", kind="hinted"
    )
    open = FormattedComponent(EpicsSignal, "{prefix}{open_suffix}")
    close = FormattedComponent(EpicsSignal, "{prefix}{close_suffix}")
    permission = FormattedComponent(
        EpicsSignalRO, "{prefix}{permission_suffix}", string=True
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
