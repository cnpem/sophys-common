Detectors
=========

C400
----

.. tags:: AreaDetector

.. automodule:: sophys.common.devices.c400
    :members: C400ROIs
    :show-inheritance:

    .. autoclass:: C400
        :members: __init__
        :show-inheritance:

        .. autosummary::
            :toctree: _generated
            :template: device_attr_list.rst

            C400Cam

.. rubric:: Old C400 (Deprecated)

.. raw:: html

    <div title="Derived directly from Ophyd's Device.">
.. tags:: Standalone
.. raw:: html

    </div>

.. autoclass:: OldC400
    :show-inheritance:
    :no-index:

    .. container:: hidden

        .. autosummary::
            :toctree: _generated
            :template: device_attr_list_embed.rst

            sophys.common.devices.c400.OldC400

    .. include:: _generated/sophys.common.devices.c400.OldC400.rst

----

Mobipix
-------

.. tags:: AreaDetector

.. automodule:: sophys.common.devices.mobipix
    :members: MobipixCam, MobipixBackend, MobipixDetector, MobipixError, MobipixMissingConfigurationError
    :show-inheritance:

    .. autoclass:: Mobipix
        :members: __init__
        :show-inheritance:

    .. autoclass:: MobipixEnergyThresholdSetter
        :members: __init__, read
        :show-inheritance:

        .. autoattribute:: nrg

        .. autoproperty:: low_threshold_adjust

        .. autoproperty:: high_threshold_adjust

----

Pilatus 300K
------------

.. tags:: AreaDetector

.. automodule:: sophys.common.devices.pilatus_300k
    :members:
    :show-inheritance:

----

Pimega
------

.. tags:: AreaDetector

.. automodule:: sophys.common.devices.pimega

    .. autoclass:: Pimega
        :members: __init__
        :show-inheritance:

        .. autosummary::
            :toctree: _generated
            :template: device_attr_list.rst

            PimegaCam

----

Vortex / Xspress
----------------

.. tags:: AreaDetector

.. automodule:: sophys.common.devices.xspress
    :members:
    :show-inheritance:
