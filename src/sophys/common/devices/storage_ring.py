from ophyd import Component, Device  # numpydoc ignore=GL08

from sophys.common.utils import EpicsSignalWithRetryRO


class StorageRing(Device):  # numpydoc ignore=PR01
    """Useful signals from the Storage Ring."""

    ring_current = Component(
        EpicsSignalWithRetryRO,
        "SI-Glob:AP-CurrInfo:Current-Mon",
        kind="hinted",
        timeout=5,
        connection_timeout=5,
    )
    sofb = Component(EpicsSignalWithRetryRO, "SI-Glob:AP-SOFB:LoopState-Sts", lazy=True)
    fofb = Component(EpicsSignalWithRetryRO, "SI-Glob:AP-FOFB:LoopState-Sts", lazy=True)
    bbb_h = Component(EpicsSignalWithRetryRO, "SI-Glob:DI-BbBProc-H:FBCTRL", lazy=True)
    bbb_v = Component(EpicsSignalWithRetryRO, "SI-Glob:DI-BbBProc-V:FBCTRL", lazy=True)
    bbb_l = Component(EpicsSignalWithRetryRO, "SI-Glob:DI-BbBProc-L:FBCTRL", lazy=True)

    _default_read_attrs = ["ring_current"]  # noqa: RUF012

    def __init__(self, *, name, **kwargs):  # numpydoc ignore=GL08
        super().__init__(prefix="", name=name, **kwargs)
