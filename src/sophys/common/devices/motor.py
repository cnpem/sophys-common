from ophyd import EpicsMotor, Component, EpicsSignal, FormattedComponent
from ophyd.device import create_device_from_components


class ControllableMotor(EpicsMotor):
    """
        Custom EpicsMotor that enables control before a plan and disables it after.
    """
    enable_control = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def stage(self):
        super().stage()
        self.enable_control.set(1).wait()

    def unstage(self):
        super().unstage()
        self.enable_control.set(0).wait()

def VirtualControllableMotor(prefix, components, name, **kwargs):
    """
        Custom EpicsMotor that enables control of a list of motors 
        before a plan and disables them after.
        
        This is useful for virtual motors that depends on the control state of several
        real motors in order to work properly.

        .. admonition:: example
        
            .. code-block:: python

                componentsDict = {
                    "top": "SWC:MOTOR:m2"),
                    "bottom": "SWC:MOTOR:m3")
                }
                motor = VirtualControllableMotor("SWC:MOTOR:m1", componentsDict, "vertical_gap")
    """
    formattedComponents = {}
    for key, motorPv in components.items():
        formattedComponents["cnen_"+key] = FormattedComponent(EpicsSignal, suffix=motorPv+".CNEN")

    devClass = create_device_from_components(
        name="virtual_motor_class", base_class=EpicsMotor, **formattedComponents)
    
    class VirtualControllableMotorClass(devClass):

        def __init__(self, attr_keys, **kwargs):
            super().__init__(**kwargs)
            self.attr_list = []
            for attr in attr_keys:
                self.attr_list.append(getattr(self, attr))

        def stage(self):
            super().stage()
            for attr in self.attr_list:
                attr.set(1).wait()

        def unstage(self):
            super().unstage()
            for attr in self.attr_list:
                attr.set(0).wait()

    return VirtualControllableMotorClass(
        name=name, prefix=prefix, attr_keys=formattedComponents.keys(), **kwargs)
