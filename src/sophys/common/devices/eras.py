import copy

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO


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

            self.num_scales.wait_for_connection()
            for i in range(int(self.num_scales.get())):
                s = Component(self.Scale, "SC{}:".format(i))
                s_name = "scale_{}".format(i)
                s.__set_name__(s, s_name)

                self._sig_attrs[s_name] = s
                self._component_kinds[s_name] = s.kind
                self._instantiate_component(s_name)

                setattr(self, s_name, self._signals[s_name])
                self.scales.append(self._signals[s_name])

    channel_1 = Component(Channel, "CH1:")
    channel_2 = Component(Channel, "CH2:")
    channel_3 = Component(Channel, "CH3:")
    channel_4 = Component(Channel, "CH4:")
