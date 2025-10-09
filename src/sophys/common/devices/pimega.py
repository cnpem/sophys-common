#!/usr/bin/env python3
from time import time
from ophyd import (
    ADComponent,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    Device,
)
from ophyd.status import SubscriptionStatus
from ophyd.flyers import FlyerInterface
from ophyd.utils.epics_pvs import AlarmSeverity
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.paths import EpicsPathSignal
from ophyd.areadetector.trigger_mixins import ADTriggerStatus, SingleTrigger
from .cam import CamBase_V33

from ..utils.status import PremadeStatus


class Digital2AnalogConverter(Device):

    cas = ADComponent(EpicsSignalWithRBV, "CAS")
    delay = ADComponent(EpicsSignalWithRBV, "Delay")
    disc = ADComponent(EpicsSignalWithRBV, "Disc")
    disch = ADComponent(EpicsSignalWithRBV, "DiscH")
    discl = ADComponent(EpicsSignalWithRBV, "DiscL")
    discls = ADComponent(EpicsSignalWithRBV, "DiscLS")
    fbk = ADComponent(EpicsSignalWithRBV, "FBK")
    gnd = ADComponent(EpicsSignalWithRBV, "GND")
    ikrum = ADComponent(EpicsSignalWithRBV, "IKrum")
    preamp = ADComponent(EpicsSignalWithRBV, "Preamp")
    RPZ = ADComponent(EpicsSignalWithRBV, "RPZ")
    shaper = ADComponent(EpicsSignalWithRBV, "Shaper")
    threshold0 = ADComponent(EpicsSignalWithRBV, "ThresholdEnergy0")
    threshold1 = ADComponent(EpicsSignalWithRBV, "ThresholdEnergy1")
    tp_buffer_in = ADComponent(EpicsSignalWithRBV, "TPBufferIn")
    tp_buffer_out = ADComponent(EpicsSignalWithRBV, "TPBufferOut")
    tpref = ADComponent(EpicsSignalWithRBV, "TPRef")
    tpref_a = ADComponent(EpicsSignalWithRBV, "TPRefA")
    tpref_b = ADComponent(EpicsSignalWithRBV, "TPRefB")


class PimegaAcquire(Device):
    """Handle the necessary PVs to start and stop the pimega acquisition."""

    SUB_VALUE = "value"
    _default_sub = SUB_VALUE

    acquire = ADComponent(EpicsSignalWithRBV, "Acquire")
    capture = ADComponent(EpicsSignalWithRBV, "Capture")

    def subscribe(self, callback, event_type=None, run=True):
        return self.acquire.subscribe(callback, event_type, run)

    def unsubscribe(self, cid):
        return self.acquire.unsubscribe(cid)

    def check_value_zero(self, value):
        # We can be called either with an integer, or an automatically
        # generated namedtuple with both acquire and capture desired values.
        return value == 0 or (isinstance(value, tuple) and value.acquire == 0)

    def set(self, value, **kwargs):
        if self.check_value_zero(value):
            # Stop both the backend and the detector
            self.acquire.set(0).wait(timeout=30.0)
            # In practice, this does nothing. But it doesn't hurt anyone :-)
            return self.capture.set(0)
        else:
            # Start backend
            self.capture.set(1, **kwargs).wait(timeout=30.0)
            # Send start signal to chips. This also checks that the Capture one has finished.
            return self.acquire.set(1, **kwargs)

    # Needed for code calling put directly (namely SingleTrigger)
    def put(self, value, **kwargs):
        if self.check_value_zero(value):
            # Stop both the backend and the detector
            self.acquire.put(0, **kwargs)
            # In practice, this does nothing. But it doesn't hurt anyone :-)
            self.capture.put(0, **kwargs)
        else:
            # Start backend
            self.capture.put(1, **kwargs)
            # Send start signal to chips. This also checks that the Capture one has finished.
            self.acquire.put(1, **kwargs)


