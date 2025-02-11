from ophyd import Device, EpicsMotor, Component, EpicsSignal, FormattedComponent
from ophyd.device import create_device_from_components


class MotorMixinResolution(Device):
    motor_step_size = Component(EpicsSignal, ".MRES", kind="config", auto_monitor=True)

    steps_per_revolution = Component(EpicsSignal, ".SREV", kind="omitted")
    units_per_revolution = Component(EpicsSignal, ".UREV", kind="omitted")


class MotorMixinMiscellaneous(Device):
    display_precision = Component(
        EpicsSignal, ".PREC", kind="config", auto_monitor=True
    )
    code_version = Component(EpicsSignal, ".VERS", kind="config")


class MotorMixinMotion(Device):
    max_velocity = Component(EpicsSignal, ".VMAX", kind="config")
    base_velocity = Component(EpicsSignal, ".VBAS", kind="config")


class ExtendedEpicsMotor(
    EpicsMotor, MotorMixinResolution, MotorMixinMiscellaneous, MotorMixinMotion
):
    pass


class ControllableMotor(EpicsMotor):
    """Custom EpicsMotor that enables control before a plan and disables it after."""

    enable_control = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stage_sigs["enable_control"] = 1


def create_virtual_controllable_motor(components):
    """
    Custom EpicsMotor that enables control of a list of motors
    before a plan and disables them after.

    This is useful for virtual motors that depends on the control
    state of several real motors in order to work properly.

    This is primarily intended for cases in which we have a virtual
    motor (e.g. a slit, composed of two motors in a direction), and to
    move that virtual motor, you first have to enable movement of every
    single real motor it is composed of.

    .. admonition:: Usage example - A vertical slit gap

        .. code-block:: python

            real_motors = {
                "top": "SWC:MOTOR:m2",
                "bottom": "SWC:MOTOR:m3",
            }
            v_gap = VirtualControllableMotor("SWC:MOTOR:m1", real_motors, "vertical_gap")

    Parameters
    ----------
    components : dict of (string, string)
        The real motors that constitute this virtual device, in the form (name, prefix).
    """
    formattedComponents = {}
    for key, motorPv in components.items():
        formattedComponents["cnen_" + key] = FormattedComponent(
            EpicsSignal, suffix=motorPv + ".CNEN"
        )

    devClass = create_device_from_components(
        name="virtual_motor_class", base_class=EpicsMotor, **formattedComponents
    )

    class VirtualControllableMotorClass(devClass):
        def __init__(self, *args, attr_keys, **kwargs):
            super().__init__(*args, **kwargs)
            self.attr_list = []
            for attr in attr_keys:
                self.attr_list.append(getattr(self, attr))

        def stage(self):
            ret = super().stage()
            for attr in self.attr_list:
                attr.set(1).wait()

            return ret

        def unstage(self):
            for attr in self.attr_list:
                attr.set(0).wait()

            return super().unstage()

    return (VirtualControllableMotorClass, {"attr_keys": formattedComponents.keys()})


def MotorGroup(prefix, motors_suffixes, name, **kwargs):
    """
    Function to instantiate several motor devices.

    .. admonition:: Usage example

        .. code-block:: python

            real_motors = {
                "x": "SWC:MOTOR:m1",
                "y": "SWC:MOTOR:m2",
                "z": "SWC:MOTOR:m3"
            }
            motors_suffixes = {
                "x": "m1",
                "y": "m2",
                "z": "m3",
                "kin_x": ("CS1:m1", real_motors),
                "kin_y": ("CS1:m2", real_motors),
                "kin_z": ("CS1:m3", real_motors)
            }

            motor_group = MotorGroup(
                prefix="SWC:MOTOR:", motors_suffixes=motors_suffixes, name="motor_group")

    Parameters
    ----------
    prefix : str
        The prefix of the motor group.
    motors_suffixes : dict of (string, string)
        The real motors that constitute this motor group, in the form of .
    name : str
        Name of the created motor group.
    """
    components = {}

    for key, suffix in motors_suffixes.items():
        args = {}
        comp_kwargs = {}
        deviceClass = ControllableMotor
        if isinstance(suffix, tuple):
            args["components"] = suffix[1]
            suffix = suffix[0]
            deviceClass, comp_kwargs = create_virtual_controllable_motor(suffix[1])

        components[key] = Component(deviceClass, prefix=suffix, **comp_kwargs)

    devClass = create_device_from_components(name="motor_group", **components)

    return devClass(prefix=prefix, name=name, **kwargs)
