from sophys.common.devices.motor import (
    ControllableMotor,
    VirtualControllableMotorBaseClass,
)
from sophys.common.devices.slit import Slit, KinematicSlit, HorizontalSlit, VerticalSlit


def test_simple_horizontal_slit(soft_ioc):
    slit = HorizontalSlit(soft_ioc, "SLIT:LEFT", "SLIT:RIGHT", name="test_slit")

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)


def test_horizontal_slit_with_real_gap_offset(soft_ioc):
    slit = HorizontalSlit(
        soft_ioc,
        "SLIT:LEFT",
        "SLIT:RIGHT",
        gap="SLIT:HGAP",
        offset="SLIT:HOFF",
        has_kinematic=False,
        name="test_slit",
    )

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, ControllableMotor)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, ControllableMotor)
    slit.horizontal_offset.wait_for_connection(2.0)


def test_horizontal_slit_with_kinematic_gap_offset(soft_ioc):
    slit = HorizontalSlit(
        soft_ioc,
        "SLIT:LEFT",
        "SLIT:RIGHT",
        gap="SLIT:HGAP",
        offset="SLIT:HOFF",
        has_kinematic=True,
        name="test_slit",
    )

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, VirtualControllableMotorBaseClass)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, VirtualControllableMotorBaseClass)
    slit.horizontal_offset.wait_for_connection(2.0)


def test_simple_vertical_slit(soft_ioc):
    slit = VerticalSlit(soft_ioc, "SLIT:TOP", "SLIT:BOTTOM", name="test_slit")

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)


def test_vertical_slit_with_real_gap_offset(soft_ioc):
    slit = VerticalSlit(
        soft_ioc,
        "SLIT:TOP",
        "SLIT:BOTTOM",
        gap="SLIT:VGAP",
        offset="SLIT:VOFF",
        has_kinematic=False,
        name="test_slit",
    )

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, ControllableMotor)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, ControllableMotor)
    slit.vertical_offset.wait_for_connection(2.0)


def test_vertical_slit_with_kinematic_gap_offset(soft_ioc):
    slit = VerticalSlit(
        soft_ioc,
        "SLIT:TOP",
        "SLIT:BOTTOM",
        gap="SLIT:VGAP",
        offset="SLIT:VOFF",
        has_kinematic=True,
        name="test_slit",
    )

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, VirtualControllableMotorBaseClass)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, VirtualControllableMotorBaseClass)
    slit.vertical_offset.wait_for_connection(2.0)


def test_simple_slit(soft_ioc):
    slit = Slit(
        soft_ioc, "SLIT:TOP", "SLIT:BOTTOM", "SLIT:LEFT", "SLIT:RIGHT", name="test_slit"
    )

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)


def test_slit_with_real_gap_offset(soft_ioc):
    slit = Slit(
        soft_ioc,
        "SLIT:TOP",
        "SLIT:BOTTOM",
        "SLIT:LEFT",
        "SLIT:RIGHT",
        v_gap="SLIT:VGAP",
        v_offset="SLIT:VOFF",
        h_gap="SLIT:HGAP",
        h_offset="SLIT:HOFF",
        has_kinematic=False,
        name="test_slit",
    )

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, ControllableMotor)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, ControllableMotor)
    slit.vertical_offset.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, ControllableMotor)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, ControllableMotor)
    slit.horizontal_offset.wait_for_connection(2.0)


def test_slit_with_kinematic_gap_offset(soft_ioc):
    slit = Slit(
        soft_ioc,
        "SLIT:TOP",
        "SLIT:BOTTOM",
        "SLIT:LEFT",
        "SLIT:RIGHT",
        v_gap="SLIT:VGAP",
        v_offset="SLIT:VOFF",
        h_gap="SLIT:HGAP",
        h_offset="SLIT:HOFF",
        has_kinematic=True,
        name="test_slit",
    )

    assert hasattr(slit, "top")
    assert isinstance(slit.top, ControllableMotor)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, ControllableMotor)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "left")
    assert isinstance(slit.left, ControllableMotor)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, ControllableMotor)
    slit.right.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, VirtualControllableMotorBaseClass)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, VirtualControllableMotorBaseClass)
    slit.vertical_offset.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, VirtualControllableMotorBaseClass)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, VirtualControllableMotorBaseClass)
    slit.horizontal_offset.wait_for_connection(2.0)


def test_simple_kinematic_slit(soft_ioc):
    slit = KinematicSlit(
        soft_ioc, "SLIT:VGAP", "SLIT:VOFF", "SLIT:HGAP", "SLIT:HOFF", name="test_slit"
    )

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, ControllableMotor)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, ControllableMotor)
    slit.vertical_offset.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, ControllableMotor)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, ControllableMotor)
    slit.horizontal_offset.wait_for_connection(2.0)


def test_kinematic_slit_with_virtual_axes(soft_ioc):
    slit = KinematicSlit(
        soft_ioc,
        "SLIT:VGAP",
        "SLIT:VOFF",
        "SLIT:HGAP",
        "SLIT:HOFF",
        top="SLIT:TOP",
        bottom="SLIT:BOTTOM",
        left="SLIT:LEFT",
        right="SLIT:RIGHT",
        name="test_slit",
    )

    assert hasattr(slit, "vertical_gap")
    assert isinstance(slit.vertical_gap, ControllableMotor)
    slit.vertical_gap.wait_for_connection(2.0)

    assert hasattr(slit, "vertical_offset")
    assert isinstance(slit.vertical_offset, ControllableMotor)
    slit.vertical_offset.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_gap")
    assert isinstance(slit.horizontal_gap, ControllableMotor)
    slit.horizontal_gap.wait_for_connection(2.0)

    assert hasattr(slit, "horizontal_offset")
    assert isinstance(slit.horizontal_offset, ControllableMotor)
    slit.horizontal_offset.wait_for_connection(2.0)

    assert hasattr(slit, "top")
    assert isinstance(slit.top, VirtualControllableMotorBaseClass)
    slit.top.wait_for_connection(2.0)

    assert hasattr(slit, "bottom")
    assert isinstance(slit.bottom, VirtualControllableMotorBaseClass)
    slit.bottom.wait_for_connection(2.0)

    assert hasattr(slit, "left")
    assert isinstance(slit.left, VirtualControllableMotorBaseClass)
    slit.left.wait_for_connection(2.0)

    assert hasattr(slit, "right")
    assert isinstance(slit.right, VirtualControllableMotorBaseClass)
    slit.right.wait_for_connection(2.0)
