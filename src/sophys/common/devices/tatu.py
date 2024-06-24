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

    master_pulse = DynamicDeviceComponent({
        "number": (EpicsSignal, ":MasterPulseNumber", {"kind": "config"}),
        "period": (EpicsSignal, ":MasterPulsePeriod", {"kind": "config"}),
        "length": (EpicsSignal, ":MasterPulseLength", {"kind": "config"}),
        "active": (EpicsSignalRO, ":MasterPulsing", {"kind": "config"}),
        "count": (EpicsSignalRO, ":IssuedMasterPulses", {"kind": "config"})
    })

    fly_scan = DynamicDeviceComponent({
        "time": (EpicsSignal, ":FlyScanTimePreset", {"kind": "config"}),
        "trigger_count": (EpicsSignalRO, ":TriggerCounter"),
        "file_path_1": (EpicsSignal, ":FlyScanFilePath", {"kind": "config"}),
        "file_path_2": (EpicsSignal, ":FlyScanFilePath2", {"kind": "config"}),
        "file_name": (EpicsSignal, ":FlyScanFileName", {"kind": "config"}),
        "file_open": (EpicsSignalRO, ":FlyScanFileOpen", {"kind": "config"}),
        "file_valid_path": (EpicsSignalRO, ":FlyScanFileValidPath", {"kind": "config"}),
        "file_error_code": (EpicsSignalRO, ":FlyScanErrorCode", {"kind": "config"}),
        "file_error_message": (EpicsSignalRO, ":FlyScanErrorMsg", {"kind": "config"})
    })


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