import copy
import typing

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO


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
    """
    for component_name, component in components:
        component.__set_name__(component, component_name)

        obj._sig_attrs[component_name] = component
        obj._component_kinds[component_name] = component.kind
        obj._instantiate_component(component_name)

        if for_each_sig is not None:
            for_each_sig(name=component_name, sig=obj._signals[component_name])


class ERAS(Device):
    """Ophyd abstraction for the Ethernet Range Selector device."""

    device_name = Component(EpicsSignal, "GetDev", write_pv="SetDev")
    location = Component(EpicsSignal, "GetLoc", write_pv="SetLoc")
    version = Component(EpicsSignalRO, "GetVer")

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

        class Scale(Device):
            full_scale_label = Component(EpicsSignal, "GetFSLbl", write_pv="SetFSLbl")
            full_scale = Component(EpicsSignalRO, "GetFS")
            sensitivity_label = Component(EpicsSignal, "GetSTLbl", write_pv="SetSTLbl")
            sensitivity = Component(EpicsSignalRO, "GetST")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if not hasattr(self.__class__, "_old_sig_attrs"):
                self.__class__._old_sig_attrs = copy.deepcopy(self._sig_attrs)

            self.scales = []
            self._sig_attrs = self.__class__._old_sig_attrs

            n_scales = -1
            try:
                self.num_scales.wait_for_connection()
                n_scales = int(self.num_scales.get())
            except TimeoutError:
                n_scales = 8

            def for_each_sig(name, sig):
                setattr(self, name, sig)
                self.scales.append(sig)

            components = (
                (f"scale_{i}", Component(self.Scale, f"SC{i}:"))
                for i in range(n_scales)
            )
            add_components_to_device(self, components, for_each_sig=for_each_sig)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        components = (
            (f"channel_{i}", Component(self.Channel, f"CH{i}:")) for i in range(1, 5)
        )
        add_components_to_device(
            self, components, for_each_sig=lambda name, sig: setattr(self, name, sig)
        )
