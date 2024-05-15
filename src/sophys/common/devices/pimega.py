#!/usr/bin/env python3

from ophyd import (
    ADComponent,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    EpicsSignalWithRBV,
    EpicsSignalNoValidation,
    Kind,
    SingleTrigger,
)
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.detectors import DetectorBase


class PimegaCam(CamBase):

    magic_start = ADComponent(EpicsSignal, "MagicStart")
    acquire_capture = ADComponent(EpicsSignal, "AcquireCapture")
    num_capture = ADComponent(EpicsSignalWithRBV, "NumCapture")

    medipix_mode = ADComponent(EpicsSignalWithRBV, "MedipixMode")

    detector_state = ADComponent(EpicsSignalRO, "DetectorState_RBV")
    processed_acquisition_counter = ADComponent(EpicsSignalRO, "ProcessedAcquisitionCounter_RBV")
    num_captured = ADComponent(EpicsSignalRO, "NumCaptured_RBV")

    dac_cas = ADComponent(EpicsSignalWithRBV, "DAC_CAS")
    dac_delay = ADComponent(EpicsSignalWithRBV, "DAC_Delay")
    dac_disc = ADComponent(EpicsSignalWithRBV, "DAC_Disc")
    dac_disch = ADComponent(EpicsSignalWithRBV, "DAC_DiscH")
    dac_discl = ADComponent(EpicsSignalWithRBV, "DAC_DiscL")
    dac_discls = ADComponent(EpicsSignalWithRBV, "DAC_DiscLS")
    dac_fbk = ADComponent(EpicsSignalWithRBV, "DAC_FBK")
    dac_gnd = ADComponent(EpicsSignalWithRBV, "DAC_GND")
    dac_ikrum = ADComponent(EpicsSignalWithRBV, "DAC_IKrum")
    dac_preamp = ADComponent(EpicsSignalWithRBV, "DAC_Preamp")
    dac_RPZ = ADComponent(EpicsSignalWithRBV, "DAC_RPZ")
    dac_shaper = ADComponent(EpicsSignalWithRBV, "DAC_Shaper")
    dac_threshold0 = ADComponent(EpicsSignalWithRBV, "DAC_ThresholdEnergy0")
    dac_threshold1 = ADComponent(EpicsSignalWithRBV, "DAC_ThresholdEnergy1")
    dac_tp_buffer_in = ADComponent(EpicsSignalWithRBV, "DAC_TPBufferIn")
    dac_tp_buffer_out = ADComponent(EpicsSignalWithRBV, "DAC_TPBufferOut")
    dac_tpref = ADComponent(EpicsSignalWithRBV, "DAC_TPRef")
    dac_tpref_a = ADComponent(EpicsSignalWithRBV, "DAC_TPRefA")
    dac_tpref_b = ADComponent(EpicsSignalWithRBV, "DAC_TPRefB")

    file_name = ADComponent(EpicsSignalWithRBV, "FileName")
    file_path = ADComponent(EpicsSignalWithRBV, "FilePath")
    file_number = ADComponent(EpicsSignalWithRBV, "FileNumber")
    file_template = ADComponent(EpicsSignalWithRBV, "FileTemplate")
    auto_increment = ADComponent(EpicsSignalWithRBV, "AutoIncrement")
    auto_save = ADComponent(EpicsSignalWithRBV, "AutoSave")

    def __init__(self, prefix, name, **kwargs):
        super(PimegaCam, self).__init__(prefix, name=name, **kwargs)


class PimegaDetector(DetectorBase):
    cam = ADComponent(PimegaCam, "cam1:", kind="config")


class Pimega(SingleTrigger, PimegaDetector):
    def __init__(self, name, prefix, **kwargs):
        super(Pimega, self).__init__(prefix, name=name, **kwargs)
