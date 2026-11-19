import pytest

import logging
import json
from typing import Literal
from uuid import uuid4

from sophys.common.utils.logging import LoggingLevels, configure_json_logging


MODULE_NAME = "sophys.tests.logging"


def assert_stream(capsys, expected: dict, stream: Literal["out", "err"] = "out"):
    _stream_output = getattr(capsys.readouterr(), stream) or "{}"

    try:
        got = json.loads(_stream_output)
    except json.decoder.JSONDecodeError as e:
        raise AssertionError(f"Failed to parse as JSON: {_stream_output}.") from e

    for key in sorted(set(got.keys()) | set(expected.keys())):
        assert key in got, f"Missing key '{key}' in stream: {got}"
        assert key in expected, f"Unexpected key '{key}' in stream: {got}"
        assert (
            got[key] == expected[key]
        ), f"Mismatch in value - Got: {got[key]}, Expected: {expected[key]}"


def verify_logger(logger: logging.Logger, configured_level: int, capsys):
    def expected_message(message: str, level: int) -> dict:
        return (
            {}
            if configured_level > level
            else {
                "name": logger.name,
                "levelname": logging.getLevelName(level),
                "msg": message,
            }
        )

    assert logger.getEffectiveLevel() == configured_level

    handler = logger.handlers[0] if len(logger.handlers) == 1 else logging.lastResort
    assert isinstance(handler, (logging.StreamHandler, logging.NullHandler))

    fn_with_level = (
        (getattr(logger, name.lower()), getattr(logging, name.upper()))
        for name in ("debug", "info", "warning", "error", "critical")
    )
    for log, level in fn_with_level:
        message = str(uuid4())
        log(message)
        handler.flush()
        assert_stream(capsys, expected_message(message, level))


@pytest.fixture(scope="session")
def ophyd_device():
    from sophys.common.devices.simulated import instantiate_sim_devices

    return instantiate_sim_devices().rand


def test_ophyd_logging_default(capsys):
    configure_json_logging([])

    from ophyd.log import logger as ophyd_logger

    verify_logger(ophyd_logger, logging.WARNING, capsys)


def test_bluesky_logging_default(capsys):
    configure_json_logging([])

    from bluesky.log import logger as bluesky_logger

    verify_logger(bluesky_logger, logging.WARNING, capsys)


def test_queueserver_logging_default(capsys):
    configure_json_logging([])

    pytest.importorskip("bluesky_queueserver")
    from bluesky_queueserver.manager.manager import logger as qs_logger

    verify_logger(qs_logger, logging.WARNING, capsys)


def test_module_logging_default(capsys):
    configure_json_logging([MODULE_NAME])

    module_logger = logging.getLogger(MODULE_NAME)
    verify_logger(module_logger, logging.INFO, capsys)


LOG_LEVELS_TO_TEST = (
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
)


@pytest.mark.parametrize(("log_level"), LOG_LEVELS_TO_TEST)
def test_ophyd_logging_custom(capsys, ophyd_device, log_level: int):
    configure_json_logging([], LoggingLevels(OPHYD_LEVEL=log_level))

    from ophyd.log import logger as ophyd_logger

    verify_logger(ophyd_logger, log_level, capsys)

    expected_run_min_messages = {
        logging.DEBUG: 4,
    }

    ophyd_device.set(0).wait()
    ophyd_device.put(1)

    messages = capsys.readouterr().out
    assert len(messages) >= expected_run_min_messages.get(log_level, 0)


@pytest.mark.parametrize(("log_level"), LOG_LEVELS_TO_TEST)
def test_bluesky_logging_custom(capsys, ophyd_device, log_level: int):
    configure_json_logging([], LoggingLevels(BLUESKY_LEVEL=log_level))

    from bluesky.log import logger as bluesky_logger

    verify_logger(bluesky_logger, log_level, capsys)

    expected_run_min_messages = {
        logging.DEBUG: 10,
        logging.INFO: 2,
    }

    from bluesky import RunEngine, plans as bp

    RE = RunEngine()
    RE(bp.count([ophyd_device], num=1))

    messages = capsys.readouterr().out
    assert len(messages) >= expected_run_min_messages.get(log_level, 0)


@pytest.mark.parametrize(("log_level"), LOG_LEVELS_TO_TEST)
def test_queueserver_logging_custom(capsys, log_level: int):
    configure_json_logging([], LoggingLevels(QUEUESERVER_LEVEL=log_level))

    pytest.importorskip("bluesky_queueserver")
    from bluesky_queueserver.manager.manager import logger as qs_logger

    verify_logger(qs_logger, log_level, capsys)


@pytest.mark.parametrize(("log_level"), LOG_LEVELS_TO_TEST)
def test_module_logging_custom(capsys, log_level: int):
    configure_json_logging([MODULE_NAME], LoggingLevels(MODULE_LEVEL=log_level))

    module_logger = logging.getLogger(MODULE_NAME)
    verify_logger(module_logger, log_level, capsys)
