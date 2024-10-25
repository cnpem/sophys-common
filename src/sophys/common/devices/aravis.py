from ophyd import ADComponent
from ophyd.areadetector import SingleTrigger, DetectorBase, EpicsSignalWithRBV, \
    EpicsSignalRO, EpicsSignal, Device
from sophys.common.utils import HDF5PluginWithFileStoreV34
from .cam import CamBase_V33


class ADAravis(Device):
    
    frames_completed = ADComponent(EpicsSignalRO, "ARFramesCompleted")
    frames_underruns = ADComponent(EpicsSignalRO, "ARFrameUnderruns")
    missing_packets = ADComponent(EpicsSignalRO, "ARMissingPackets")
    resent_packets = ADComponent(EpicsSignalRO, "ARResentPackets")
    packet_resend_enable = ADComponent(EpicsSignal, "ARPacketResendEnable", string=True)
    packet_timeout = ADComponent(EpicsSignal, "ARPacketTimeout")
    frame_retention = ADComponent(EpicsSignal, "ARFrameRetention")
    reset_camera = ADComponent(EpicsSignal, "ARResetCamera")
    connect_camera = ADComponent(EpicsSignal, "ARConnectCamera")
    check_connection = ADComponent(EpicsSignal, "ARCheckConnection")
    convert_pixel_format = ADComponent(EpicsSignalWithRBV, "ARConvertPixelFormat", string=True)
    shift_dir = ADComponent(EpicsSignalWithRBV, "ARShiftDir", string=True)
    shift_bits = ADComponent(EpicsSignalWithRBV, "ARShiftBits")


class ADGenICam(Device):

    frame_rate = ADComponent(EpicsSignalWithRBV, "FrameRate")
    frame_rate_enable = ADComponent(EpicsSignalWithRBV, "FrameRateEnable")
    trigger_source = ADComponent(EpicsSignalWithRBV , "TriggerSource", string=True)
    trigger_overlap = ADComponent(EpicsSignalWithRBV, "TriggerOverlap", string=True)
    trigger_software = ADComponent(EpicsSignal, "TriggerSoftware", string=True)
    exposure_mode = ADComponent(EpicsSignalWithRBV, "ExposureMode")
    exposure_auto = ADComponent(EpicsSignalWithRBV, "ExposureAuto", string=True)
    gain_auto = ADComponent(EpicsSignalWithRBV, "GainAuto", string=True)
    pixel_format = ADComponent(EpicsSignalWithRBV, "PixelFormat", string=True)


class AravisCam(CamBase_V33, ADAravis, ADGenICam):
    pass


class AravisDetector(SingleTrigger, DetectorBase):

    cam = ADComponent(AravisCam, "cam1:")
    hdf5 = ADComponent(
        HDF5PluginWithFileStoreV34,
        "HDF1:",
        write_path_template="/tmp",
        read_attrs=[],
    )