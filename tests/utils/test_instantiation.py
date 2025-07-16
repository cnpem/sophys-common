import pytest

import functools

from ophyd import Signal, EpicsSignal

from sophys.common.utils.instantiation import warn_on_timeout


class EpicsSignalConnectingAtInstantiation(EpicsSignal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wait_for_connection(timeout=0.2)


def test_warn_on_timeout():
    log = []

    def logger(s):
        log.append(s)

    _w = functools.partial(warn_on_timeout, logger=logger)

    # Should not error
    _w(Signal, name="abc")
    assert len(log) == 0

    # Should error (but not TimeoutError)
    with pytest.raises(TypeError):
        _w(Signal)
    assert len(log) == 0

    # Should error (with TimeoutError)
    _w(EpicsSignalConnectingAtInstantiation, read_pv="this_pv_does_not_exist")
    assert len(log) != 0
