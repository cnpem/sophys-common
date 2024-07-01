from ophyd import Component, FormattedComponent, \
    Device, EpicsSignal, EpicsSignalRO, PVPositionerIsClose
from .motor import ControllableMotor


class Goniometer(PVPositionerIsClose):

    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:GonRx{device_number}_SP_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}_SP", kind="config")
    actuate = Component(EpicsSignal, "GonRxUpdate_SP", kind="omitted")

    def __init__(self, prefix, device_number, **kwargs):
        self.device_number = device_number
        super().__init__(prefix=prefix, **kwargs)


class ShortStroke(PVPositionerIsClose):

    readback = FormattedComponent(EpicsSignal, "{prefix}Shs{shs_axis}_S_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}Shs{shs_axis}_SP", kind="config")
    actuate = FormattedComponent(EpicsSignal, "ShsUpdate_{shs_axis}_SP", kind="omitted")

    def __init__(self, prefix, shs_axis, **kwargs):
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class DcmLite(Device):

    gonio1 = Component(Goniometer, "1")
    gonio2 = Component(Goniometer, "2")
    
    gap = Component(ShortStroke, "Uy")
    pitch = Component(ShortStroke, "Rx") 
    roll = Component(ShortStroke, "Rz")

    leveler1 = Component(ControllableMotor, "PB01:m1")
    leveler2 = Component(ControllableMotor, "PB01:m2")
    leveler3 = Component(ControllableMotor, "PB01:m3")
    u_x = Component(ControllableMotor, "PB01:m4")

    spindle_x_plus = Component(ControllableMotor, "PB01:m5")
    spindle_x_minus = Component(ControllableMotor, "PB01:m6")
    
    granite_x = Component(ControllableMotor, "PB01:CS2:m7")
    granite_y = Component(ControllableMotor, "PB01:CS1:m8")
