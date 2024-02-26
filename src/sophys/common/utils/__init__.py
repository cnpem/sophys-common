from dataclasses import dataclass, fields
from io import IOBase
import sys
from typing import Union

from bluesky import RunEngine

from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite

from .callbacks import *  # noqa: F403
from .registry import *  # noqa: F403
from .signals import *  # noqa: F403


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass


@dataclass
class DebugOptions:
    file: Union[IOBase, str, None] = sys.stdout
    datefmt: str = "%H:%M:%S"
    color: bool = True
    level: Union[str, int] = "DEBUG"

    def asdict(self):
        # https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict
        # Workaround for deepcopy failing on IOBase subclasses
        return dict((field.name, getattr(self, field.name)) for field in fields(self))

    @staticmethod
    def no_debug():
        return DebugOptions(level="INFO")


def set_debug_mode(
    run_engine: RunEngine,
    bluesky_debug: DebugOptions = DebugOptions(),
    ophyd_debug: DebugOptions = DebugOptions(),
    mock_commands: bool = True,
    print_documents: bool = False,
) -> dict:
    """
    Enables / disables debugging facilities for bluesky / ophyd.

    Parameters
    ----------
    run_engine : RunEngine
        The RunEngine on which to set the debug options.
        Note that the bluesky and ophyd debug options are global, so they affect all RunEngines.
    bluesky_debug : DebugOptions, optional
        Options to pass to bluesky's logging configuration. Passing None will leave the configurations unchanged.
    ophyd_debug : DebugOptions, optional
        Options to pass to ophyd's logging configuration. Passing None will leave the configurations unchanged.
    mock_commands : bool, optional
        Whether to mock all of 'run_engine's commands, replacing the default commands for dummy ones
        that only print to stdout what it would have done. Defaults to True.

        If it is set, the return's "old_commands" key will be set to a dictionary, in which
        each command name (key) will be associated with the old command function (value).
    print_documents : bool, optional
        Whether to subscribe 'run_engine' to a callback that prints every document generated. Defaults to False.

        If it is set, the return's "print_sub_id" key will be set to the subscription ID returned by the RunEngine.
    """
    return_dict = {}

    from bluesky.log import config_bluesky_logging
    from ophyd.log import config_ophyd_logging

    if bluesky_debug is not None:
        config_bluesky_logging(**bluesky_debug.asdict())
    if ophyd_debug is not None:
        config_ophyd_logging(**ophyd_debug.asdict())

    if mock_commands:

        def mock_command(command):
            async def __inner(msg):
                print(" --- {}: {}".format(command, msg))
                if msg.obj is not None:
                    return {msg.obj: None}

            __inner.__doc__ = "RunEngine '{}' mock implementation.".format(command)
            return __inner

        return_dict["old_commands"] = dict()
        for command in run_engine.commands:
            return_dict["old_commands"][command] = run_engine._command_registry[command]
            run_engine.register_command(command, mock_command(command))

    if print_documents:

        def pretty_doc_print(name, doc):
            if name == "start":
                print()
            print("[{}] - {}".format(name, str(doc)))

        return_dict["print_sub_id"] = run_engine.subscribe(pretty_doc_print)

    return return_dict


def is_in_queueserver() -> bool:
    """
    Returns whether the current code is running in a queueserver environment (e.g. in the startup sequence), or not.

    This is very similar to queueserver's :func:`bluesky_queueserver.is_re_worker_active`, but without a hard dependency on queueserver.
    """
    try:
        from bluesky_queueserver import is_re_worker_active
    except ImportError:
        is_re_worker_active = lambda: False  # noqa: E731

    return is_re_worker_active()
