from sophys.common.utils.status import PremadeStatus


def test_premade_status_success():
    sts = PremadeStatus(True)
    assert sts.done
    assert sts.success


def test_premade_status_fail():
    sts = PremadeStatus(False)
    assert sts.done
    assert not sts.success
