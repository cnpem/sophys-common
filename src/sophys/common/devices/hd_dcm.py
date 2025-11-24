import time
from enum import Enum
from typing import Dict, Generator

from ophyd import (
    Component,
    Device,
    EpicsSignal,
    EpicsMotor,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    FormattedComponent,
    PVPositionerIsClose,
)
from ophyd.flyers import FlyerInterface
from ophyd.status import StatusBase, SubscriptionStatus

from .motor import ControllableMotor

FLY_KICKOFF_WAIT_TIMEOUT = 30


class ScanType(str, Enum):
    """Enumeration of supported scan types."""

    STEP_SCAN = "step_scan"
    FLY_SCAN = "fly_scan"
    EPICS = "epics"


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


class Energy(PVPositionerIsClose):
    """Positioner for controlling and reading back DCM energy.
    Default tolarance is 1eV."""

    setpoint = Component(EpicsSignal, "Energy_SP", kind="omitted")
    readback = Component(EpicsSignalRO, "GonRx_Energy_RBV", kind="hinted")
    actuate = Component(EpicsSignal, "EnergyUpdate_SP", kind="omitted")
    atol = 1e-3


class GoniometerGantry(PVPositionerIsClose):
    """Positioner for controlling the Bragg angle (gantry axis) in the DCM."""

    setpoint = Component(EpicsSignal, "GonRx_SP", kind="omitted")
    readback = Component(EpicsSignalRO, "GonRx_S_RBV", kind="hinted")
    atol = 8e-5


class BaseShs(PVPositionerIsClose):
    """Base class for HD-DCM short-stroke"""

    error_rms = FormattedComponent(
        EpicsSignalRO, "{prefix}Shs{shs_axis}_RMSError_RBV", kind="config"
    )


class UncoupledShortStroke(BaseShs):
    """Uncoupled mode positioner for a short stroke axis of the DCM Lite."""

    readback = FormattedComponent(
        EpicsSignal, "{prefix}Shs{shs_axis}_S_RBV", kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}Shs{shs_axis}_SP", kind="config"
    )

    atol = 0.02

    def __init__(self, prefix, shs_axis, **kwargs):
        """
        Parameters:
            prefix (str): PV prefix for the device.
            shs_axis (str): Axis identifier (e.g., 'Rx', 'Rz', 'Uy').
        """
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class CoupledShortStroke(BaseShs):
    """Coupled mode positioner for a short stroke axis of the DCM Lite."""

    readback = FormattedComponent(
        EpicsSignal, "{prefix}Shs{shs_axis}_Offset_RBV", kind="hinted"
    )
    setpoint = FormattedComponent(
        EpicsSignalRO, "{prefix}Shs{shs_axis}_Offset", kind="config"
    )

    def __init__(self, prefix, shs_axis, **kwargs):
        """
        Parameters:
            prefix (str): PV prefix for the device.
            shs_axis (str): Axis identifier (e.g., 'Rx', 'Rz', 'Uy').
        """
        self.shs_axis = shs_axis
        super().__init__(prefix=prefix, **kwargs)


class HardwareAcquisition(Device):
    """Device representing the configuration of hardware-based data acquisition."""

    enable_hardware_acquisition = Component(
        EpicsSignalWithRBV, "DCM01:HWAcquisition_Enable", kind="config"
    )
    hardware_acquisition_mode = Component(
        EpicsSignalWithRBV, "DCM01:HWAcquisition_Mode", kind="config"
    )
    file_name = Component(
        EpicsSignalWithRBV, "DCM01:HWAcquisition_FileName", kind="config"
    )


class StepScanByHardware(Device):
    """Device for managing execution state of a hardware-triggered step scan."""

    start = Component(
        EpicsSignal, "StepScan_Running_RBV", write_pv="StepScan_Start", kind="config"
    )
    end = Component(EpicsSignal, "StepScan_End", kind="config")
    finished = Component(EpicsSignal, "StepScan_TrajectoryComplete_RBV", kind="config")


