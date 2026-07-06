from ophyd import Device, Component, EpicsSignalWithRBV, EpicsSignalRO, EpicsSignal
from enum import StrEnum
from ophyd.pv_positioner import PVPositionerIsClose


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


class MFC(PVPositionerIsClose):
    """
    Bronkhorst's Prestige series Mass Flow Controller Ophyd device, with the `PVPositionerIsClose` interface.
    """

    raw_setpoint = Component(EpicsSignalWithRBV, "Setpoint", kind="config")
    raw_readback = Component(
        EpicsSignalRO, "Measure_RBV", kind="config"
    )  # Dimensionless metered value of flow

    readback = Component(EpicsSignalRO, "FloatMeasure_RBV", kind="hinted")
    setpoint = Component(EpicsSignalWithRBV, "FloatSetpoint", kind="config")
    actuate = Component(EpicsSignalWithRBV, "EnableSetpoint", kind="config")
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

    @property
    def egu(self):
        return self.capacity_unit.get(timeout=5, connection_timeout=5)
