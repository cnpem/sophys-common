import numpy as np
from ophyd import (  # numpydoc ignore=GL08
    Component,
    Device,
    EpicsMotor,
    EpicsSignal,
    FormattedComponent,
)
from ophyd.device import create_device_from_components
from ophyd.status import AndStatus, SubscriptionStatus
from ophyd.status import wait as status_wait


class ReadbackEpicsMotor(EpicsMotor):
    """
    An EpicsMotor subclass that includes readback tolerance checking.

    This motor extends the standard `EpicsMotor` to ensure that a move operation
    does not complete until both the standard motion status (`dmov`) and the
    actual readback value (`user_readback`) are within a specified `tolerance`
    and `relative tolerance` from the target position.

    Parameters
    ----------
    prefix : str, optional
        The EPICS PV prefix for the motor records.
    name : str
        The name of the device (required by Ophyd).
    tolerance : float
        The acceptable absolute difference between the target position and
        the `user_readback` value to consider the move successful.
    relative_tolerance : float
        The relative tolerance.
    timeout : float
        Maximum timeout to wait to mark the status as a failure.
    settle_time : float, optional
        Time to wait after completion.
    **kwargs
        Additional keyword arguments passed to `EpicsMotor`.
    """

    def __init__(  # numpydoc ignore=GL08
        self,
        prefix: str,
        name: str,
        tolerance: float,
        relative_tolerance: float,
        timeout: float | None = None,
        settle_time: float | None = None,
        **kwargs,
    ):
        self.tolerance = tolerance
        self.rtol = relative_tolerance
        self.status_timeout = timeout
        self.rbv_settle_time = settle_time
        super().__init__(
            prefix=prefix,
            name=name,
            timeout=timeout,
            settle_time=settle_time,
            **kwargs,
        )

    def move(self, position, wait=True, **kwargs):
        """
        Move the motor to a target position and wait for readback tolerance.

        Unlike the standard `EpicsMotor.move`, this method blocks or returns
        a status object that only completes when both the motor motion is done
        and the actual readback (`user_readback`) is within the defined
        `tolerance` and `relative tolerance` from the target position.

        Parameters
        ----------
        position : float
            The target position to move the motor to.
        wait : bool, optional
            If True, blocks execution until the motion and readback tolerance
            criteria are met. If False, returns the status object immediately.
            Defaults to True.
        **kwargs : dict
            Additional keyword arguments passed to the parent's move method.
        """
        timeout = kwargs.get("timeout", self.status_timeout)
        settle_time = kwargs.get("settle_time", self.rbv_settle_time)
        self._started_moving = False
        dmov_status = super().move(position, timeout=timeout)
        self.user_setpoint.put(position, wait=False)

        def check_readback(*args, value, **kwargs):  # numpydoc ignore=GL08
            return np.isclose(a=value, b=position, atol=self.tolerance, rtol=self.rtol)

        rbv_status = SubscriptionStatus(
            self.user_readback,
            check_readback,
            settle_time=settle_time,
            timeout=timeout,
        )
        combined_status = AndStatus(dmov_status, rbv_status)

        try:
            if wait:
                status_wait(combined_status)
        except KeyboardInterrupt:
            self.stop()
            raise

        return combined_status


class MotorMixinResolution(Device):  # numpydoc ignore=GL08
    motor_step_size = Component(EpicsSignal, ".MRES", kind="config", auto_monitor=True)

    steps_per_revolution = Component(EpicsSignal, ".SREV", kind="omitted")
    units_per_revolution = Component(EpicsSignal, ".UREV", kind="omitted")


class MotorMixinMiscellaneous(Device):  # numpydoc ignore=GL08
    display_precision = Component(
        EpicsSignal, ".PREC", kind="config", auto_monitor=True
    )
    code_version = Component(EpicsSignal, ".VERS", kind="config")


class MotorMixinMotion(Device):  # numpydoc ignore=GL08
    max_velocity = Component(EpicsSignal, ".VMAX", kind="config")
    base_velocity = Component(EpicsSignal, ".VBAS", kind="config")


class ExtendedEpicsMotor(  # numpydoc ignore=GL08
    EpicsMotor, MotorMixinResolution, MotorMixinMiscellaneous, MotorMixinMotion
):
    pass


class ControllableMotor(EpicsMotor):  # numpydoc ignore=PR01
    """Custom EpicsMotor that enables control before a plan and disables it after."""

    enable_control = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def __init__(self, *args, **kwargs):  # numpydoc ignore=GL08
        super().__init__(*args, **kwargs)

        self.stage_sigs["enable_control"] = 1


class VirtualControllableMotorBaseClass(EpicsMotor):  # numpydoc ignore=GL08
    pass


def _create_virtual_controllable_motor(components):
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
            EpicsSignal, suffix=motorPv + ".CNEN", kind="config"
        )

    devClass = create_device_from_components(
        name="virtual_motor_class",
        base_class=VirtualControllableMotorBaseClass,
        **formattedComponents,
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


def MotorGroup(prefix, motors_suffixes, **kwargs):  # numpydoc ignore=PR01,PR02
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
    motors_suffixes : dict of (str, str)
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
            deviceClass, comp_kwargs = _create_virtual_controllable_motor(suffix[1])

        components[key] = Component(deviceClass, suffix=suffix, **comp_kwargs)

    devClass = create_device_from_components(name="motor_group", **components)

    return devClass(prefix=prefix, **kwargs)
