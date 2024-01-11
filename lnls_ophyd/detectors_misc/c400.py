import logging
from ophyd import Device, Component, EpicsSignal


class C400(Device):
    exposure_time = Component(EpicsSignal, ":PERIOD", kind="config")
    reading = Component(EpicsSignal, ":COUNT_ch1", kind="normal")
    acquire = Component(EpicsSignal, ":ACQUIRE", kind="omitted", put_complete=True)

    def stage(self):
        logging.warn(
            "This C400 device is deprecated! Please consider using the new AreaDetector-based version."
        )
        self.initial_enabled_state = 0
        self.acquire.set(1).wait()
        return super().stage()

    def unstage(self):
        ret = super().unstage()
        self.acquire.set(self.initial_enabled_state).wait()
        return ret
