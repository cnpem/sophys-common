from ophyd import (
    Device,
    Component,
    Signal,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    Kind,
)


class HDDCM(Device):
    class FollowerEpicsSignal(Signal):
        enable = Component(EpicsSignal, "EnableFollower")
        disable = Component(EpicsSignal, "DisableFollower")

        readback = Component(EpicsSignalRO, "EnableFollower_RBV")

        def set(self, value, **kwargs):
            if bool(value):
                return self.enable.set(1, **kwargs)
            else:
                return self.disable.set(1, **kwargs)

        def get(self, **kwargs):
            return self.readback.get(**kwargs)

    follower_mode = Component(FollowerEpicsSignal, "UndUz_")

    harmonic = Component(EpicsSignalWithRBV, "UndUz_Harmonic", kind=Kind.hinted)
    energy = Component(EpicsSignalRO, "GonRx_Energy_RBV", kind=Kind.hinted)

    gonio_position = Component(EpicsSignalRO, "GonRx_S_RBV")

    in_position = Component(EpicsSignalRO, "GonRx_DesVelZero_RBV")
