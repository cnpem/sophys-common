from ophyd import Device, Component, EpicsSignal, EpicsSignalWithRBV, \
    DynamicDeviceComponent, EpicsSignalRO


class PicoloChannel(Device):
    """
    Device for one of the channels in the Picolo picoammeter.
    """

    data = Component(EpicsSignalRO, "Data")
    enable = Component(EpicsSignal, "Enable")
    value = Component(EpicsSignal, "EngValue", kind="hinted")
    saturated = Component(EpicsSignal, "Saturated")
    range = Component(EpicsSignalWithRBV, "Range")
    auto_range = Component(EpicsSignal, "AutoRange")
    acquire_mode = Component(EpicsSignalWithRBV, "AcquireMode")
    state = Component(EpicsSignalRO, "State")


class PicoloAcquisitionTime(EpicsSignalWithRBV):
    """
        Device that handles set enum acquisition time using a float in milliseconds.
    """

    def set_value(self, acquisiton_time: float):
        enums = self.metadata['enum_strs']
        enums_float = [(float(item.replace(" ms", ""))/1000) for item in enums]
        if acquisiton_time not in enums_float:
            print("Acquisition time not found")
            return
        
        super().set(f"{int(acquisiton_time*1000)} ms").wait()    


class Picolo(Device):
    """
    Device for the 4 channel Picolo picoammeter.
    """

    range = Component(EpicsSignal, "Range")
    auto_range = Component(EpicsSignal, "AutoRange", string=True)
    acquisition_time = Component(PicoloAcquisitionTime, "AcquisitionTime", string=True)
    sample_rate = Component(EpicsSignalWithRBV, "SampleRate")
    acquire_mode = Component(EpicsSignal, "AcquireMode")
    samples_per_trigger = Component(EpicsSignalWithRBV, "NumAcquire")
    data_reset = Component(EpicsSignal, "DataReset")
    data_acquired = Component(EpicsSignal, "DataAcquired")
    
    continuous_mode = DynamicDeviceComponent({
        "start_acq": (EpicsSignal, "Start", {}),
        "stop_acq": (EpicsSignal, "Stop", {})
    })

    ch1 = Component(PicoloChannel, "Current1:")
    ch2 = Component(PicoloChannel, "Current2:")
    ch3 = Component(PicoloChannel, "Current3:")
    ch4 = Component(PicoloChannel, "Current4:")


    def reset_data(self):
        past_acquire_mode = self.acquire_mode.get() # Set continuous mode
        
        self.acquire_mode.set(0).wait() # Set continuous mode
        
        self.data_reset.set(1).wait()

        self.acquire_mode.set(past_acquire_mode).wait()
