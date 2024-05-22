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


