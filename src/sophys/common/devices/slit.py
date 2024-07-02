from ophyd import FormattedComponent, Component
from ophyd.device import create_device_from_components
from .motor import ControllableMotor, VirtualControllableMotor


def VerticalSlit(prefix, top, bottom, gap, offset, name, **kwargs):

    verticalSlitComponents = {
        "top": FormattedComponent(ControllableMotor, f"{prefix}{top}"),
        "bottom": FormattedComponent(ControllableMotor, f"{prefix}{bottom}"),
        "gap": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{gap}", components={
                "top": f"{prefix}{top}",
                "bottom": f"{prefix}{bottom}"
            }),
        "offset": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{offset}", components={
                "top": f"{prefix}{top}",
                "bottom": f"{prefix}{bottom}"
            })
    }

    VerticalSlit = create_device_from_components(
        name="vertical_slit", **verticalSlitComponents)

    return VerticalSlit(prefix=prefix, name=name, **kwargs)


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
