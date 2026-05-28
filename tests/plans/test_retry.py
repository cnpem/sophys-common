from collections import defaultdict

from bluesky import RunEngine, plan_stubs as bps
from bluesky.utils import FailedStatus

from ophyd import Signal

from sophys.common.plans import mv_with_retry


class FailfulSignal(Signal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._attempts = defaultdict(lambda: 0)

    def reset(self):
        self._attempts.clear()
        super().put(0)

    def put(self, value, **kwargs):
        self._attempts[value] += 1

        if self._attempts[value] >= value:
            return super().put(value, **kwargs)

    def set(self, value, **kwargs):
        return super().set(value, timeout=0.2, **kwargs)


def test_mv_with_retry():
    signal = FailfulSignal(name="sig")

    RE = RunEngine()

    def plan_mv():
        try:
            yield from bps.abs_set(signal, 2, wait=True)
        except FailedStatus:
            pass

        assert signal.get() == 0

        yield from bps.mv(signal, 2)
        assert signal.get() == 2

    RE(plan_mv())

    signal.reset()
    assert signal.get() == 0

    def plan_mv_with_retry():
        yield from mv_with_retry(signal, 3, retry_count=3)
        assert signal.get() == 3

    RE(plan_mv_with_retry())

    signal.reset()
    assert signal.get() == 0

    def plan_mv_with_not_enough_retries():
        did_throw = False
        try:
            yield from mv_with_retry(signal, 4, retry_count=3)
        except FailedStatus:
            did_throw = True

        assert signal.get() == 0
        assert did_throw

    RE(plan_mv_with_not_enough_retries())
