from enum import Enum, IntEnum  # numpydoc ignore=GL08
from ophyd import EpicsSignal, EpicsSignalRO, Component, Device
from ophyd.status import StableSubscriptionStatus
from ophyd.flyers import FlyerInterface
from ophyd.device import create_device_from_components
from time import time as ttime


# --- Enums for mbbi PVs --- #
class SegmentType(str, Enum):
    """Enum for EU3508/EU2408 segment types."""

    END = "End"
    RAMP_RATE = "Ramp (Rate)"
    RAMP_TIME_TO_TARGET = "Ramp (Time to target)"
    DWELL = "Dwell"


class SegmentEndType(str, Enum):
    """Enum for EU2408 segment end types."""

    DWELL = "Dwell"
    RESET = "Reset"
    SHUTDOWN = "Shutdown"


class EU3508ProgStatusType(IntEnum):
    """IntEnum for EU3508 Status types."""

    NOT_RUNNING = 0
    RUNNING = 1
    HOLD = 2
    HOLDBACK = 3
    END = 4


class EpicsSignalWithRBV(EpicsSignal):  # numpydoc ignore=PR01
    """An Epics signal with `write_pv` being `pvname` and `read_pv` being `pvname:RBV`."""

    def __init__(self, prefix, **kwargs):  # numpydoc ignore=GL08
        super().__init__(prefix + ":RBV", write_pv=prefix, **kwargs)


class EU3508PID(Device):
    """PID control PVs of EU3508."""

    p = Component(EpicsSignalRO, "P:RBV", kind="config")
    p2 = Component(EpicsSignalRO, "P2:RBV", kind="config")
    p3 = Component(EpicsSignalRO, "P3:RBV", kind="config")

    i = Component(EpicsSignalRO, "I:RBV", kind="config")
    i2 = Component(EpicsSignalRO, "I2:RBV", kind="config")
    i3 = Component(EpicsSignalRO, "I3:RBV", kind="config")

    d = Component(EpicsSignalRO, "D:RBV", kind="config")
    d2 = Component(EpicsSignalRO, "D2:RBV", kind="config")
    d3 = Component(EpicsSignalRO, "D3:RBV", kind="config")

    boundary1 = Component(EpicsSignalRO, "PIDB1:RBV", kind="config")
    boundary2 = Component(EpicsSignalRO, "PIDB2:RBV", kind="config")


class EU3508Segment(Device):
    """Segment configuration PVs of EU3508."""

    duration = Component(EpicsSignalWithRBV, "DUR", kind="config", write_timeout=10)
    end_type = Component(
        EpicsSignalWithRBV, "ENDTYP", string=True, kind="config", write_timeout=10
    )
    ramp_rate = Component(EpicsSignalWithRBV, "RT", kind="config", write_timeout=10)
    temperature = Component(EpicsSignalWithRBV, "TGT", kind="config", write_timeout=10)
    type = Component(
        EpicsSignalWithRBV, "TYP", string=True, kind="config", write_timeout=10
    )


class EU3508SegmentStatus(Device):
    """Current segment status of EU3508."""

    rate = Component(EpicsSignalRO, "CURRENT_RATE:RBV", kind="config")
    target_setpoint = Component(EpicsSignalRO, "CURRENT_SETPOINT:RBV", kind="config")
    type = Component(EpicsSignalRO, "CURRENT_SEG_TYP:RBV", kind="config")
    segment_number = Component(EpicsSignalRO, "CURRENT_SEG:RBV", kind="config")
    time = Component(EpicsSignalRO, "CURRENT_SEG_TIME_LEFT:RBV", kind="config")
    time_remaining = Component(EpicsSignalRO, "CURRENT_TIME_LEFT:RBV", kind="config")


class EU3508Status(Device):
    """EU3508 device status PVs."""

    pid = Component(EU3508PID, "LOOP1:")
    status = Component(EpicsSignalRO, "STAT:RBV", kind="config", string=True)
    mode = Component(EpicsSignalRO, "LOOP1:MAN:RBV", string=True, kind="config")
    power = Component(EpicsSignalRO, "LOOP1:O:RBV", kind="config")


def _createSegmentComponents(cls=EU3508Segment, prog_num: str = "0", kind="config"):
    """
    Creates a dictionary that is passed to `create_device_from_components`.
    The dictionary's entries signature is `{"s{i}": Component(cls, "PROG{prog_num}:S{i}:", kind="config)}`

    Parameters
    ----------
    cls: class
        Class of signal/device to be created inside the parent.

    kind: str or `ophyd.Kind`
        Parameter passed to the signal/device.
    """
    components = {}
    for i in range(15):
        components.update(
            {f"s{i}": Component(cls, f"PROG{prog_num}:S{i + 1}:", kind=kind)}
        )
    return components


class EU3508(Device, FlyerInterface):
    """EU3508 Ophyd Device, with FlyerInterface."""

    readback = Component(EpicsSignalRO, "LOOP1:PV:RBV", kind="hinted")
    setpoint = Component(EpicsSignalRO, "LOOP1:WSP:RBV", kind="config")

    start = Component(EpicsSignal, "PROG0:RUN", kind="config")
    skip = Component(EpicsSignal, "PROG0:SKIP", kind="config")
    reset = Component(EpicsSignal, "PROGRESET", kind="config", write_timeout=10)  # stop
    hold = Component(EpicsSignal, "PROGHOLD", kind="config", write_timeout=10)  # pause
    run_hold = Component(
        EpicsSignal, "PROG0:RUNHOLD", kind="config", write_timeout=10
    )  # resume
    running = Component(EpicsSignal, "PROGSTAT:RBV", kind="config")

    status = Component(EU3508Status, "", kind="config")
    segment_status = Component(EU3508SegmentStatus, "PROG:", kind="config")
    segment = Component(
        create_device_from_components("segment", **_createSegmentComponents()), ""
    )

    def kickoff(self):  # numpydoc ignore=GL08
        return self.start.set(1)

    def _check_ramp_done(self, value, old_value, **kwargs):
        """Callback to check if EU3508 has finished a given segment."""
        return old_value == EU3508ProgStatusType.RUNNING and (
            value == EU3508ProgStatusType.END
            or value == EU3508ProgStatusType.NOT_RUNNING
        )

    def complete(self):  # numpydoc ignore=GL08
        return StableSubscriptionStatus(self.running, self._check_ramp_done, 5)

    def describe_collect(self):  # numpydoc ignore=GL08
        descriptor = {"blower": {}}
        return descriptor

    def collect(self):  # numpydoc ignore=GL08
        data = {}
        timestamps = {}
        return [{"time": ttime(), "data": data, "timestamps": timestamps}]

    def pause(self):  # numpydoc ignore=GL08
        self.hold.set(1, timeout=5).wait()
        return super().pause()

    def resume(self):  # numpydoc ignore=GL08
        self.run_hold.set(1, timeout=5).wait()
        return super().resume()

    def stop(self, *, success=False):  # numpydoc ignore=GL08
        self.reset.set(0, timeout=5).wait()
        return super().stop(success=success)
