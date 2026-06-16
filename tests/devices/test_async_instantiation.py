import sys

import pytest

from ophyd_async.core import init_devices, NotConnectedError
from ophyd_async.epics.motor import Motor

from sophys.common.utils.registry import register_async_devices, get_named_registry


@pytest.mark.timeout(0.5)
async def test_single_mock_instantiation():
    async with init_devices(mock=True, timeout=1.0):
        _ = Motor("SOMETHING:NON:EXISTENT")


@pytest.mark.timeout(0.5)
async def test_multiple_mock_instantiations():
    async with init_devices(mock=True, timeout=1.0):
        _1 = Motor("SOMETHING:NON:EXISTENT")
        _2 = Motor("SOMETHING:NON:EXISTENT")


@pytest.mark.timeout(1.5)
async def test_single_instantiation():
    with pytest.raises(NotConnectedError):
        async with init_devices(timeout=1.0):
            _ = Motor("SOMETHING:NON:EXISTENT")


@pytest.mark.timeout(2.5)
async def test_multiple_instantiations():
    with pytest.raises(NotConnectedError):
        async with init_devices(timeout=1.0):
            _1 = Motor("SOMETHING:NON:EXISTENT")
            _2 = Motor("SOMETHING:NON:EXISTENT")


@pytest.mark.timeout(1.5)
async def test_many_instantiations_parallel():
    with pytest.raises(NotConnectedError):
        async with init_devices(timeout=1.0):
            # NOTE: The try..except is there to generate an exception context we can use to retrieve the current stack frame
            try:
                raise ValueError
            except ValueError:
                _, _, tb = sys.exc_info()
                assert tb is not None
                current_frame = tb.tb_frame

                for x in range(100):
                    current_frame.f_locals[f"_{x}"] = Motor("SOMETHING:NON:EXISTENT")


@pytest.mark.timeout(1.5)
class TestRegistry:
    @pytest.fixture(autouse=True)
    def clean_registry_on_cleanup(self):
        yield
        get_named_registry("TEST", False).clear()

    async def test_registry_instantiation_with_timeout(self):
        with pytest.raises(NotConnectedError):
            async with register_async_devices("TEST", timeout=1.0, raise_on_error=True):
                _ = Motor("SOMETHING:NON:EXISTENT")

    async def test_registry_instantiation(self):
        async with register_async_devices(
            "TEST", timeout=1.0, mock=True, raise_on_error=True
        ):
            my_motor = Motor("SOMETHING:NON:EXISTENT")

        registry = get_named_registry("TEST")
        assert registry is not None
        assert registry.find(name="my_motor") is my_motor

    async def test_registry_instantiation_twice(self):
        async with register_async_devices(
            "TEST", timeout=1.0, mock=True, raise_on_error=True
        ):
            my_motor_1 = Motor("SOMETHING:NON:EXISTENT")
        async with register_async_devices(
            "TEST", timeout=1.0, mock=True, raise_on_error=True
        ):
            my_motor_2 = Motor("SOMETHING:NON:EXISTENT")

        registry = get_named_registry("TEST")
        assert registry is not None
        assert registry.find(name="my_motor_1") is my_motor_1
        assert registry.find(name="my_motor_2") is my_motor_2

    async def test_registry_instantiation_with_partial_timeout(self, soft_ioc):
        async with register_async_devices("TEST", timeout=1.0):
            my_motor_1 = Motor(soft_ioc + "SLIT:TOP")
            my_motor_2 = Motor("SOMETHING:NON:EXISTENT")
            # Just to check if the timeout time remains low
            _ = Motor("SOMETHING:NON:EXISTENT")

        registry = get_named_registry("TEST")
        assert registry is not None
        assert registry.find(name="my_motor_1") is my_motor_1
        assert registry.find(name="my_motor_2", allow_none=True) is not my_motor_2
        assert registry.find(name="my_motor_2", allow_none=True) is None

    async def test_registry_instantiation_with_partial_timeout_and_exc(self, soft_ioc):
        with pytest.raises(NotConnectedError):
            async with register_async_devices("TEST", timeout=1.0, raise_on_error=True):
                my_motor_1 = Motor(soft_ioc + "SLIT:TOP")
                my_motor_2 = Motor("SOMETHING:NON:EXISTENT")
                # Just to check if the timeout time remains low
                _ = Motor("SOMETHING:NON:EXISTENT")

        registry = get_named_registry("TEST")
        assert registry is not None
        assert registry.find(name="my_motor_1") is my_motor_1
        assert registry.find(name="my_motor_2", allow_none=True) is not my_motor_2
        assert registry.find(name="my_motor_2", allow_none=True) is None
