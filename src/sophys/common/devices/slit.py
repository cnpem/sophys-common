from ophyd import FormattedComponent
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


def HorizontalSlit(prefix, left, right, gap, offset, name, **kwargs):

    horizontalSlitComponents = {
        "left": FormattedComponent(ControllableMotor, f"{prefix}{left}"),
        "right": FormattedComponent(ControllableMotor, f"{prefix}{right}"),
        "gap": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{gap}", components={
                "left": f"{prefix}{left}",
                "right": f"{prefix}{right}"
            }),
        "offset": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{offset}", components={
                "left": f"{prefix}{left}",
                "right": f"{prefix}{right}"
            })
    }

    HorizontalSlit = create_device_from_components(
        name="horizontal_slit", **horizontalSlitComponents)

    return HorizontalSlit(prefix=prefix, name=name, **kwargs)
    