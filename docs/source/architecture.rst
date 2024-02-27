Package organization
====================

This document explains how the bluesky / ophyd packages are to be organized for beamline usage at LNLS. The proposed structure is intended to make things as simple to use and maintains as possible, while providing enough flexibility for the experiments needs.

Below is a high-level schematic showing how the ``sophys-...`` packages are structured:

.. image:: /images/sophys_package_organization.png

sophys-common
-------------

There is a general package, ``sophys-common``, that hosts reusable pieces of code and functionality for usage in each beamline, and that is managed by `the SwC group <http://swc.lnls.br/>`_ (and can be contributed to by anyone who wants to! 🙂). To view the documentation, congratulations! You're reading it right now 😃.

This ``sophys-common`` package has the ``sophys.common`` import prefix, which means that everything from the package is accessible in Python via ``import sophys.common.(...)``, as is the case with the other ``sophys`` packages.

The contents of this package can be summarized as the following:

- Ophyd definitions for common devices in multiple beamlines.

- Bluesky plans for common / general procedures in many beamlines.

- Utilitary functionality not normally provided by other packages, but that are useful to have.

- Usage examples and documentation for helping out people using ophyd and bluesky at LNLS.

sophys-<beamline>
-----------------

There are also separate repositories for each beamline. That contains everything bluesky / ophyd related that does not belong to the general ``sophys-common`` package, like instantiation of the devices of that beamline, definition of devices specific to that beamline only, or plans heavily tied to the experiment type made only in that beamline.

Those repositories are generally to be administrated by the beamline staff, when they have a person dedicated to doing computer stuff, but the SwC group makes itself available to help out whenever needed.

The contents of those packages can be summarized as the following:

- Ophyd definitions for devices unique to the beamline.

- Bluesky plans for procedures exclusive to the beamline, or not flexible enough to be generalized.

- Utilities related to the specific applications in the package (e.g. functionality common to many plans).

- Device instantiations for actual hardware running on the beamline (See :ref:`device-instantiation` for more details).

.. _device-instantiation:

Device instantiation
^^^^^^^^^^^^^^^^^^^^

Ophyd device definitions are useless unless we make actual use of them. As with any other Python class, the way to do that is to instantiate an object of that class, and additionally in this particular context, put that instance in a place where other tools can find it later.

In order to keep things as simple and organized as possible, we decided that having a stardard function in ``sophys.xxx.devices.__init__.py`` to create and register all devices would be good. That allows us to branch out the instantiation into other functions / files, as the developer sees fit. That function obeys the following signature:

.. code-block:: python

    def instantiate_devices() -> dict[str, ophyd.Device]:
        ...

This function will then be called by someone to instantiate and register the devices. For instance, in queueserver, the startup code will call this function, and use the return dict to register the devices internally.

.. note::

    To access the instantiated devices at a later point, say from an arbitrary location in your code, using the straightforward approach can be annoying, since you must pass the reference to those instances along all the way.

    In order to make things a little better, you can instead register them in a globally accessible registry, using the `ophyd-registry <https://pypi.org/project/ophyd-registry/>`_ package. ``sophys-common`` has some auxiliary methods for interacting with those registries `you can check out <http://sol.gitpages.cnpem.br/bluesky/sophys-common/utils.html#registry>`_.

    It is recommended to use registries whenever possible, as they keep things a bit more tidy and organized.

.. hint::

    Below is an example usage of ``ophyd-registry`` to register and retrieve devices:

    .. code-block:: python

        # sophys.xxx.devices.__init__.py

        from sophys.common.utils.registry import register_devices, get_all_devices

        from sophys.xxx.devices import DeviceX, DeviceY

        def instantiate_devices():
            with register_devices("XXX"):
                DeviceX("XXX:A:DeviceX", name="DeviceX - Hut A")
                DeviceX("XXX:B:DeviceX", name="DeviceX - Hut B")
                DeviceX("XXX:A:DeviceY", name="DeviceY - Hut A")

            return get_all_devices(True)

        # ...

        # In some other place...
    
        # Get a specific device
        from sophys.common.utils.registry import get_named_registry
        xxx_registry = get_named_registry("XXX")
        x_a = xxx_registry.find("DeviceX - Hut A")
        # ... or
        from sophys.common.utils.registry import find_all
        x_a = find_all("DeviceX - Hut A")[0]

        # Get all devices
        from sophys.common.utils.registry import get_all_devices
        all_devices = get_all_devices(True)


    Below is the same example, without using ``ophyd-registry`` (assuming the caller of ``instantiate_devices`` added the devices to ``globals()``):

    .. code-block:: python

        # sophys.xxx.devices.__init__.py

        from sophys.xxx.devices import DeviceX, DeviceY

        def instantiate_devices():
            devices = {
                "devicex_a": DeviceX("XXX:A:DeviceX", name="DeviceX - Hut A"),
                "devicex_b": DeviceX("XXX:B:DeviceX", name="DeviceX - Hut B"),
                "devicey_a": DeviceX("XXX:A:DeviceY", name="DeviceY - Hut A"),
            }

            return devices

        # ...

        # In some other place...

        # Get a specific device
        x_a = devicex_a

        # Get all devices
        from ophyd import Device
        all_devices = {k: v for k, v in globals().items() if isinstance(v, Device)}

Namespace packages
------------------

All the sophys packages are structured in a special way, named a ``namespace package``. This is a standard feature of Python, that allows us to share the ``sophys.`` import prefix along many independent packages. So, we can have both ``sophys-common`` and ``sophys-xxx`` share the same ``from sophys.(...) import (...)``.

This is why all the packages have a ``src`` folder, inside of which they have a ``sophys`` folder, **without a** ``__init__.py`` **file in it**, and inside of that goes the specific code for that package.

You can read more about namespace packages in `the Packaging Python User Guide <https://packaging.python.org/en/latest/guides/packaging-namespace-packages/>`_, in `the PEP that introduced it <https://peps.python.org/pep-0420/>`_, and in `the setuptools user guide about it <https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#finding-namespace-packages>`_, if you want to learn more. Overall, it's a neat little eye candy, and also helps us standarize the package organization across repositories!
