from itertools import chain
import logging
from contextlib import contextmanager
import functools
import re
import threading
import typing


__global_registries = dict()
__global_registry_names = dict()
__auto_register = threading.local()


def in_autoregister_context() -> bool:
    """Returns whether the current execution context is auto registering new devices to a registry."""
    return hasattr(__auto_register, "val") and __auto_register.val is not None


def get_named_registry(registry_name: str, create_if_missing: bool = False):
    """
    Get the instance of ophyd-registry's Registry associated with ``register_name``.

    If ``create_if_missing`` is ``True``, create a new Registry for that name if it is missing, otherwise raise a ``RuntimeError``.
    """
    global __global_registries

    if registry_name not in __global_registries:
        if create_if_missing:
            return create_named_registry(registry_name)
        else:
            raise RuntimeError(
                "There are no registries named '{}'. Available registries:\n {}".format(
                    registry_name, ", ".join(__global_registries.keys())
                )
            )

    return __global_registries.get(registry_name)


def create_named_registry(registry_name: str):
    """
    Create a new Registry associated with ``registry_name``, clearing an existing one if it does.

    The created instance has ``auto_registrer`` set to ``False``, so you must explicitly register devices to it.
    Check :func:`register_devices` for some convenience.

    Returns the created / cleared Registry instance.
    """
    try:
        from ophydregistry import Registry
    except ImportError:
        logging.error("Package 'ophyd-registry' is missing.")
        return

    global __global_registries
    global __global_registry_names
    if len(__global_registries) == 0:

        def instantiation_callback(obj):
            if in_autoregister_context():
                get_named_registry(__auto_register.val).register(obj)

        from ophyd import ophydobj

        ophydobj.OphydObject.add_instantiation_callback(
            instantiation_callback, fail_if_late=False
        )

    try:
        registry = get_named_registry(registry_name, create_if_missing=False)
        registry.clear()
        return registry
    except RuntimeError:
        registry = Registry(auto_register=False)
        __global_registries[registry_name] = registry
        __global_registry_names[registry] = registry_name
        return registry


def get_registry_name(registry):
    """Return the name associated with this registry."""
    global __global_registry_names
    return __global_registry_names[registry]


def get_all_registries():
    """Return all the Registry instances currently instantiated."""
    global __global_registries
    return __global_registries.values()


def get_all_root_devices(as_dict: bool = False, use_registry_name: bool = True):
    """
    Return all the root devices from all the registries currently instantiated.

    Parameters
    ----------
    as_dict : bool, optional
        If True, return a dictionary, as per :func:`to_variable_dict`.
        Otherwise, return a list of all root devices. Defaults to False.
    """
    registries = get_all_registries()

    if as_dict:
        return to_variable_dict(registries, use_registry_name)

    return list(chain.from_iterable(v.root_devices for v in registries))


def get_all_devices(
    as_dict: bool = False,
    include_components: bool = False,
    use_registry_name: bool = True,
    use_dotted_name: bool = True,
):
    """
    Return all the devices from all the registries currently instantiated.

    Parameters
    ----------
    as_dict : bool, optional
        If True, return a dictionary, as per :func:`to_variable_dict`.
        Otherwise, return a list of all devices. Defaults to False.
    include_components : bool, optional
        If True, return all registered devices and components.
    use_registry_name : bool, optional
        If True, prepend the containing registry name to the device's
        name in the dict key. Defaults to True.
    use_dotted_name : bool, optional
        If True, use the dotted name, with hierarchical information,
        in the dict key. Otherwise, use `name`. Defaults to True.
    """
    root_devices = get_all_root_devices(True, use_registry_name)
    devices = root_devices.copy()

    for key, dev in root_devices.items():
        devices[key] = dev

        it = []
        if include_components and hasattr(dev, "_signals"):
            it = dev._signals.items()
        elif hasattr(dev, "walk_subdevices"):
            it = dev.walk_subdevices(include_lazy=True)

        for child_dotted_name, child in it:
            pattern = re.compile("[^a-zA-Z0-9_]")
            clear_name = functools.partial(re.sub, pattern, "_")

            name = clear_name(child_dotted_name if use_dotted_name else child.name)
            if use_registry_name:
                name = key + "_" + name

            devices[name] = child

    if not as_dict:
        return list(chain.from_iterable(devices.values()))
    return devices


def find_all(
    any_of: typing.Optional[str] = None,
    *,
    label: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    allow_none: typing.Optional[bool] = False,
):
    res = list(
        chain.from_iterable(
            i.findall(any_of=any_of, label=label, name=name, allow_none=True)
            for i in get_all_registries()
        )
    )

    if len(res) == 0 and not allow_none:
        from ophydregistry.exceptions import ComponentNotFound

        raise ComponentNotFound(
            'Could not find components matching: label="{}", name="{}"'.format(
                label or any_of, name or any_of
            )
        )

    return res


def remove_all_named(name: str):
    """Remove all devices with a given name from all registries."""
    registries = get_all_registries()

    for reg in registries:
        devs = reg.findall(name=name, allow_none=True)

        for dev in devs:
            reg.pop(dev)


@contextmanager
def register_devices(registry_name: str):
    """
    Context Manager for registering instantiated devices inside it to ``registry_name``.

    For instance, to register devices ``a`` and ``b`` to registry ``beamline_a``,
    and devices ``c``, ``d``, and ``e`` to registry ``beamline_b``, you could do something like:

    .. code-block:: python

        # ...

        with register_devices("beamline_a"):
            DeviceAClass(name="a")
            DeviceBClass(name="b")

        with register_devices("beamline_b"):
            DeviceCClass(name="c")
            DeviceDClass(name="d")
            DeviceEClass(name="e")
    """
    _ = get_named_registry(
        registry_name, True
    )  # Ensure the registry exists without clearing it if it does.

    __auto_register.val = registry_name
    yield
    __auto_register.val = None


def to_variable_dict(registries: typing.Iterable, use_registry_name: bool = True):
    """
    Turns a registry (or set of registries) into a dictionary, intended of being used as such:

    - ``globals().update(<return value>)``
    - ``locals().update(<return value>)``
    """

    def process_name(registry, name: str, use_registry_name: bool = True):
        pattern = re.compile("[^a-zA-Z0-9_]")
        clear_name = functools.partial(re.sub, pattern, "_")

        device_name = clear_name(name)
        registry_name = clear_name(get_registry_name(registry))

        if use_registry_name:
            return "{}_{}".format(registry_name, device_name)
        return device_name

    ret = {}
    for registry in registries:
        ret.update(
            {
                process_name(registry, d.name, use_registry_name): d
                for d in registry.root_devices
            }
        )

    return ret


try:
    from ophydregistry.registry import Registry
except ImportError:
    pass
else:
    find_all.__doc__ = Registry.findall.__doc__
