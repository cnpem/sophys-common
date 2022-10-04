from ophyd import (
    Device,
    Component,
    EpicsSignal,
    EpicsSignalRO,
    set_and_wait,
    DeviceStatus,
)


class C400(Device):
    exposure_time = Component(EpicsSignal, ":PERIOD", kind="config")
    reading = Component(EpicsSignal, ":COUNT_ch1", kind="normal")
    acquire = Component(EpicsSignal, ":ACQUIRE", kind="omitted", put_complete=True)

    def stage(self):
        self.initial_enabled_state = 0
        set_and_wait(self.acquire, 1)
        return super().stage()

    def unstage(self):
        ret = super().unstage()
        set_and_wait(self.acquire, self.initial_enabled_state)
        return ret


if __name__ == "__main__":
    c400 = C400("EMA:B:c40001", name="c400")
