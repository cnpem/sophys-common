from ophyd import Component
from ophyd.device import create_device_from_components

from .motor import ControllableMotor, VirtualControllableMotor


def _create_vertical_components(prefix, top, bottom, gap, offset):
    """
    Create all the components belonging to the vertical slit device and
    return them in a dictionary.
    """

    virtualMotorComponents = {
        "top": f"{prefix}{top}",
        "bottom": f"{prefix}{bottom}"
    }

    verticalSlitComponents = {
        "top": Component(ControllableMotor, f"{top}"),
        "bottom": Component(ControllableMotor, f"{bottom}"),
        "gap": Component(
            VirtualControllableMotor, f"{gap}", components=virtualMotorComponents),
        "offset": Component(
            VirtualControllableMotor, f"{offset}", components=virtualMotorComponents)
    }

    return verticalSlitComponents


def VerticalSlit(prefix, top, bottom, gap, offset, **kwargs):
    """Create a slit device that can only be moved vertically."""

    verticalSlitComponents = _create_vertical_components(prefix, top, bottom, gap, offset)

    verticalSlitClass = create_device_from_components(
        name="vertical_slit", **verticalSlitComponents)

    return verticalSlitClass(prefix=prefix, **kwargs)


def _create_horizontal_components(prefix, left, right, gap, offset):
    """
    Create all the components belonging to the horizontal slit device and
    return them in a dictionary.
    """

    virtualMotorComponents = {
        "left": f"{prefix}{left}",
        "right": f"{prefix}{right}"
    }

    horizontalSlitComponents = {
        "left": Component(ControllableMotor, f"{left}"),
        "right": Component(ControllableMotor, f"{right}"),
        "gap": Component(
            VirtualControllableMotor, f"{gap}", components=virtualMotorComponents),
        "offset": Component(
            VirtualControllableMotor, f"{offset}", components=virtualMotorComponents)
    }

    return horizontalSlitComponents


def HorizontalSlit(prefix, left, right, gap, offset, **kwargs):
    """Create a slit device that can only be moved horizontally."""

    horizontalSlitComponents = _create_horizontal_components(prefix, left, right, gap, offset)

    horizontalSlitClass = create_device_from_components(
        name="horizontal_slit", **horizontalSlitComponents)

    return horizontalSlitClass(prefix=prefix, **kwargs)


def Slit(prefix, top, bottom, v_gap, v_offset, left, right, h_gap, h_offset, **kwargs):
    """Create a slit device that can be moved vertically and horizontally."""
    slitComponents = {}

    horizontalSlitComponents = _create_horizontal_components(prefix, left, right, h_gap, h_offset)
    slitComponents.update(horizontalSlitComponents)
    verticalSlitComponents = _create_vertical_components(prefix, top, bottom, v_gap, v_offset)
    slitComponents.update(verticalSlitComponents)

    slitClass = create_device_from_components(
        name="slit", **slitComponents)

    return slitClass(prefix=prefix, **kwargs)
