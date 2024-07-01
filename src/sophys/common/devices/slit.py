from ophyd import FormattedComponent
from ophyd.device import create_device_from_components
from .motor import ControllableMotor, VirtualControllableMotor


def VerticalSlit(prefix, top, bottom, vertical_gap, vertical_offset, name, **kwargs):

    verticalSlitComponents = {
        "top": FormattedComponent(ControllableMotor, f"{prefix}{top}"),
        "bottom": FormattedComponent(ControllableMotor, f"{prefix}{bottom}"),
        "gap": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{vertical_gap}", components={
                "top": f"{prefix}{top}",
                "bottom": f"{prefix}{bottom}"
            }),
        "offset": FormattedComponent(
            VirtualControllableMotor, f"{prefix}{vertical_offset}", components={
                "top": f"{prefix}{top}",
                "bottom": f"{prefix}{bottom}"
            })
    }

    VerticalSlit = create_device_from_components(
        name="slit", **verticalSlitComponents)

    return VerticalSlit(prefix=prefix, name=name, **kwargs)
    