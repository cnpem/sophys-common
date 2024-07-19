from ophyd import EpicsMotor, Component, EpicsSignal, FormattedComponent
from ophyd.device import create_device_from_components


class ControllableMotor(EpicsMotor):
    """Custom EpicsMotor that enables control before a plan and disables it after."""

    enable_control = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stage_sigs["enable_control"] = 1


def VirtualControllableMotor(prefix, components, name, **kwargs):
    """
    Custom EpicsMotor that enables control of a list of motors
    before a plan and disables them after.

    This is useful for virtual motors that depends on the control
    state of several real motors in order to work properly.

    This is primarily intended for cases in which we have a virtual
    motor (e.g. a slit, composed of two motors in a direction), and to
    move that virtual motor, you first have to enable movement of every
    single real motor it is composed of.

    .. admonition:: Example usage - A vertical slit gap

        .. code-block:: python

            real_motors = {
                "top": "SWC:MOTOR:m2",
                "bottom": "SWC:MOTOR:m3",
            }
            v_gap = VirtualControllableMotor("SWC:MOTOR:m1", real_motors, "vertical_gap")

    Parameters
    ----------

    prefix : str
        The prefix of the virtual motor.
    components : dict of (string, string)
        The real motors that constitute this virtual device, in the form (name, prefix).
    name : str
        Name of the created virtual motor.
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
