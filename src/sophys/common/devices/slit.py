import typing

from ophyd import Device, Component
from ophyd.device import create_device_from_components

from .motor import ControllableMotor, _create_virtual_controllable_motor


def _get_optional_kinematic_component(
    suffix: str, has_kinematic: bool, virtual_motor_components: dict
):
    if has_kinematic:
        klass, kwargs = _create_virtual_controllable_motor(virtual_motor_components)
        return Component(klass, str(suffix), **kwargs)
    return Component(ControllableMotor, str(suffix))


def _create_vertical_components(
    prefix: str,
    top: str,
    bottom: str,
    gap: typing.Optional[str] = None,
    offset: typing.Optional[str] = None,
    has_kinematic: bool = True,
) -> dict:
    """
    Create all the components belonging to the vertical slit device and
    return them in a dictionary.
    """

    virtualMotorComponents = {"top": f"{prefix}{top}", "bottom": f"{prefix}{bottom}"}

    verticalSlitComponents = {
        "top": Component(ControllableMotor, f"{top}"),
        "bottom": Component(ControllableMotor, f"{bottom}"),
    }

    if gap is not None:
        verticalSlitComponents.update(
            {
                "vertical_gap": _get_optional_kinematic_component(
                    gap, has_kinematic, virtualMotorComponents
                )
            }
        )

    if offset is not None:
        verticalSlitComponents.update(
            {
                "vertical_offset": _get_optional_kinematic_component(
                    offset, has_kinematic, virtualMotorComponents
                )
            }
        )

    return verticalSlitComponents


def VerticalSlit(
    prefix: str,
    top: str,
    bottom: str,
    gap: typing.Optional[str] = None,
    offset: typing.Optional[str] = None,
    has_kinematic: bool = True,
    **kwargs,
) -> Device:
    """Create a slit device that can only be moved vertically."""

    verticalSlitComponents = _create_vertical_components(
        prefix, top, bottom, gap, offset, has_kinematic
    )

    verticalSlitClass = create_device_from_components(
        name="vertical_slit", **verticalSlitComponents
    )

    return verticalSlitClass(prefix=prefix, **kwargs)


def _create_horizontal_components(
    prefix: str,
    left: str,
    right: str,
    gap: typing.Optional[str] = None,
    offset: typing.Optional[str] = None,
    has_kinematic: bool = True,
) -> dict:
    """
    Create all the components belonging to the horizontal slit device and
    return them in a dictionary.
    """

    virtualMotorComponents = {"left": f"{prefix}{left}", "right": f"{prefix}{right}"}

    horizontalSlitComponents = {
        "left": Component(ControllableMotor, f"{left}"),
        "right": Component(ControllableMotor, f"{right}"),
    }

    if gap is not None:
        horizontalSlitComponents.update(
            {
                "horizontal_gap": _get_optional_kinematic_component(
                    gap, has_kinematic, virtualMotorComponents
                )
            }
        )

    if offset is not None:
        horizontalSlitComponents.update(
            {
                "horizontal_offset": _get_optional_kinematic_component(
                    offset, has_kinematic, virtualMotorComponents
                )
            }
        )

    return horizontalSlitComponents


def HorizontalSlit(
    prefix: str,
    left: str,
    right: str,
    gap: typing.Optional[str] = None,
    offset: typing.Optional[str] = None,
    has_kinematic: bool = True,
    **kwargs,
) -> Device:
    """Create a slit device that can only be moved horizontally."""

    horizontalSlitComponents = _create_horizontal_components(
        prefix, left, right, gap, offset, has_kinematic
    )

    horizontalSlitClass = create_device_from_components(
        name="horizontal_slit", **horizontalSlitComponents
    )

    return horizontalSlitClass(prefix=prefix, **kwargs)


