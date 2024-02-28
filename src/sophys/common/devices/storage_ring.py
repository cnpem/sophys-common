from ophyd import Device, Component, EpicsSignalRO


class StorageRing(Device):
    ring_current = Component(
        EpicsSignalRO, "SI-Glob:AP-CurrInfo:Current-Mon", lazy=True
    )

    _default_read_attrs = ["ring_current"]

    def __init__(self, *, name, **kwargs):
        super().__init__(prefix="", name=name, **kwargs)
