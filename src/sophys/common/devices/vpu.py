from ophyd import Device, EpicsSignal, EpicsSignalRO, Component
from sophys.common.utils import (
    EpicsSignalWithMonSP,
    EpicsSignalWithRBSP,
    EpicsSignalMon,
    EpicsSignalCmd,
)


class VPU(Device):
    """
    Device for controlling the VPU Undulator.
    """

    k_param = Component(EpicsSignalWithMonSP, "KParam")
    taper = Component(EpicsSignalWithMonSP, "Taper")
    taper_velo = Component(EpicsSignalMon, "TaperVelo")
    center_offset = Component(EpicsSignalWithMonSP, "CenterOffset")
    center_offset_velo = Component(EpicsSignalMon, "CenterOffsetVelo")
    pitch_offset = Component(EpicsSignalMon, "PitchOffset")
    pitch_offset_velo = Component(EpicsSignalMon, "PitchOffsetVelo")
    move_velo = Component(EpicsSignalWithRBSP, "MoveVelo")
    move_acc = Component(EpicsSignalWithRBSP, "MoveAcc")
    move_start = Component(EpicsSignalCmd, "MoveStart")
    abort = Component(EpicsSignalCmd, "Abort")

    moving = Component(EpicsSignalMon, "Moving")
    warning = Component(EpicsSignalMon, "Warning")
    alarm = Component(EpicsSignalMon, "Alarm")
    beamline_control = Component(EpicsSignalMon, "BeamLineCtrl")

    scan_mode = Component(EpicsSignal, "ScanMode-Sel")
    activate_scan_mode = Component(EpicsSignalCmd, "ActivateScanMode")
    flyscan_start = Component(EpicsSignalCmd, "FlyScanStart")
    scan_finished = Component(EpicsSignalMon, "ScanFinished")
