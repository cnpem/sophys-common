Miscellaneous devices
=====================

CompactRIO
----------

NI-9215
~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.crio.CRIO_9215

.. include:: _generated/sophys.common.devices.crio.CRIO_9215.rst

NI-9220
~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.crio.CRIO_9220

.. include:: _generated/sophys.common.devices.crio.CRIO_9220.rst

NI-9223
~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.crio.CRIO_9223

.. include:: _generated/sophys.common.devices.crio.CRIO_9223.rst

NI-9403
~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.crio.CRIO_9403

.. include:: _generated/sophys.common.devices.crio.CRIO_9403.rst

Storage Ring
------------

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.storage_ring.StorageRing

.. include:: _generated/sophys.common.devices.storage_ring.StorageRing.rst

VPU
---

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.vpu.VPU

.. include:: _generated/sophys.common.devices.vpu.VPU.rst

DCM Lite
--------

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.dcm_lite.DcmLite
        sophys.common.devices.dcm_lite.Goniometer
        sophys.common.devices.dcm_lite.ShortStroke

DcmLite
~~~~~~~

.. include:: _generated/sophys.common.devices.dcm_lite.DcmLite.rst

Goniometer
~~~~~~~~~~

.. tags:: Motor

.. include:: _generated/sophys.common.devices.dcm_lite.Goniometer.rst

ShortStroke
~~~~~~~~~~~

.. tags:: Motor

.. include:: _generated/sophys.common.devices.dcm_lite.ShortStroke.rst

HVPS
----------

High Voltage Power Supply (HVPS)
~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.hvps.HVPS

.. include:: _generated/sophys.common.devices.hvps.HVPS.rst

PMT
---

Photomultiplier
~~~~~~~~~~~~~~~

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.pmt.Photomultiplier

.. include:: _generated/sophys.common.devices.pmt.Photomultiplier.rst

Simulated devices
-----------------

We have also implemented a factory function to create some simulated devices, mainly for testing and development usage. It is the :py:func:`instantiate_sim_devices` function, importable from :py:mod:`sophys.common.devices`.

It is inspired by the :py:mod:`ophyd.sim` module, but with some trimming down and fixes for our specific requirements.

Example usage:


.. code-block:: python

    from sophys.common.devices import instantiate_sim_devices

    hw = instantiate_sim_devices()

    from bluesky import RunEngine
    from bluesky.plans import scan

    RE = RunEngine()
    RE(scan([hw.det, hw.rand], hw.motor, -2, 2, 25))
    