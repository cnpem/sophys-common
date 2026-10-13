# numpydoc ignore=GL08

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import logging
from logging import NullHandler, Formatter
from logging.config import dictConfig as config_logging_dict

import json


__all__ = ["LoggingLevels", "JSONFormatter", "configure_json_logging"]


@dataclass
class LoggingLevels:
    """Container for defining logging levels for various modules."""

    MODULE_LEVEL: int = logging.INFO

    OPHYD_LEVEL: int = logging.WARNING
    BLUESKY_LEVEL: int = logging.WARNING

    QUEUESERVER_LEVEL: int = logging.WARNING


class JSONFormatter(Formatter):
    """Formatter class for formatting message into JSON strings."""

    INCLUDED_RECORD_FIELDS = ("name", "levelname", "msg")

    def format(self, record: logging.LogRecord):
        """
        Format a logging.LogRecord object into a JSON string.

        Parameters
        ----------
        record : logging.LogRecord
            The message object to format.
        """
        data = {name: getattr(record, name) for name in self.INCLUDED_RECORD_FIELDS}
        if "msg" in self.INCLUDED_RECORD_FIELDS:
            data["msg"] = super().format(record)

        return json.dumps(data, separators=(", ", ": "))


def configure_json_logging(
    module_names: Sequence[str], levels: LoggingLevels | None = None
):
    """
    Configure the logging module to output JSON-formatted text to sys.stdout.

    Parameters
    ----------
    module_names : sequence of str
        Custom module names to setup logging for. Usually contains 'sophys.xxx'.
    levels : LoggingLevels, optional
        Level configuration for each different module.
    """
    if levels is None:
        levels = LoggingLevels()

    configuration: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {"json": {"()": "sophys.common.utils.logging.JSONFormatter"}},
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "ophyd": {
                "handlers": ["stream"],
                "level": levels.OPHYD_LEVEL,
            },
            "bluesky": {
                "handlers": ["stream"],
                "level": levels.BLUESKY_LEVEL,
            },
            "bluesky_queueserver": {
                "handlers": ["stream"],
                "level": levels.QUEUESERVER_LEVEL,
            },
        },
    }

    for module_name in module_names:
        configuration["loggers"][module_name] = {
            "handlers": ["stream"],
            "level": levels.MODULE_LEVEL,
        }

    config_logging_dict(configuration)

    logging.lastResort = NullHandler()
