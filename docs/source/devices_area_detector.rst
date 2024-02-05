AreaDetector devices
====================

C400
----

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

----

Mobipix
-------

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

.. automodule:: sophys.common.devices.pilatus_300k
    :members:
    :show-inheritance:

----

Vortex
------

.. automodule:: sophys.common.devices.vortex
    :members:
    :show-inheritance:
