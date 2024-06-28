Controller devices
==================

ERAS - Ethernet Range Selector
------------------------------

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.eras.ERAS

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.eras.Channel

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.eras.Scale

.. include:: _generated/sophys.common.devices.eras.ERAS.rst

Channels are accessible via `self.channel_{x}`, for `x` in {1, 2, 3, 4}.

    .. include:: _generated/sophys.common.devices.eras.Channel.rst

    Each channel has `n` scales, with `n` given by the value of `num_scales` at the device initialization.

        .. include:: _generated/sophys.common.devices.eras.Scale.rst


TATU - Timing and Trigger Unit 
------------------------------

.. container:: hidden

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.TatuInput

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.TatuOutputCondition

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.TatuOutput

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.TatuBase

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.Tatu9401

    .. autosummary::
        :toctree: _generated
        :template: device_attr_list_embed.rst

        sophys.common.devices.tatu.Tatu9403

.. include:: _generated/sophys.common.devices.tatu.Tatu9401.rst

.. include:: _generated/sophys.common.devices.tatu.Tatu9403.rst

Each input and output are themselves Ophyd devices with some specific signals:

    .. include:: _generated/sophys.common.devices.tatu.TatuInput.rst

    .. include:: _generated/sophys.common.devices.tatu.TatuOutput.rst

    Each output condition, in turn, has its own signals:

        .. include:: _generated/sophys.common.devices.tatu.TatuOutputCondition.rst
