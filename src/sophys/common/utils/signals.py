import copy
import typing

import numpy as np

from ophyd import Device, Component, EpicsSignal, EpicsSignalRO
from ophyd.utils.epics_pvs import _wait_for_value


def add_components_to_device(
    obj: Device,
    components: typing.Iterable[tuple[str, Component]],
    *,
    for_each_sig: typing.Optional[typing.Callable] = None,
):
    """
    Add a collection of components to a device, after it has been initialized.

    Parameters
    ----------
    obj : Device
        The device to which the components will be added.
    components : iterable of (component name, component) tuples
        The components that will be added to `obj`.
    for_each_sig : callable, optional
        Callback that is called on each signal addition, with signature (name: str, sig: Signal) -> Any.

        By default, it does nothing.

        One common usage is to call setattr of the signal to its parent.

    Examples
    --------
    Add four signals named ``channel_{x}`` to ``obj``, each with prefix ``CH{x}``:

    .. code-block:: python

        components = (
            (
                f"channel_{i}",
                Component(EpicsSignal, f"CH{i}:"),
            )
            for i in range(1, 5)
        )
        add_components_to_device(
            obj, components, for_each_sig=lambda name, sig: setattr(self, name, sig)
        )

    Add an arbitrary number of signals named ``scale_{x}`` to ``obj``,
    each with prefix ``SC{x}``, while also adding them to a list ``scales``:

    .. code-block:: python

        def for_each_sig(name, sig):
            setattr(self, name, sig)
            self.scales.append(sig)

        n_scales = 8
        components = (
            (f"scale_{i}", Component(Scale, f"SC{i}:")) for i in range(n_scales)
        )
        add_components_to_device(self, components, for_each_sig=for_each_sig)
    """
    if not hasattr(obj.__class__, "_old_sig_attrs"):
        obj.__class__._old_sig_attrs = copy.deepcopy(obj._sig_attrs)
    obj._sig_attrs = copy.deepcopy(obj.__class__._old_sig_attrs)

    for component_name, component in components:
        component.__set_name__(component, component_name)

        obj._sig_attrs[component_name] = component
        obj._component_kinds[component_name] = component.kind
        obj._instantiate_component(component_name)

        if for_each_sig is not None:
            for_each_sig(name=component_name, sig=obj._signals[component_name])


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


class EpicsSignalMon(EpicsSignalRO):
    def __init__(self, prefix, **kwargs):
        super().__init__(prefix + "-Mon", **kwargs)


class EpicsSignalWithRBSP(EpicsSignal):
    """
    A simple Signal with a similar logic of EpicsSignalWithRBV, but
    pvname is -RB and write_pv is -SP.
    """

    def __init__(self, prefix, **kwargs):
        super().__init__(prefix + "-RB", write_pv=prefix + "-SP", **kwargs)


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