def Slit(
    prefix: str,
    top: str,
    bottom: str,
    left: str,
    right: str,
    v_gap: typing.Optional[str] = None,
    v_offset: typing.Optional[str] = None,
    h_gap: typing.Optional[str] = None,
    h_offset: typing.Optional[str] = None,
    has_kinematic: bool = True,
    **kwargs,
) -> Device:
    """Create a slit device that can be moved vertically and horizontally."""
    slitComponents = {}

    horizontalSlitComponents = _create_horizontal_components(
        prefix, left, right, h_gap, h_offset, has_kinematic
    )
    slitComponents.update(horizontalSlitComponents)
    verticalSlitComponents = _create_vertical_components(
        prefix, top, bottom, v_gap, v_offset, has_kinematic
    )
    slitComponents.update(verticalSlitComponents)

    slitClass = create_device_from_components(name="slit", **slitComponents)

    return slitClass(prefix=prefix, **kwargs)


def _create_kinematic_vertical_components(
    prefix: str,
    gap: str,
    offset: str,
    top: typing.Optional[str] = None,
    bottom: typing.Optional[str] = None,
) -> dict:
    """
    Create all the components belonging to the vertical slit device
    that can be moved through a gap and an offset and return them in a dictionary,
    using them as real motors, while the individual directions are virtual motors.
    """

    virtualMotorComponents = {
        "vertical_gap": f"{prefix}{gap}",
        "vertical_offset": f"{prefix}{offset}",
    }

    verticalSlitComponents = {
        "vertical_gap": Component(ControllableMotor, f"{gap}"),
        "vertical_offset": Component(ControllableMotor, f"{offset}"),
    }

    klass, kwargs = _create_virtual_controllable_motor(virtualMotorComponents)
    if top is not None:
        verticalSlitComponents.update(
            {
                "top": Component(klass, top, name=f"{top}", **kwargs),
            }
        )

    if bottom is not None:
        verticalSlitComponents.update(
            {"bottom": Component(klass, bottom, name=f"{bottom}", **kwargs)}
        )

    return verticalSlitComponents


def _create_kinematic_horizontal_components(
    prefix: str,
    gap: str,
    offset: str,
    left: typing.Optional[str] = None,
    right: typing.Optional[str] = None,
) -> dict:
    """
    Create all the components belonging to the horizontal slit device
    that can be moved through a gap and an offset and return them in a dictionary,
    using them as real motors, while the individual directions are virtual motors.
    """

    virtualMotorComponents = {
        "horizontal_gap": f"{prefix}{gap}",
        "horizontal_offset": f"{prefix}{offset}",
    }

    horizontalSlitComponents = {
        "horizontal_gap": Component(ControllableMotor, f"{gap}"),
        "horizontal_offset": Component(ControllableMotor, f"{offset}"),
    }

    klass, kwargs = _create_virtual_controllable_motor(virtualMotorComponents)
    if left is not None:
        horizontalSlitComponents.update(
            {
                "left": Component(klass, left, name=f"{left}", **kwargs),
            }
        )

    if right is not None:
        horizontalSlitComponents.update(
            {"right": Component(klass, right, name=f"{right}", **kwargs)}
        )

    return horizontalSlitComponents


def KinematicSlit(
    prefix: str,
    v_gap: str,
    v_offset: str,
    h_gap: str,
    h_offset: str,
    top: typing.Optional[str] = None,
    bottom: typing.Optional[str] = None,
    left: typing.Optional[str] = None,
    right: typing.Optional[str] = None,
    **kwargs,
) -> Device:
    """
    Create a slit device that can be moved with a gap or an offset horizontally and vertically,
    using them as real motors, while the individual directions are virtual motors.
    """
    slitComponents = {}

    horizontalSlitComponents = _create_kinematic_horizontal_components(
        prefix, h_gap, h_offset, left, right
    )

    slitComponents.update(horizontalSlitComponents)
    verticalSlitComponents = _create_kinematic_vertical_components(
        prefix, v_gap, v_offset, top, bottom
    )

    slitComponents.update(verticalSlitComponents)

    slitClass = create_device_from_components(name="slit", **slitComponents)

    return slitClass(prefix=prefix, **kwargs)
