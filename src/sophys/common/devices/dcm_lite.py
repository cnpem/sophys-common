from ophyd import Component, FormattedComponent, DynamicDeviceComponent, \
    Device, EpicsSignal, EpicsSignalRO, PVPositionerIsClose


class Goniometer(PVPositionerIsClose):
    
    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:GonRx{device_number}_SP_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}_SP", kind="config")
    actuate = Component(EpicsSignal, "GonRxUpdate_SP", kind="omitted")

    def __init__(self, prefix, device_number, **kwargs):
        self.device_number = device_number
        super().__init__(prefix=prefix, **kwargs)

class DcmLite(Device):

    gonio1 = Component(Goniometer, "1")
    gonio2 = Component(Goniometer, "2")
    
