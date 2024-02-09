from dataclasses import dataclass, fields
from io import IOBase
import sys
from typing import Union

import numpy as np

from bluesky import RunEngine

from ophyd import EpicsSignal
from ophyd.utils.epics_pvs import _wait_for_value
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass


class EpicsSignalWithCustomReadout(EpicsSignal):
    """
    An EpicsSignal subclass extending the validation of the result of a 'set' operation.

    This is useful in cases where the readout of a particular 'set' is different from the
    value you set, like when making a command to an IOC, and expecting a "Done" string in return.

    Parameters
    ----------
    enforce_type : type, optional
        Whether to try to apply a type conversion to the readout value.
        If not set, defaults to not trying any type conversion (the default EpicsSignal behavior).
    """

    def __init__(self, read_pv, write_pv, enforce_type=None, **kwargs):
        super(EpicsSignalWithCustomReadout, self).__init__(
            read_pv=read_pv, write_pv=write_pv, **kwargs
        )

        self._expected_readout = None
        self._enforce_type = enforce_type

    # FIXME: Use the default value for timeout
    def set(self, value, *, expected_readout=None, timeout=5.0, settle_time=None):
        """
        Set the value of the Signal and return a Status object.

        If put completion is used for this EpicsSignal, the status object will
        complete once EPICS reports the put has completed.

        Otherwise the readback will be polled until equal to 'expected_readout',
        and if 'enforce_type' was set in the constructor, both of the values will
        be cast to that type, raising an Exception if the conversion is not possible.

        Parameters
        ----------
        value : any
        expected_readout : any, optional
            Expected value of the 'read_pv' after successfully setting the value.
            If not set, defaults to 'value'.
        timeout : float, optional
            Maximum time to wait.
        settle_time: float, optional
            Delay after the set() has completed to indicate completion
            to the caller

        Returns
        -------
        st : Status

        See Also
        --------
        EpicsSignal.set
        """
        self._expected_readout = (
            expected_readout if expected_readout is not None else value
        )
        if self._enforce_type is not None:
            self._expected_readout = create_loose_comparator(
                self._enforce_type, self._expected_readout
            )

        return super(EpicsSignalWithCustomReadout, self).set(
            value=value, timeout=timeout, settle_time=settle_time
        )

    def _set_and_wait(self, value, timeout, **kwargs):
        self.put(value, **kwargs)

        if is_loose_comparator(self._expected_readout) and (
            self.tolerance or self.rtolerance
        ):
            self._expected_readout.atol = self.tolerance
            self._expected_readout.rtol = self.rtolerance

            self.tolerance = None
            self.rtolerance = None

        _wait_for_value(
            self,
            self._expected_readout,
            poll_time=0.01,
            timeout=timeout,
            atol=self.tolerance,
            rtol=self.rtolerance,
        )


class EpicsSignalWithCustomReadoutRBV(EpicsSignalWithCustomReadout):
    """An EpicsSignalWithCustomReadout subclass setting the read_pv to 'write_pv + _RBV' by default."""

    def __init__(self, write_pv, **kwargs):
        super().__init__(read_pv=write_pv + "_RBV", write_pv=write_pv, **kwargs)


def create_loose_comparator(common_type, readout):
    ret = _LooseComparator(common_type)()
    ret._value = readout
    return ret


def is_loose_comparator(obj):
    return hasattr(obj, "_loose_comparator")


class _LooseComparator:
    """
    An object that will try to cast itself and other values to a common type in a comparison.
    The common type must be a numerical type, otherwise the behavior is undefined.

    For example, this can be used to automatically cast string variables into float for numerical comparisons.
    """

    class _WrapperObjectMetaclass(type):
        def __new__(cls, class_name, class_parents, class_attrs, common_type=object):
            if "_value" not in class_attrs:
                class_attrs["_value"] = None

            def repr(self):
                return "Wrapper object: Value={}, Common type={}".format(
                    self._value, common_type
                )

            class_attrs["__repr__"] = repr

            # fmt: off
            binary_attrs_list = [
                "__lt__", "__le__", "__gt__", "__ge__",
                "__add__", "__sub__", "__mul__", "__matmul__", "__truediv__", "__floordiv__", "__mod__", "__divmod__", "__pow__", "__lshift__", "__rshift__", "__and__", "__xor__", "__or__",
                "__radd__", "__rsub__", "__rmul__", "__rmatmul__", "__rtruediv__", "__rfloordiv__", "__rmod__", "__rdivmod__", "__rpow__", "__rlshift__", "__rrshift__", "__rand__", "__rxor__", "__ror__",
                "__iadd__", "__isub__", "__imul__", "__imatmul__", "__itruediv__", "__ifloordiv__", "__imod__", "__ipow__", "__ilshift__", "__irshift__", "__iand__", "__ixor__", "__ior__",
            ]
            # fmt: on

            def create_binary_attr_impl(attr):
                def attrs_impl(self, other):
                    # Calls 'common_type(self) <attr> common_type(other)'
                    return getattr(common_type(self._value), attr)(common_type(other))

                return attrs_impl

            # Special case for __eq__ and __ne__ to deal with tolerance
            def eq_close(self, other):
                atol = getattr(self, "atol", 0) or 0
                rtol = getattr(self, "rtol", 0) or 0

                a = common_type(self._value)
                b = common_type(other)

                return np.isclose(a, b, atol=atol, rtol=rtol)

            def ne_close(self, other):
                return not eq_close(self, other)

            class_attrs["__eq__"] = eq_close
            class_attrs["__ne__"] = ne_close

            class_attrs.update(
                {attr: create_binary_attr_impl(attr) for attr in binary_attrs_list}
            )

            return super().__new__(cls, class_name, class_parents, class_attrs)

    def __init__(self, common_type):
        class _WrapperObject(
            metaclass=_LooseComparator._WrapperObjectMetaclass, common_type=common_type
        ):
            _loose_comparator = None

        self.__inner_cls = _WrapperObject

    def __call__(self, arg=None):
        ret = self.__inner_cls()
        ret._value = arg
        return ret


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
