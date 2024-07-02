from ophyd import Component, FormattedComponent, \
    Device, EpicsSignal, EpicsSignalRO, PVPositionerIsClose
from .motor import ControllableMotor


class Goniometer(PVPositionerIsClose):
    """
        Device for controlling one Goniometer of the DCM Lite.
    """
    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:GonRx{device_number}_SP_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}_SP", kind="config")
    actuate = Component(EpicsSignal, "DCM01:GonRxUpdate_SP", kind="omitted")

    def __init__(self, prefix, device_number, **kwargs):
        self.device_number = device_number
        super().__init__(prefix=prefix, **kwargs)


class ShortStroke(PVPositionerIsClose):
    """
        Device for controlling one axis of the Short Stroke of the DCM Lite.
    """

    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:Shs{shs_axis}_S_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:Shs{shs_axis}_SP", kind="config")
    actuate = FormattedComponent(EpicsSignal, "{prefix}DCM01:ShsUpdate_{shs_axis}_SP", kind="omitted")

    def __init__(self, prefix, shs_axis, **kwargs):
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class DcmLite(Device):
    """
        Device for controlling the DCM Lite monochromator.
    """

    gonio1 = Component(Goniometer, "", device_number="1")
    gonio2 = Component(Goniometer, "", device_number="2")
    
    gap = Component(ShortStroke, "", shs_axis="Uy")
    pitch = Component(ShortStroke, "", shs_axis="Rx") 
    roll = Component(ShortStroke, "", shs_axis="Rz")

    leveler1 = Component(ControllableMotor, "PB01:m1")
    leveler2 = Component(ControllableMotor, "PB01:m2")
    leveler3 = Component(ControllableMotor, "PB01:m3")
    u_x = Component(ControllableMotor, "PB01:m4")

    spindle_x_plus = Component(ControllableMotor, "PB01:m5")
    spindle_x_minus = Component(ControllableMotor, "PB01:m6")

    granite_x = Component(ControllableMotor, "PB01:CS2:m7")
    granite_y = Component(ControllableMotor, "PB01:CS1:m8")