class FlyScan(Device):
    """Device for configuring and triggering a fly scan trajectory."""

    active = Component(EpicsSignalRO, "Scan_Active_RBV", kind="config")
    amplitude = Component(EpicsSignalWithRBV, "Scan_Amplitude", kind="config")
    frequency = Component(EpicsSignalWithRBV, "Scan_Frequency", kind="config")
    period_mode = Component(EpicsSignalWithRBV, "Scan_PeriodMode", kind="config")
    periods = Component(EpicsSignalWithRBV, "Scan_Periods", kind="config")
    start = Component(EpicsSignalWithRBV, "Scan_Start", kind="config")
    end = Component(EpicsSignal, "Scan_Stop", kind="config")


class HDDCML(Device):
    """Main device abstraction for the HDDCM (High-Dynamic Double Crystal Monochromator)."""

    bragg = Component(GoniometerGantry, "DCM01:", name="bragg", kind="config")
    energy = Component(Energy, "DCM01:", name="energy", kind="hinted", limits=(4.6, 35))

    shs_uncoupled = Component(EpicsSignal, "DCM01:Shs_UncoupledMode", kind="config")
    shs_coupled = Component(EpicsSignalWithRBV, "DCM01:Shs_CoupledMode", kind="config")

    base = Component(DcmGranite, "PB01:", name="base", kind="config")

    gap_coupled = Component(CoupledShortStroke, "DCM01:", shs_axis="Uy", kind="config")
    pitch_coupled = Component(
        CoupledShortStroke, "DCM01:", shs_axis="Rx", kind="config"
    )
    roll_coupled = Component(CoupledShortStroke, "DCM01:", shs_axis="Rz", kind="config")

    gap_uncoupled = Component(
        UncoupledShortStroke, "DCM01:", shs_axis="Uy", kind="config"
    )
    pitch_uncoupled = Component(
        UncoupledShortStroke, "DCM01:", shs_axis="Rx", kind="config"
    )
    roll_uncoupled = Component(
        UncoupledShortStroke, "DCM01:", shs_axis="Rz", kind="config"
    )

    @property
    def gap(self):
        """Returns the active gap axis device, depending on coupled mode."""
        if self.shs_coupled.get():
            return self.gap_coupled
        else:
            return self.gap_uncoupled

    @property
    def pitch(self):
        """Returns the active pitch axis device, depending on coupled mode."""
        if self.shs_coupled.get():
            return self.pitch_coupled
        else:
            return self.pitch_uncoupled

    @property
    def roll(self):
        """Returns the active roll axis device, depending on coupled mode."""
        if self.shs_coupled.get():
            return self.roll_coupled
        else:
            return self.roll_uncoupled

    def __init__(self, prefix="", tatu=None, **kwargs):
        """
        Parameters:
            prefix (str): PV prefix.
            tatu (TatuDevice): Optional reference to a Tatu Device controller object.
        """
        self.tatu = tatu
        super().__init__(prefix, **kwargs)


class _BaseDCMFlyerCommon:
    """Shared utility methods for both fly and step flyer mixins for HDDCMs."""

    def _describe_from_config(self, config_attr_name):
        """Return the describe dict for a configured scan device."""
        descriptor = {"dcm": {}}
        for attr in getattr(self, config_attr_name).configuration_attrs:
            comp = getattr(getattr(self, config_attr_name), attr)
            descriptor["dcm"].update(comp.describe())
        return descriptor

    def _collect_from_config(self, config_attr_name):
        """Return the collected data and timestamps from the scan configuration."""
        data = {}
        timestamps = {}
        for attr in getattr(self, config_attr_name).configuration_attrs:
            comp = getattr(getattr(self, config_attr_name), attr)
            comp_name = comp.name
            comp_read = comp.read()[comp_name]
            data[comp_name] = comp_read["value"]
            timestamps[comp_name] = comp_read["timestamp"]
        return [{"time": time.time(), "data": data, "timestamps": timestamps}]


class RequiresTatu:
    """Mixin that enforces the presence of a Tatu instance."""

    def _require_tatu(self):
        if not getattr(self, "tatu", None):
            raise RuntimeError(
                f"{self.__class__.__name__} requires a valid 'tatu' instance."
            )


