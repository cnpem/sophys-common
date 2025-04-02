from ophyd import Device, Component, EpicsSignalRO


class StorageRing(Device):
    """Useful signals from the Storage Ring."""

    ring_current = Component(
        EpicsSignalRO,
        "SI-Glob:AP-CurrInfo:Current-Mon",
        kind="hinted",
        timeout=5,
        connection_timeout=5,
    )

    _default_read_attrs = ["ring_current"]

    def __init__(self, *, name, **kwargs):
        super().__init__(prefix="", name=name, **kwargs)