class PimegaCam(CamBase_V33):

    magic_start = ADComponent(EpicsSignal, "MagicStart")
    trigger_mode = ADComponent(EpicsSignalWithRBV, "TriggerMode", string=True)
    acquire = ADComponent(PimegaAcquire, "")
    num_capture = ADComponent(EpicsSignalWithRBV, "NumCapture")
    num_exposures = ADComponent(EpicsSignalWithRBV, "NumExposures")

    acquire_time = ADComponent(EpicsSignalWithRBV, "AcquireTime")
    acquire_period = ADComponent(EpicsSignalWithRBV, "AcquirePeriod")

    medipix_mode = ADComponent(EpicsSignalWithRBV, "MedipixMode")

    detector_state = ADComponent(EpicsSignalRO, "DetectorState_RBV")
    processed_acquisition_counter = ADComponent(
        EpicsSignalRO, "ProcessedAcquisitionCounter_RBV"
    )
    num_captured = ADComponent(EpicsSignalRO, "NumCaptured_RBV")

    dac = ADComponent(Digital2AnalogConverter, "DAC_")

    file_name = ADComponent(EpicsSignalWithRBV, "FileName", string=True)
    file_path = ADComponent(
        EpicsPathSignal, "FilePath", path_semantics="posix", string=True
    )
    file_path_exists = ADComponent(EpicsSignalRO, "FilePathExists_RBV", string=True)
    file_number = ADComponent(EpicsSignalWithRBV, "FileNumber")
    file_template = ADComponent(EpicsSignalWithRBV, "FileTemplate", string=True)
    auto_increment = ADComponent(EpicsSignalWithRBV, "AutoIncrement", string=True)
    auto_save = ADComponent(EpicsSignalWithRBV, "AutoSave", string=True)

    ioc_status_message = ADComponent(
        EpicsSignalRO, "IOCStatusMessage_RBV", string=True, kind="omitted"
    )
    backend_status_message = ADComponent(
        EpicsSignalRO, "ServerStatusMessage_RBV", string=True, kind="omitted"
    )

    def __init__(self, prefix, name, **kwargs):
        super(PimegaCam, self).__init__(prefix, name=name, **kwargs)


class PimegaDetector(DetectorBase):
    cam = ADComponent(PimegaCam, "cam1:", kind="config")


class PimegaTriggerStatus(ADTriggerStatus):
    def __str__(self):
        # NOTE: Arbitrary timeout, just in case something goes horribly wrong.
        return "\n".join(self.exception(timeout=2.0).args)


class PimegaStartAcquisitionException(Exception):
    pass


class Pimega(SingleTrigger, PimegaDetector):
    _status_type = PimegaTriggerStatus

    def __init__(self, name, prefix, **kwargs):
        super(Pimega, self).__init__(prefix, name=name, **kwargs)

    def stage(self):
        # Make sure the current acquisition status is 'Done'
        self._acquisition_signal.set(0).wait(timeout=30.0)

        self._acquisition_signal.subscribe(
            self._acquire_setpoint_changed, EpicsSignal.SUB_SETPOINT
        )

        return super().stage()

    def unstage(self):
        super().unstage()

        self._acquisition_signal.unsubscribe(self._acquire_setpoint_changed)

    def _acquire_setpoint_changed(self, value, severity, **kwargs):
        if self._status is None or self._status.done:
            return

        if value == 1 and severity == AlarmSeverity.INVALID:
            exc_messages = (
                "An alarm has been raised by the IOC, with the following status messages:",
                f"IOC: {self.cam.ioc_status_message.get()}",
                f"Backend: {self.cam.backend_status_message.get()}",
            )
            exc = PimegaStartAcquisitionException(*exc_messages)
            self._status.set_exception(exc)
            return

    def pause(self):
        super().pause()
        self.cam.acquire.set(0).wait()

    def stop(self):
        super().stop()
        self.cam.acquire.set(0).wait()


class PimegaFlyScan(Pimega, FlyerInterface):

    # 1 week timeout
    complete_timeout = 604800

    def kickoff(self):
        return self.cam.acquire.set(1, timeout=15)

    def _fly_scan_complete(self, **kwargs):
        """
        Wait for the Pimega device to acquire and save all the predetermined quantity
        of images.
        """
        num2capture = self.cam.num_capture.get()
        num_captured = self.cam.num_captured.get()

        return num2capture == num_captured

    def complete(self):
        return SubscriptionStatus(
            self.cam.num_captured,
            callback=self._fly_scan_complete,
            timeout=self.complete_timeout,
        )

    def describe_collect(self):
        descriptor = {"pimega": {}}
        descriptor["pimega"].update(self.cam.file_name.describe())
        descriptor["pimega"].update(self.cam.file_path.describe())
        return descriptor

    def collect(self):
        data = {}
        timestamps = {}
        for device in [self.cam.file_name, self.cam.file_path]:
            dev_name = device.name
            dev_info = device.read()[dev_name]
            data.update({dev_name: dev_info["value"]})
            timestamps.update({dev_name: dev_info["timestamp"]})

        return [{"time": time(), "data": data, "timestamps": timestamps}]
