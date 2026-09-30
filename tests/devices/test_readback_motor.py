import numpy as np
import pytest
from ophyd.utils.errors import UnknownStatusFailure

from sophys.common.devices.motor import ReadbackEpicsMotor


def create_motor(prefix, name="test_motor", **kwargs):
    return ReadbackEpicsMotor(
        prefix,
        name=name,
        tolerance=kwargs.pop("tolerance", 1e-7),
        relative_tolerance=kwargs.pop("relative_tolerance", 0.0),
        timeout=kwargs.pop("timeout", 1.0),
        **kwargs,
    )


def test_rbv_motor_connection(soft_ioc):
    motor = create_motor(f"{soft_ioc}SLIT:TOP")
    motor.wait_for_connection(2.0)


def test_move_succeeds_when_readback_is_within_tolerance(soft_ioc):
    motor = create_motor(f"{soft_ioc}SLIT:TOP")
    motor.wait_for_connection(2.0)

    status = motor.move(1.0)

    assert status.success
    assert np.isclose(motor.user_readback.get(), 1.0)


def test_move_wait_false_returns_status(soft_ioc):
    motor = create_motor(f"{soft_ioc}SLIT:TOP", name="async_motor")
    motor.wait_for_connection(2.0)
    status = motor.move(2.0, wait=False)
    status.wait(timeout=2.0)

    assert motor.user_readback.get() == 2.0
    assert status.success


def test_fails_when_readback_is_outside_tolerance(soft_ioc):
    motor = create_motor(f"{soft_ioc}READBACK", name="offset_motor", timeout=1.0)
    motor.wait_for_connection(2.0)

    status = motor.move(1.0, wait=False)

    with pytest.raises(UnknownStatusFailure):
        status.wait(timeout=2.0)

    assert status.done
    assert not status.success
