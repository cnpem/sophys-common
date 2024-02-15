from itertools import chain
import logging
from contextlib import contextmanager
import threading
import typing


__global_registries = dict()
__auto_register = threading.local()


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
        logging.error("Package 'ophydregistry' is missing.")
        return

    global __global_registries
    if len(__global_registries) == 0:

        def instantiation_callback(obj):
            if __auto_register.val is not None:
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
        __global_registries[registry_name] = Registry(auto_register=False)
        return __global_registries[registry_name]


def get_all_registries():
    """Return all the Registry instances currently instantiated."""
    global __global_registries
    return __global_registries.values()


def get_all_devices():
    """Return all the root devices from all the registries currently instantiated."""
    global __global_registries
    return list(
        chain.from_iterable(v.root_devices for v in __global_registries.values())
    )


def find_all(
    any_of: typing.Optional[str] = None,
    *,
    label: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    allow_none: typing.Optional[bool] = False
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


try:
    from ophydregistry.registry import Registry
except ImportError:
    pass
else:
    find_all.__doc__ = Registry.findall.__doc__
