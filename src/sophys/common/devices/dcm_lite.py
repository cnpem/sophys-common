from ophyd import (
    Component,
    FormattedComponent,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    PVPositionerIsClose,
    PVPositionerPC,
    EpicsMotor,
    EpicsSignalWithRBV,
)
from .motor import ControllableMotor

from warnings import deprecated

# warnings.warn(
#    "Importing DcmLite and its components is deprecated"
#    "The new recommended class can be instatiated using the factory provided."
#    "New module located at sophys.common.devices.hd_dcm", stacklevel=2)


class DcmGranite(Device):
    """
    Device for controlling the DCM Granite.
    """

    leveler1 = Component(ControllableMotor, "m1")
    leveler2 = Component(ControllableMotor, "m2")
    leveler3 = Component(ControllableMotor, "m3")

    u_x = Component(ControllableMotor, "m4")

    spindle_x_plus = Component(ControllableMotor, "m5")
    spindle_x_minus = Component(ControllableMotor, "m6")

    granite_ux = Component(EpicsMotor, "CS2:m7")
    granite_ry = Component(EpicsMotor, "CS2:m2")
    granite_uz = Component(EpicsMotor, "CS2:m9")

    leveler_rx = Component(EpicsMotor, "CS1:m1")
    leveler_rz = Component(EpicsMotor, "CS1:m3")
    leveler_uy = Component(EpicsMotor, "CS1:m8")


class Goniometer(PVPositionerIsClose):
    """
    Device for controlling one Goniometer of the DCM Lite.
    """

    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}GonRx{device_number}_SP_RBV", kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}GonRx{device_number}_SP", kind="config"
    )
    actuate = Component(EpicsSignal, "GonRxUpdate_SP", kind="omitted")

    stopped = FormattedComponent(
        EpicsSignalRO, "{prefix}GonRx{device_number}_DesVelZero_RBV", kind="omitted"
    )
    low_limit = FormattedComponent(
        EpicsSignalRO, "{prefix}GonRx{device_number}_MinusLimit_RBV", kind="omitted"
    )
    high_limit = FormattedComponent(
        EpicsSignalRO, "{prefix}GonRx{device_number}_PlusLimit_RBV", kind="omitted"
    )

    def __init__(self, prefix, device_number, **kwargs):
        self.device_number = device_number
        super().__init__(prefix=prefix, **kwargs)


class UncoupledShortStroke(PVPositionerIsClose):
    """
    Device for controlling one axis of the Short Stroke of the DCM Lite.
    """

    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}Shs{shs_axis}_S_RBV", kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}Shs{shs_axis}_SP", kind="config"
    )
    actuate = FormattedComponent(
        EpicsSignal, "{prefix}ShsUpdate_{shs_axis}_SP", kind="omitted"
    )

    def __init__(self, prefix, shs_axis, **kwargs):
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class CoupledShortStroke(PVPositionerIsClose):
    """
    Device for controlling one axis of the Short Stroke of the DCM Lite.
    """

    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}Shs{shs_axis}_Offset_RBV", kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}Shs{shs_axis}_Offset", kind="config"
    )
    actuate = FormattedComponent(
        EpicsSignal, "{prefix}ShsUpdate_{shs_axis}_SP", kind="omitted"
    )

    def __init__(self, prefix, shs_axis, **kwargs):
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class ShortStroke(Device):
    """
    Device for controlling all the axis of the Short Stroke of the DCM Lite.
    """

    gap_uncoupled = Component(UncoupledShortStroke, "", shs_axis="Uy")
    pitch_uncoupled = Component(UncoupledShortStroke, "", shs_axis="Rx")
    roll_uncoupled = Component(UncoupledShortStroke, "", shs_axis="Rz")


class DcmEnergy(PVPositionerPC):
    """
    Device for controlling the DCM Energy.
    """

    setpoint = Component(EpicsSignal, "_SP", kind="config")
    actuate = Component(EpicsSignal, "Update_SP", kind="omitted")


class DcmScan(Device):
    """
    Device that groups all the PVs related to the energy scan of the DCM Lite.
    """

    start = Component(EpicsSignal, "Start")
    active = Component(EpicsSignalRO, "Active_RBV")

    time_mode = Component(EpicsSignalWithRBV, "PeriodMode", string=True)
    frequency = Component(EpicsSignalWithRBV, "Frequency")
    amplitude = Component(EpicsSignalWithRBV, "Amplitude")
    periods_tukey = Component(EpicsSignalWithRBV, "TukeyPeriods")
    periods_scan = Component(EpicsSignalWithRBV, "Periods")


@deprecated("Deprecated use the HD DCM class from sophys.common.devices.hd_dcm instead")
class DcmLite(Device):
    """
    Device for controlling the DCM Lite monochromator.
    """

    gonio1 = Component(Goniometer, "DCM01:", device_number="1")
    gonio2 = Component(Goniometer, "DCM01:", device_number="2")
    short_stroke = Component(ShortStroke, "DCM01:")

    granite = Component(DcmGranite, "PB01:")

    energy = Component(DcmEnergy, "DCM01:Energy")
    scan = Component(DcmScan, "DCM01:Scan_")
