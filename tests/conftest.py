import pytest

from .soft_ioc import start_soft_ioc


@pytest.fixture(scope="session")
def soft_ioc():
    soft_ioc_prefix, stop_soft_ioc = start_soft_ioc()
    yield soft_ioc_prefix
    stop_soft_ioc()
