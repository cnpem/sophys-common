from ophyd import Device, Component, EpicsSignalWithRBV, EpicsSignalRO
from ophyd.pv_positioner import PVPositionerIsClose


class MFCMixFluid(Device):
    """
    Device that aggragates the PVs with suffix `Mix` from the MFC's IOC. It's meant to be used as a `Component` for the `MFC` device.
    """

    fluid_name = Component(EpicsSignalRO, "FluidNameList", string=True, kind="config")
    fraction_type = Component(
        EpicsSignalRO, "FractionType_RBV", string=True, kind="config"
    )
    fraction = Component(EpicsSignalRO, "Fraction_RBV", kind="config")


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
    capacity = Component(EpicsSignalRO, "Capacity_RBV", kind="config")
    capacity_unit = Component(
        EpicsSignalRO, "CapacityUnit_RBV", string=True, kind="config"
    )

    fluid_name = Component(EpicsSignalRO, "FluidNameList", string=True, kind="config")
    mix = Component(MFCMixFluid, "Mix", kind="config")

    inlet_pressure = Component(EpicsSignalRO, "InletPressure_RBV", kind="config")
    outlet_pressure = Component(EpicsSignalRO, "OutletPressure_RBV", kind="config")

    temperature = Component(EpicsSignalRO, "Temperature_RBV", kind="config")

    @property
    def egu(self):
        return self.capacity_unit.get(timeout=5, connection_timeout=5)

    def __init__(self, prefix, *, name, atol=1e-2, rtol=None, timeout=10, **kwargs):
        super().__init__(
            prefix, name=name, atol=atol, rtol=rtol, timeout=timeout, **kwargs
        )
