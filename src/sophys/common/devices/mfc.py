from ophyd import Device, Component, EpicsSignalWithRBV, EpicsSignalRO, EpicsSignal
from bluesky.utils import FailedStatus
from enum import StrEnum
from ophyd.pv_positioner import PVPositionerDone


class MixFractionType(StrEnum):
    VOLUME_FRACTION = "Volume fraction"
    MASS_FRACTION = "Mass fraction"
    MOLE_FRACTION = "Mole fraction"


class InitResetType(StrEnum):
    UNLOCKED = "unlocked"
    LOCKED = "locked"


class MFCFlowValueError(FailedStatus):
    def __init__(self, value):
        super().__init__(
            f"The flow value {value} is out of range. The allowed range is between 0 and 32000"
        )


class MFCMixFluid(Device):
    fluid_name_list = Component(
        EpicsSignal, "FluidNameList", string=True, kind="config"
    )
    fluid_name = Component(EpicsSignalRO, "FluidName_RBV", string=True, kind="config")
    fraction_type = Component(
        EpicsSignalWithRBV, "FractionType", string=True, kind="config"
    )
    fraction = Component(EpicsSignalWithRBV, "Fraction", kind="config")


class MFC(PVPositionerDone):
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
