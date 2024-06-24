from ophyd import Component, DynamicDeviceComponent, \
    Device, EpicsSignal, EpicsSignalRO


class TatuBase(Device):

    activate = Component(
        EpicsSignal, write_pv=":Activate", read_pv=":TatuActive", kind="config")
    master_mode = Component(EpicsSignal, ":MasterMode", kind="config")
    tatu_stop = Component(EpicsSignal, ":Stop", kind="config")
    trigger = Component(EpicsSignal, ":FlyScan", kind="config")
    reset_pulses = Component(EpicsSignal, ":Zeropulses", kind="config")
    record_readouts = Component(EpicsSignal, ":Record", kind="config")


    def stage(self):
        super().stage()
        self.activate.set(1).wait()

    def unstage(self):
        super().unstage()
        self.activate.set(0).wait()

    def stop(self):
        self.tatu_stop.set(1)

    def pause(self):
        self.master_mode_state = self.master_mode.get()
        self.tatu_stop.set(1)

    def resume(self):
        self.master_mode.set(self.master_mode_state).wait()
        self.activate.set(1).wait()