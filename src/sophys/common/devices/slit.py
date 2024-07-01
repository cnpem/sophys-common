from ophyd import Device, FormattedComponent
from .motor import ControllableMotor, VirtualControllableMotor


class VerticalSlit(Device):

    top = FormattedComponent(ControllableMotor, "{prefix}{motor_top}")
    bottom = FormattedComponent(ControllableMotor, "{prefix}{motor_bottom}")

    vertical_gap = FormattedComponent(
        VirtualControllableMotor, "{prefix}{vertical_gap}", components={
            "cnen_top": "{prefix}{motor_top}",
            "cnen_bottom": "{prefix}{motor_bottom}"
        })
    vertical_offset = FormattedComponent(
        VirtualControllableMotor, "{prefix}{vertical_offset}", components={
            "cnen_top": "{prefix}{motor_top}",
            "cnen_bottom": "{prefix}{motor_bottom}"
        })
    
    def __init__(self, prefix, motor_top, motor_bottom, vertical_gap, vertical_offset, **kwargs):
        self.motor_top = motor_top
        self.motor_bottom = motor_bottom
        self.vertical_gap = vertical_gap
        self.vertical_offset = vertical_offset
        super().__init__(prefix=prefix, **kwargs)