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
    warmup_acquire_time: float = 1.0
    warmup_acquire_period: float = 1.0
    warmup_signal_timeout: float = 5.0

    def __init__(
        self,
        prefix: str,
        *,
        override_path: bool = False,
        write_path_template="/tmp",
        read_attrs=[],
        **kwargs,
    ):
        """
        A simple HDF5 plugin class, with some additional behavior (see Parameters and Attributes below).

        Parameters
        ----------
        prefix : str
            Prefix of this plugin (e.g. 'HDF1:')
        override_path : bool, optional
            Whether to use the common override logic of HDF5 ophyd plugins.
            By default, it is disabled (the currently configured PV values will be used)
        write_path_template : str, optional
            Used when `override_path` is `True`. By default it is `/tmp`.

        Attributes
        ----------
        warmup_acquire_time : float
            The value to set AcquireTime when doing a warmup. Defaults to 1.0.
        warmup_acquire_period : float
            The value to set AcquirePeriod when doing a warmup. Defaults to 1.0.
        warmup_signal_timeout : float
            The timeout to pass to each set().wait() call in the warmup. Defaults to 5.0.
        """
        super().__init__(
            prefix,
            write_path_template=write_path_template,
            read_attrs=read_attrs,
            **kwargs,
        )

        self._override_path = override_path

    def warmup(self):
        """
        A convenience method for 'priming' the plugin.

        The plugin has to 'see' one acquisition before it is ready to capture.
        This sets the array size, etc.

        This method is an override of the similar-named method in HDF5Plugin.
        """
        self.enable.set(1).wait()

        from collections import OrderedDict

        sigs = OrderedDict(
            [
                (self.parent.cam.array_callbacks, 1),
                (self.parent.cam.image_mode, "Single"),
                (self.parent.cam.trigger_mode, "Internal"),
                (self.parent.cam.acquire_time, self.warmup_acquire_time),
                (self.parent.cam.acquire_period, self.warmup_acquire_period),
                (self.parent.cam.acquire, 1),
            ]
        )

        original_vals = {sig: sig.get() for sig in sigs}

        for sig, val in sigs.items():
            sig.set(val).wait(timeout=self.warmup_signal_timeout)

        import time

        while self.parent.cam.acquire.get() != 0:
            time.sleep(0.01)

        for sig, val in reversed(list(original_vals.items())):
            sig.set(val).wait(timeout=self.warmup_signal_timeout)

    def stage(self):
        if not self._override_path:
            # stage_sigs will be ran after the override takes place.
            self.stage_sigs["file_path"] = self.hdf.file_path.get()
            self.stage_sigs["file_name"] = self.hdf.file_name.get()
            self.stage_sigs["file_number"] = self.hdf.file_number.get()

        super().stage()

    def unstage(self):
        if not self._override_path:
            # The super().unstage call will override our values to
            # the dumb defaults. Before that, however, we have the
            # updated values.
            file_path = self.file_path.get()
            file_name = self.file_name.get()
            file_number = self.file_number.get()

        super().unstage()

        if not self._override_path:
            self.file_path.set(file_path).wait()
            self.file_name.set(file_name).wait()
            self.file_number.set(file_number).wait()

class HDF5PluginWithFileStoreV34(HDF5PluginWithFileStore):
    file_number_sync = None
    file_number_write = None
    pool_max_buffers = None

@dataclass
class DebugOptions:
    file: Union[IOBase, str, None] = sys.stdout
    """Where to save the log."""
    datefmt: str = "%H:%M:%S"
    """What formatting to use for the date of an event."""
    color: bool = True
    """Whether to use colored output in the logs."""
    level: Union[str, int] = "DEBUG"
    """What is the minimum level of logging that will be processed."""

    def asdict(self):
        # https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict
        # Workaround for deepcopy failing on IOBase subclasses
        return dict((field.name, getattr(self, field.name)) for field in fields(self))

    @staticmethod
    def info_level():
        """Create a `DebugOptions` object with no `DEBUG` messages processed."""
        return DebugOptions(level="INFO")


def set_debug_mode(
    run_engine: RunEngine,
    bluesky_debug: Union[bool, DebugOptions, None] = None,
    ophyd_debug: Union[bool, DebugOptions, None] = None,
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
    bluesky_debug : DebugOptions or bool, optional
        Whether to enable / disable debug logging, or options to pass to bluesky's logging configuration.
        Passing None will leave the configurations unchanged.
    ophyd_debug : DebugOptions or bool, optional
        Whether to enable / disable debug logging, options to pass to ophyd's logging configuration.
        Passing None will leave the configurations unchanged.
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
        if bluesky_debug is True:
            bluesky_debug = DebugOptions()
        elif bluesky_debug is False:
            bluesky_debug = DebugOptions.info_level()

        config_bluesky_logging(**bluesky_debug.asdict())

    if ophyd_debug is not None:
        if ophyd_debug is True:
            ophyd_debug = DebugOptions()
        elif ophyd_debug is False:
            ophyd_debug = DebugOptions.info_level()

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
