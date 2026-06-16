import pytest

import asyncio

from typing import Annotated as A
from unittest.mock import ANY

from ophyd_async.core import init_devices, set_mock_value, SignalR, SignalRW
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.epics.core import EpicsDevice, PvSuffix as Pv
from ophyd_async.testing import (
    StatusWatcher,
    assert_reading,
    assert_value,
    wait_for_pending_wakeups,
)

from sophys.common.devices.async_positioner import BasePositioner


async def _test_positioner_movement(
    positioner: BasePositioner,
    before_set_func=None,
    after_set_func=None,
    before_end_func=None,
    initial_pos: float = 0.0,
    final_pos: float = 1.0,
):
    if before_set_func is not None:
        await before_set_func()
    s = positioner.set(final_pos)

    watcher = StatusWatcher(s)
    await watcher.wait_for_call(
        name=positioner.name,
        current=initial_pos,
        initial=initial_pos,
        target=final_pos,
        time_elapsed=ANY,
    )
    # Wait a bit and give it an update, checking that the watcher is called with it
    await asyncio.sleep(0.1)

    await assert_value(positioner.setpoint, final_pos)
    assert not s.done

    if after_set_func is not None:
        await after_set_func(s)

    set_mock_value(positioner.readback, (final_pos - initial_pos) / 2)
    await watcher.wait_for_call(
        name=positioner.name,
        current=(final_pos - initial_pos) / 2,
        initial=initial_pos,
        target=final_pos,
        time_elapsed=ANY,
    )

    # Make it almost get there and check that it completes
    set_mock_value(positioner.readback, final_pos - 1e-9)
    await wait_for_pending_wakeups()

    if before_end_func is not None:
        await before_end_func(s)
        await wait_for_pending_wakeups()

    assert s.done
    assert s.success


class _SimpleMockPositioner(BasePositioner, EpicsDevice):
    readback: A[SignalR[float], Pv("Readback"), Format.HINTED_SIGNAL]
    setpoint: A[SignalRW[float], Pv("Setpoint")]


@pytest.fixture
async def simple_mock_positioner():
    async with init_devices(mock=True):
        simple_mock_positioner = _SimpleMockPositioner("PV:TEST:")

    set_mock_value(simple_mock_positioner.readback, 0.0)
    set_mock_value(simple_mock_positioner.setpoint, 0.0)

    yield simple_mock_positioner


async def test_simple_positioner(simple_mock_positioner):
    set_mock_value(simple_mock_positioner.readback, 0.5)
    await assert_value(simple_mock_positioner.readback, 0.5)
    await assert_reading(
        simple_mock_positioner,
        {
            "simple_mock_positioner": {
                "value": 0.5,
                "timestamp": ANY,
                "alarm_severity": 0,
            }
        },
    )

    set_mock_value(simple_mock_positioner.readback, 0.0)
    await assert_value(simple_mock_positioner.readback, 0.0)
    await assert_reading(
        simple_mock_positioner,
        {
            "simple_mock_positioner": {
                "value": 0.0,
                "timestamp": ANY,
                "alarm_severity": 0,
            }
        },
    )

    await _test_positioner_movement(simple_mock_positioner)


class _MockPositionerWithActuator(BasePositioner, EpicsDevice):
    readback: A[SignalR[float], Pv("Readback"), Format.HINTED_SIGNAL]
    setpoint: A[SignalRW[float], Pv("Setpoint")]

    actuate: A[SignalRW[float], Pv("Actuate")]
    actuate_value = 2.5


@pytest.fixture
async def mock_positioner_with_actuator():
    async with init_devices(mock=True):
        mock_positioner_with_actuator = _MockPositionerWithActuator("PV:TEST:")

    set_mock_value(mock_positioner_with_actuator.readback, 0.0)
    set_mock_value(mock_positioner_with_actuator.setpoint, 0.0)

    yield mock_positioner_with_actuator


async def test_positioner_with_actuator(mock_positioner_with_actuator):
    async def before_set_func():
        await assert_value(mock_positioner_with_actuator.actuate, 0.0)

    async def after_set_func(s):
        await assert_value(
            mock_positioner_with_actuator.actuate,
            mock_positioner_with_actuator.actuate_value,
        )

    await _test_positioner_movement(
        mock_positioner_with_actuator, before_set_func, after_set_func
    )


class _MockPositionerWithDone(BasePositioner, EpicsDevice):
    readback: A[SignalR[float], Pv("Readback"), Format.HINTED_SIGNAL]
    setpoint: A[SignalRW[float], Pv("Setpoint")]

    done: A[SignalRW[float], Pv("Done")]
    done_value = 1.5


@pytest.fixture
async def mock_positioner_with_done():
    async with init_devices(mock=True):
        mock_positioner_with_done = _MockPositionerWithDone("PV:TEST:")

    set_mock_value(mock_positioner_with_done.readback, 0.0)
    set_mock_value(mock_positioner_with_done.setpoint, 0.0)

    yield mock_positioner_with_done


async def test_positioner_with_done(mock_positioner_with_done):
    async def before_set_func():
        await assert_value(mock_positioner_with_done.done, 0.0)

    async def before_end_func(s):
        assert not s.done

        set_mock_value(
            mock_positioner_with_done.done, mock_positioner_with_done.done_value
        )

    await _test_positioner_movement(
        mock_positioner_with_done, before_set_func, None, before_end_func
    )

    await assert_value(
        mock_positioner_with_done.done, mock_positioner_with_done.done_value
    )
