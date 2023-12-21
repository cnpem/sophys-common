import logging
from ophyd import (
    Device,
    Component,
    EpicsSignal,
    set_and_wait,
)


class C400(Device):
    exposure_time = Component(EpicsSignal, ":PERIOD", kind="config")
    reading = Component(EpicsSignal, ":COUNT_ch1", kind="normal")
    acquire = Component(EpicsSignal, ":ACQUIRE", kind="omitted", put_complete=True)

    def stage(self):
        logging.warn(
            "This C400 device is deprecated! Please consider using the new AreaDetector-based version."
        )
        self.initial_enabled_state = 0
        set_and_wait(self.acquire, 1)
        return super().stage()

    def unstage(self):
        ret = super().unstage()
        set_and_wait(self.acquire, self.initial_enabled_state)
        return ret
