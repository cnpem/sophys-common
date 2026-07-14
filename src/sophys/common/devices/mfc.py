from ophyd import (
    Device,
    Component,
    EpicsSignalWithRBV,
    EpicsSignalRO,
)  # numpydoc ignore=GL08
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
    Bronkhorst's Prestige series Mass Flow Controller Ophyd device.

    This device has the `PVPositionerIsClose` interface. The `atol` and `timeout` properties
    have the defaults `1e-2` and `10` respectively. These can be changed for each equipment
    or use case. The `egu` is overwritten to show the equipment's capacity unit.

    Parameters
    ----------
    prefix : str
        The device prefix used for all sub-positioners. This is optional as it
        may be desirable to specify full PV names for PVPositioners.
    name : str
        The device name.
    atol : float, default: 1e-2
        A measure of absolute tolerance.
    rtol : float, optional
        A measure of relative tolerance.
    timeout : float, default: 10
        The default timeout to use for motion requests, in seconds.
    **kwargs
        Extra keyword arguments passed to `PVPositionerIsClose`.

    See Also
    --------
    ophyd.pv_positioner.PVPositionerIsClose: Base class for `PVPositioner` that updates done status based on np.isclose.
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
    def egu(self):  # numpydoc ignore=GL08
        return self.capacity_unit.get(timeout=5, connection_timeout=5)

    def __init__(
        self, prefix, *, name, atol=1e-2, rtol=None, timeout=10, **kwargs
    ):  # numpydoc ignore=GL08
        super().__init__(
            prefix, name=name, atol=atol, rtol=rtol, timeout=timeout, **kwargs
        )
