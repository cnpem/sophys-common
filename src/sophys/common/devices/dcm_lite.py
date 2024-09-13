from ophyd import Component, FormattedComponent, \
    Device, EpicsSignal, EpicsSignalRO, PVPositionerIsClose, \
    EpicsMotor
from .motor import ControllableMotor


class DcmGranite(Device):
    """
        Device for controlling the DCM Granite
    """

    leveler1 = Component(ControllableMotor, "m1")
    leveler2 = Component(ControllableMotor, "m2")
    leveler3 = Component(ControllableMotor, "m3")

    u_x = Component(ControllableMotor, "m4")

    spindle_x_plus = Component(ControllableMotor, "m5")
    spindle_x_minus = Component(ControllableMotor, "m6")

    granite_ux = Component(EpicsMotor, "CS2:m7")
    granite_ry = Component(EpicsMotor, "CS2:m2")
    granite_uz = Component(EpicsMotor, "CS2:m9")

    leveler_rx = Component(EpicsMotor, "CS1:m1")
    leveler_rz = Component(EpicsMotor, "CS1:m3")
    leveler_uy = Component(EpicsMotor, "CS1:m8")


class Goniometer(PVPositionerIsClose):
    """
        Device for controlling one Goniometer of the DCM Lite.
    """
    readback = FormattedComponent(EpicsSignal, "{prefix}DCM01:GonRx{device_number}_SP_RBV", kind="hinted")
    setpoint = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}_SP", kind="config")
    actuate = Component(EpicsSignal, "DCM01:GonRxUpdate_SP", kind="omitted")

    stopped = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}DesVelZero_RBV", kind="omitted")
    low_limit  = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}MinusLimit_RBV", kind="omitted")
    high_limit = FormattedComponent(EpicsSignalRO, "{prefix}DCM01:GonRx{device_number}PlusLimit_RBV", kind="omitted")

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

    granite = DcmGranite("PB01:", name="granite")

