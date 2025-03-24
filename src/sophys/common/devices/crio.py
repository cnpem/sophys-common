import threading

from ophyd import (
    Component,
    FormattedComponent as FormattedCpt,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    Kind,
)
from ophyd.device import create_device_from_components
from ophyd.status import Status

# Useful resources:
# https://cnpemcamp.sharepoint.com/sites/lnls/groups/sol/SitePages/CRIO-PVs.aspx


class _BaseCRIO(Device):
    pv_averaging_time = FormattedCpt(
        EpicsSignal, "{global_prefix}PvAvgTime", kind=Kind.config
    )
    file_averaging_time = FormattedCpt(
        EpicsSignal, "{global_prefix}FileAvgTime", kind=Kind.config
    )
    saving_to_file = FormattedCpt(
        EpicsSignalRO, "{global_prefix}AnalogSaving2File", kind=Kind.omitted
    )
    disable_file_close = FormattedCpt(
        EpicsSignal, "{global_prefix}DisableFileClose", kind=Kind.omitted
    )

    def __init__(self, prefix: str, **kwargs):
        # Get the prefix before the second to last ':' (without the card information)
        self.global_prefix = prefix[:-1].rpartition(":")[0] + ":"

        super().__init__(prefix, **kwargs)

        self._seen_devices = set()

    def cached_trigger(self, calling_child):
        """Call `trigger` only once per `trigger_and_read` operation."""
        # Only go forward if seen_devices is empty (first time here), or if
        # calling_child is in seen_devices (another trigger_and_read pair).
        # NOTE: This is so that we only trigger once for each point in a scan.
        if len(self._seen_devices) != 0 and calling_child not in self._seen_devices:
            self._seen_devices.add(calling_child)

            sts = Status()
            sts.set_finished()
            return sts

        self._seen_devices.clear()
        self._seen_devices.add(calling_child)

        return self.trigger()

    def trigger(self):
        sts = super().trigger()

        # Restart averaging window
        avg_time = self.pv_averaging_time.get()
        # If too small for the firmware, it will use the smallest it can.
        self.pv_averaging_time.set(0.001).wait()
        self.pv_averaging_time.set(avg_time).wait()

        status = Status()

        threading.Timer(avg_time, status.set_finished).start()

        return sts & status


class BaseAnalogInput(EpicsSignalRO):
    def trigger(self):
        sts = super().trigger()
        sts &= self.parent.cached_trigger(self)
        return sts


def __createAnalogIn(num: int) -> dict:
    components = {}
    for i in range(num):
        components.update(
            {
                f"ai{i}": Component(BaseAnalogInput, f"ai{i}", kind=Kind.hinted),
                f"ai{i}_offset": Component(
                    EpicsSignal, f"ai{i}_Offset", kind=Kind.config
                ),
                f"ai{i}_scale_factor": Component(
                    EpicsSignal, f"ai{i}_SF", kind=Kind.config
                ),
            }
        )
    return components


__CRIO_9215_docstring = """
An Ophyd device for the NI-9215 CompactRIO device, with 4 analog inputs.
"""

__CRIO_9220_docstring = """
An Ophyd device for the NI-9220 CompactRIO device, with 16 analog inputs.
"""

__CRIO_9223_docstring = """
An Ophyd device for the NI-9223 CompactRIO device, with 4 analog inputs.
"""


CRIO_9215 = create_device_from_components(
    "CRIO_9215",
    base_class=_BaseCRIO,
    docstring=__CRIO_9215_docstring,
    **__createAnalogIn(4),
)
CRIO_9220 = create_device_from_components(
    "CRIO_9220",
    base_class=_BaseCRIO,
    docstring=__CRIO_9220_docstring,
    **__createAnalogIn(16),
)
CRIO_9223 = create_device_from_components(
    "CRIO_9223",
    base_class=_BaseCRIO,
    docstring=__CRIO_9223_docstring,
    **__createAnalogIn(4),
)


class CRIO_9403(_BaseCRIO):
    """
    An Ophyd device for the NI-9403 CompactRIO device.

    Commonly used as a :ref:`tatu`, this device contains low-level debug signals for such usages.
    """

    bi0 = Component(EpicsSignalRO, "bi0")
    bi1 = Component(EpicsSignalRO, "bi1")
    bi2 = Component(EpicsSignalRO, "bi2")
    bi3 = Component(EpicsSignalRO, "bi3")

    bo4 = Component(EpicsSignalWithRBV, "bo4")
    bo5 = Component(EpicsSignalWithRBV, "bo5")
    bo6 = Component(EpicsSignalWithRBV, "bo6")
    bo7 = Component(EpicsSignalWithRBV, "bo7")

    bi8 = Component(EpicsSignalRO, "bi8")
    bi9 = Component(EpicsSignalRO, "bi9")
    bi10 = Component(EpicsSignalRO, "bi10")
    bi11 = Component(EpicsSignalRO, "bi11")

    bo12 = Component(EpicsSignalWithRBV, "bo12")
    bo13 = Component(EpicsSignalWithRBV, "bo13")
    bo14 = Component(EpicsSignalWithRBV, "bo14")
    bo15 = Component(EpicsSignalWithRBV, "bo15")

    bi16 = Component(EpicsSignalRO, "bi16")
    bi17 = Component(EpicsSignalRO, "bi17")
    bi18 = Component(EpicsSignalRO, "bi18")
    bi19 = Component(EpicsSignalRO, "bi19")

    bo20 = Component(EpicsSignalWithRBV, "bo20")
    bo21 = Component(EpicsSignalWithRBV, "bo21")
    bo22 = Component(EpicsSignalWithRBV, "bo22")
    bo23 = Component(EpicsSignalWithRBV, "bo23")
