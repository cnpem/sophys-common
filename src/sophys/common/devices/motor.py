from ophyd import EpicsMotor, Component, EpicsSignal
from ophyd.device import create_device_from_components


class ControllableMotor(EpicsMotor):
    """
        Custom EpicsMotor that enables control before a plan and disables it after.
    """
    control_enabled = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def stage(self):
        super().stage()
        self.control_enabled.set(1)

    def unstage(self):
        super().unstage()
        self.control_enabled.set(0)

def VirtualControllableMotor(prefix, components, name, **kwargs):
    """
        Custom EpicsMotor that enables control of a list of motors 
        before a plan and disables them after.
        
        This is useful for virtual motors that depends on the control state of several
        real motors in order to work properly.

        ```
            componentsDict = {
                "cnen_top": FormattedComponent(EpicsSignal, suffix='SWC:MOTOR:m2.CNEN'),
                "cnen_bottom": FormattedComponent(EpicsSignal, suffix='SWC:MOTOR:m3.CNEN')
            }
            motor = VirtualControllableMotor("SWC:MOTOR:m1", componentsDict, "vertical_gap")
        ```
    """

    devClass = create_device_from_components(
        name="virtual_motor_class", base_class=EpicsMotor, **components)
    
    class VirtualControllableMotorClass(devClass):

        def __init__(self, attr_keys, **kwargs):
            super().__init__(**kwargs)
            self.attr_list = []
            for attr in attr_keys:
                self.attr_list.append(getattr(self, attr))

        def stage(self):
            super().stage()
            for attr in self.attr_list:
                status = attr.set(1)
                status.wait()

        def unstage(self):
            super().unstage()
            for attr in self.attr_list:
                status = attr.set(0)
                status.wait()

    return VirtualControllableMotorClass(
        name=name, prefix=prefix, attr_keys=components.keys(), **kwargs)