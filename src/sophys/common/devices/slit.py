from ophyd import FormattedComponent, Component
from ophyd.device import create_device_from_components
from .motor import ControllableMotor, VirtualControllableMotor


def _create_vertical_components(prefix, top, bottom, gap, offset):

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

    verticalSlitComponents = _create_vertical_components(prefix, top, bottom, gap, offset)

    VerticalSlit = create_device_from_components(
        name="vertical_slit", **verticalSlitComponents)

    return VerticalSlit(prefix=prefix, **kwargs)


def _create_horizontal_components(prefix, left, right, gap, offset):

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

    horizontalSlitComponents = _create_horizontal_components(prefix, left, right, gap, offset)

    HorizontalSlit = create_device_from_components(
        name="horizontal_slit", **horizontalSlitComponents)

    return HorizontalSlit(prefix=prefix, **kwargs)
