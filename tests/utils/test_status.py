import pytest

from sophys.common.utils.status import PremadeStatus


def test_premade_status_success():
    sts = PremadeStatus(True)
    assert sts.done
    assert sts.success


def test_premade_status_fail():
    sts = PremadeStatus(False)
    assert sts.done
    assert not sts.success


def test_premade_status_fail_custom_exception():
    custom_exception = ValueError("something something")
    sts = PremadeStatus(False, exception=custom_exception)
    assert sts.done
    assert not sts.success
    assert sts.exception() == custom_exception


def test_premade_status_success_with_exception():
    custom_exception = ValueError("something something")

    with pytest.raises(AssertionError):
        PremadeStatus(True, exception=custom_exception)
