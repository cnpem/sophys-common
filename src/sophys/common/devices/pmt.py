from ophyd import Device, Component, EpicsSignalRO
from sophys.common.utils import EpicsSignalWithGetSet


class Photomultiplier(Device):
    """
    Photomultiplier device developed by the group GIE.
    """

    voltage = Component(EpicsSignalWithGetSet, "", ssuffix="VoltageDAC")
    voltage_driver = Component(EpicsSignalWithGetSet, "", ssuffix="VoltageDriver")
    voltage_ramp = Component(EpicsSignalWithGetSet, "", ssuffix="VoltageRampDAC")

    current = Component(EpicsSignalWithGetSet, "", ssuffix="CurrentDAC")
    current_driver = Component(EpicsSignalWithGetSet, "", ssuffix="CurrentDriver")
    current_driver_porc = Component(EpicsSignalWithGetSet, "", ssuffix="CurrentDriverPorc")

    sample_holder_speed = Component(EpicsSignalWithGetSet, "", ssuffix="SampleHolderSpeed")
    sample_holder_type = Component(EpicsSignalWithGetSet, "", ssuffix="SampleHolderType")

    analog_input_ch1 = Component(EpicsSignalRO, "getAnalogInputCh1")
    analog_input_ch2 = Component(EpicsSignalRO, "getAnalogInputCh2")
    digital_input_ch1 = Component(EpicsSignalRO, "getDigitalInputCh1")
    digital_input_ch2 = Component(EpicsSignalRO, "getDigitalInputCh2")
    digital_output_ch1 = Component(EpicsSignalWithGetSet, "", ssuffix="DigitalOutputCh1")
    digital_output_ch2 = Component(EpicsSignalWithGetSet, "", ssuffix="DigitalOutputCh2")
    duty_cycle_ch1 = Component(EpicsSignalWithGetSet, "", ssuffix="DutyCycleCh1")
    duty_cycle_ch2 = Component(EpicsSignalWithGetSet, "", ssuffix="DutyCycleCh2")

    safety_mode = Component(EpicsSignalWithGetSet, "", ssuffix="SafetyMode")
    frequency = Component(EpicsSignalWithGetSet, "", ssuffix="Frequency")
    status = Component(EpicsSignalRO, "Status")
    stop_pmt = Component(EpicsSignalRO, "Stop")

    set_timer = Component(EpicsSignalRO, "setTimer")
    read_timer = Component(EpicsSignalRO, "readTimer")
    start_timer = Component(EpicsSignalRO, "startTimer")
    stop_timer = Component(EpicsSignalRO, "stopTimer")
