import typing

from ophyd import Device, Component
from ophyd.device import create_device_from_components

from .motor import ControllableMotor, VirtualControllableMotor


def _create_vertical_components(
    prefix: str,
    top: str,
    bottom: str,
    gap: typing.Optional[str] = None,
    offset: typing.Optional[str] = None,
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
                "gap": Component(
                    VirtualControllableMotor,
                    f"{gap}",
                    components=virtualMotorComponents,
                ),
            }
        )

    if offset is not None:
        verticalSlitComponents.update(
            {
                "offset": Component(
                    VirtualControllableMotor,
                    f"{offset}",
                    components=virtualMotorComponents,
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
    **kwargs,
) -> Device:
    """Create a slit device that can only be moved vertically."""

    verticalSlitComponents = _create_vertical_components(
        prefix, top, bottom, gap, offset
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
                "gap": Component(
                    VirtualControllableMotor,
                    f"{gap}",
                    components=virtualMotorComponents,
                ),
            }
        )

    if offset is not None:
        horizontalSlitComponents.update(
            {
                "offset": Component(
                    VirtualControllableMotor,
                    f"{offset}",
                    components=virtualMotorComponents,
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
    **kwargs,
) -> Device:
    """Create a slit device that can only be moved horizontally."""

    horizontalSlitComponents = _create_horizontal_components(
        prefix, left, right, gap, offset
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
    **kwargs,
) -> Device:
    """Create a slit device that can be moved vertically and horizontally."""
    slitComponents = {}

    horizontalSlitComponents = _create_horizontal_components(
        prefix, left, right, h_gap, h_offset
    )
    slitComponents.update(horizontalSlitComponents)
    verticalSlitComponents = _create_vertical_components(
        prefix, top, bottom, v_gap, v_offset
    )
    slitComponents.update(verticalSlitComponents)

    slitClass = create_device_from_components(name="slit", **slitComponents)

    return slitClass(prefix=prefix, **kwargs)
