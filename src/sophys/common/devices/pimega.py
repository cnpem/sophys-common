#!/usr/bin/env python3
from time import time
from ophyd import (
    ADComponent,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    SingleTrigger,
    Device
)
from ophyd.status import SubscriptionStatus
from ophyd.flyers import FlyerInterface
from ophyd.areadetector.detectors import DetectorBase
from .cam import CamBase_V33


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
    """
        Handle the necessary PVs to start and stop the pimega acquisition.
    """

    acquire = ADComponent(EpicsSignalWithRBV, "Acquire")
    capture = ADComponent(EpicsSignalWithRBV, "Capture")

    def start(self):
        # Start backend
        self.capture.set(1)
        # Send start signal to chips. This also checks that the Capture one has finished.
        return self.acquire.set(1)

    def stop(self):
        # Stop both the backend and the detector
        self.acquire.set(0).wait(timeout=30.0)
        # In practice, this does nothing. But it doesn't hurt anyone :-)
        self.capture.set(0).wait()


class PimegaFilePath(EpicsSignalWithRBV):
    """
        Add '/' at the end of the file path if it isn't already specified.
    """

    def set(self, value: str, **kwargs):
        if len(value) > 0:
            if value[-1] != '/':
                value += '/'
        return super().set(value, **kwargs)


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
    processed_acquisition_counter = ADComponent(EpicsSignalRO, "ProcessedAcquisitionCounter_RBV")
    num_captured = ADComponent(EpicsSignalRO, "NumCaptured_RBV")
    
    dac = ADComponent(Digital2AnalogConverter, "DAC_")

    file_name = ADComponent(EpicsSignalWithRBV, "FileName", string=True)
    file_path = ADComponent(PimegaFilePath, "FilePath", string=True)
    file_path_exists = ADComponent(EpicsSignalRO, "FilePathExists_RBV", string=True)
    file_number = ADComponent(EpicsSignalWithRBV, "FileNumber")
    file_template = ADComponent(EpicsSignalWithRBV, "FileTemplate", string=True)
    auto_increment = ADComponent(EpicsSignalWithRBV, "AutoIncrement", string=True)
    auto_save = ADComponent(EpicsSignalWithRBV, "AutoSave", string=True)

    def __init__(self, prefix, name, **kwargs):
        super(PimegaCam, self).__init__(prefix, name=name, **kwargs)


class PimegaDetector(DetectorBase):
    cam = ADComponent(PimegaCam, "cam1:", kind="config")


class Pimega(SingleTrigger, PimegaDetector):
    def __init__(self, name, prefix, **kwargs):
        super(Pimega, self).__init__(prefix, name=name, **kwargs)


class PimegaFlyScan(Pimega, FlyerInterface):

    def kickoff(self):
        return self.cam.acquire.start()

    def fly_scan_complete(self, **kwargs):
        """
        Wait for the Pimega device to acquire and save all the predetermined quantity
        of images.
        """
        num2capture = self.cam.num_capture.get()
        num_captured = self.cam.num_captured.get()

        if num2capture == num_captured:
            return True
        return False

    def complete(self):
        return SubscriptionStatus(self.cam, callback=self.fly_scan_complete)
    
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

        return [
            {
                "time": time(),
                "data": data,
                "timestamps": timestamps
            }
        ]