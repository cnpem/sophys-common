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

def createVirtualControllableMotor(prefix, components, name):
    devClass = create_device_from_components(
        name="virtual_motor_class", base_class=EpicsMotor, **components)
    
    class VirtualControllableMotor(devClass):
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

    return VirtualControllableMotor(
        name=name, prefix=prefix, attr_keys=components.keys())