class _BaseFlyerStep(
    HDDCML, HardwareAcquisition, FlyerInterface, _BaseDCMFlyerCommon, RequiresTatu
):
    """Base class for step scan flyer, combining DCM device and acquisition logic."""

    def describe_collect(self) -> Dict[str, Dict]:
        return self._describe_from_config("step_scan")

    def collect(self) -> Generator[Dict, None, None]:
        return self._collect_from_config("step_scan")


class _BaseFlyer(
    HDDCML, HardwareAcquisition, FlyerInterface, _BaseDCMFlyerCommon, RequiresTatu
):
    """Base class for fly scan flyer, combining DCM device and acquisition logic."""

    def describe_collect(self) -> Dict[str, Dict]:
        return self._describe_from_config("fly_scan")

    def collect(self) -> Generator[Dict, None, None]:
        return self._collect_from_config("fly_scan")


class _HDDCMLFly(_BaseFlyer):
    """Fly scan mode implementation for HDDCML."""

    fly_scan = Component(FlyScan, "DCM01:")

    def _check_fly_scan(self, *, value, **kwargs):
        return value == 1

    def kickoff(self) -> StatusBase:
        self._require_tatu()
        self.fly_scan.start.set(False).wait(10)
        self.fly_scan.start.set(True).wait(FLY_KICKOFF_WAIT_TIMEOUT)
        return self.tatu.activate.set(True)

    def complete(self) -> StatusBase:
        return SubscriptionStatus(self.fly_scan.active, self._check_fly_scan)

    def pause(self) -> None:
        self._require_tatu()
        self.enable_hardware_acquisition.set(False).wait(10)
        return self.tatu.pause()

    def resume(self) -> None:
        self._require_tatu()
        self.enable_hardware_acquisition.set(True).wait(10)
        return self.tatu.resume()


class _HDDCMLStep(_BaseFlyerStep):
    """Step scan mode implementation for HDDCML."""

    step_scan = Component(StepScanByHardware, "DCM01:")

    def _check_step_scan(self, *, value, **kwargs):
        return value == 1

    def kickoff(self) -> StatusBase:
        self._require_tatu()
        self.step_scan.end.set(True)
        self.step_scan.start.set(False).wait(10)
        self.step_scan.start.set(True).wait(FLY_KICKOFF_WAIT_TIMEOUT)
        return self.tatu.activate.set(True)

    def complete(self) -> StatusBase:
        return SubscriptionStatus(self.step_scan.finished, self._check_step_scan)

    def pause(self) -> None:
        self._require_tatu()
        self.enable_hardware_acquisition.set(False).wait(10)
        return self.tatu.pause()

    def resume(self) -> None:
        self._require_tatu()
        self.enable_hardware_acquisition.set(True).wait(10)
        return self.tatu.resume()


class DCMFactory:
    """Factory class for creating DCM scan mode objects."""

    @staticmethod
    def create(scan_mode: ScanType, prefix: str, name: str, **kwargs) -> HDDCML:
        """
        Create an HDDCML object with behavior according to the scan mode.
        How to use:
            dcm = DCMFactory.create(ScanType.FLY_SCAN, prefix='...', name='my_dcm')
            if Tatu is needed, pass tatu=... as a keyword argument.
        Parameters:
            scan_mode (ScanType): Desired scan mode (step, fly, epics).
            prefix (str): PV prefix for the device.
            name (str): Device name.

        Returns:
            HDDCML or subclass: Appropriate scan mode implementation.
        """
        if scan_mode == ScanType.STEP_SCAN:
            return _HDDCMLStep(prefix, name="__" + name + "_step", **kwargs)
        elif scan_mode == ScanType.FLY_SCAN:
            return _HDDCMLFly(prefix, name="__" + name + "_fly", **kwargs)
        elif scan_mode == ScanType.EPICS:
            return HDDCML(prefix, name=name, **kwargs)
        else:
            raise ValueError(
                "Invalid scan mode, available modes are: step_scan, fly_scan, epics"
            )
