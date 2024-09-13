from ophyd.pv_positioner import PVPositionerIsClose
from ophyd import Component, Device, EpicsSignal, EpicsSignalRO


class PmacEpicsSignal(PVPositionerIsClose):

    readback = Component(EpicsSignal, "SET")
    setpoint = Component(EpicsSignalRO, "RBV")
    sync = Component(EpicsSignal, "SYNC")


class Pgm(Device):
    """
        Device for controlling the PGM Monochromator.
    """
    
    mode = Component(PmacEpicsSignal, "SCAN_MODE:")
    status = Component(PmacEpicsSignal, "SCAN_STATUS:")
    error_status = Component(PmacEpicsSignal, "SCAN_ERROR_STATUS:")

    csv_file_rows = Component(PmacEpicsSignal, "SCAN_CSV_FILE_ROWS:")
    csv_file_columns = Component(PmacEpicsSignal, "SCAN_CSV_FILE_COLUMNS:")
    csv_file_number = Component(PmacEpicsSignal, "SCAN_CSV_FILE_NUMBER:")
    
    version = Component(PmacEpicsSignal, "SCAN_VERSION:")
    abort = Component(PmacEpicsSignal, "SCAN_ABORT:")
    
    enable_int_gather = Component(PmacEpicsSignal, "SCAN_ENABLE_INT_GATHER:")
    enable_ext_gather = Component(PmacEpicsSignal, "SCAN_ENABLE_EXT_GATHER:")
    
    step_exposure_time = Component(PmacEpicsSignal, "SCAN_STEP_EXPOSURE_TIME:")
    step_move_timeout = Component(PmacEpicsSignal, "SCAN_STEP_MOVE_TIMEOUT:")
    step_abort_on_timeout = Component(PmacEpicsSignal, "SCAN_STEP_ABORT_ON_TIMEOUT:")
    step_delay_to_trigger = Component(PmacEpicsSignal, "SCAN_STEP_DELAY_TO_TRIGGER:")
    
    fly_trigger_out = Component(PmacEpicsSignal, "SCAN_FLY_TRIGGER_OUT:")
    
    start = Component(EpicsSignal, "SendCmd")
    servo_freq = Component(EpicsSignal, "SERVO_FREQ")