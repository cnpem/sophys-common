from ophyd import Device, Component, EpicsSignalWithRBV, EpicsSignalRO, EpicsSignal
from enum import StrEnum
from ophyd.pv_positioner import PVPositionerDone


class MixFractionType(StrEnum):
    """Enumeration of options for the `MixFractionType` PV."""

    VOLUME_FRACTION = "Volume fraction"
    MASS_FRACTION = "Mass fraction"
    MOLE_FRACTION = "Mole fraction"


class InitResetType(StrEnum):
    """Enumeration of options for the `InitReset` PV."""

    UNLOCKED = "unlocked"
    LOCKED = "locked"


class MFCMixFluid(Device):
    """
    Device that aggragates the PVs with suffix `Mix` from the MFC's IOC. It's meant to be used as a `Component` for the `MFC` device.
    """

    fluid_name_list = Component(
        EpicsSignal, "FluidNameList", string=True, kind="config"
    )
    fluid_name = Component(EpicsSignalRO, "FluidName_RBV", string=True, kind="config")
    fraction_type = Component(
        EpicsSignalWithRBV, "FractionType", string=True, kind="config"
    )
    fraction = Component(EpicsSignalWithRBV, "Fraction", kind="config")


class MFC(PVPositionerDone):
    """
    Bronkhorst's Prestige series Mass Flow Controller Ophyd device, with the `PVPositioner` interface.
    This class is initialized with its flow limits set to (0, 32000), following the manufacturer's recommendation.
    """

    setpoint = Component(EpicsSignalWithRBV, "Setpoint", kind="config")
    readback = Component(
        EpicsSignalRO, "Measure_RBV", kind="hinted"
    )  # Dimensionless metered value of flow

    fmeasure = Component(EpicsSignalRO, "FloatMeasure_RBV", kind="hinted")
    fsetpoint = Component(EpicsSignalWithRBV, "FloatSetpoint", kind="config")
    capacity = Component(EpicsSignalWithRBV, "Capacity", kind="config")
    capacity_unit = Component(
        EpicsSignalWithRBV, "CapacityUnit", string=True, kind="config"
    )

    fluid_name = Component(EpicsSignalRO, "FluidName_RBV", string=True, kind="config")
    fluid_name_list = Component(
        EpicsSignal, "FluidNameList", string=True, kind="config"
    )
    mix = Component(MFCMixFluid, "Mix", kind="config")

    inlet_pressure = Component(EpicsSignalWithRBV, "InletPressure", kind="config")
    outlet_pressure = Component(EpicsSignalWithRBV, "OutletPressure", kind="config")

    temperature = Component(EpicsSignalRO, "Temperature_RBV", kind="config")

    init_reset = Component(EpicsSignalWithRBV, "InitReset", string=True, kind="config")

    def __init__(self, *args, limits=(0, 32000), **kwargs):
        super().__init__(*args, limits=limits, **kwargs)
