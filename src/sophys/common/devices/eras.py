from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
from ophyd.signal import DEFAULT_CONNECTION_TIMEOUT

from ..utils.signals import add_components_to_device


class Scale(Device):
    full_scale_label = Component(EpicsSignal, "GetFSLbl", write_pv="SetFSLbl")
    full_scale = Component(EpicsSignalRO, "GetFS")
    sensitivity_label = Component(EpicsSignal, "GetSTLbl", write_pv="SetSTLbl")
    sensitivity = Component(EpicsSignalRO, "GetST")


class Channel(Device):
    """A channel from ERAS.

    To control the currently selected scale, use `current_scale`.
    You can use `scales[x]` or `scale_x` to access any scale at any time.
    """

    channel_name = Component(EpicsSignal, "GetCdv", write_pv="SetCdv")
    selected_scale = Component(EpicsSignal, "GetRng", write_pv="SetRng")
    num_scales = Component(EpicsSignal, "GetNumScl", write_pv="SetNumScl")

    @property
    def current_scale(self):
        self.selected_scale.wait_for_connection()

        return self.scales[int(self.selected_scale.get())]

    def __init__(self, *args, connection_timeout=DEFAULT_CONNECTION_TIMEOUT, **kwargs):
        super().__init__(*args, **kwargs)

        n_scales = -1
        try:
            self.num_scales.wait_for_connection(connection_timeout)
            n_scales = int(self.num_scales.get())
        except TimeoutError:
            n_scales = 8

        self.scales = []

        def for_each_sig(name, sig):
            setattr(self, name, sig)
            self.scales.append(sig)

        components = (
            (f"scale_{i}", Component(Scale, f"SC{i}:")) for i in range(n_scales)
        )
        add_components_to_device(self, components, for_each_sig=for_each_sig)


class ERAS(Device):
    """Ophyd abstraction for the Ethernet Range Selector device."""

    device_name = Component(EpicsSignal, "GetDev", write_pv="SetDev")
    location = Component(EpicsSignal, "GetLoc", write_pv="SetLoc")
    version = Component(EpicsSignalRO, "GetVer")

    def __init__(self, *args, connection_timeout=DEFAULT_CONNECTION_TIMEOUT, **kwargs):
        super().__init__(*args, **kwargs)

        components = (
            (
                f"channel_{i}",
                Component(Channel, f"CH{i}:", connection_timeout=connection_timeout),
            )
            for i in range(1, 5)
        )
        add_components_to_device(
            self, components, for_each_sig=lambda name, sig: setattr(self, name, sig)
        )
