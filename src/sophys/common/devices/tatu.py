from ophyd import Component, FormattedComponent, DynamicDeviceComponent, \
    Device, EpicsSignal, EpicsSignalRO


class TatuInput(Device):
    
    current_value = FormattedComponent(EpicsSignalRO, "{prefix}P{input_number}")
    trigger_state = FormattedComponent(EpicsSignalRO, "{prefix}InputTriggerIO{input_number}")
    edges_number_to_trigger = FormattedComponent(EpicsSignalRO, "{prefix}EdgestoTrigIO{input_number}")
    readout_threshold = FormattedComponent(EpicsSignalRO, "{prefix}AnalogThresholdIO{input_number}")
    associated_trigger_channel = FormattedComponent(EpicsSignalRO, "{prefix}AnalogAssocCh{input_number}")

    def __init__(self, prefix, input_number, **kwargs):
        self.input_number = input_number
        super().__init__(prefix=prefix, **kwargs)


class TatuOutputCondition(Device):

    condition = FormattedComponent(EpicsSignal, "{prefix}ConditionIO{output_number}:c{condition_number}")
    condition_combo = FormattedComponent(EpicsSignal, "{prefix}ConditionComboIO{output_number}:c{condition_number}")
    output = FormattedComponent(EpicsSignal, "OutputIO{output_number}:c{condition_number}")
    output_copy = FormattedComponent(EpicsSignal, "OutputCOPYIO{output_number}:c{condition_number}")
    delay = FormattedComponent(EpicsSignal, "DelayIO{output_number}:c{condition_number}")
    pulse = FormattedComponent(EpicsSignal, "PulseIO{output_number}:c{condition_number}")

    def __init__(self, prefix, condition_number, **kwargs):
        split_prefix = prefix.split("/")
        self.condition_number = condition_number
        self.output_number = split_prefix[1]
        super().__init__(prefix=split_prefix[0], **kwargs)


class TatuOutput(Device):
    
    c1 = FormattedComponent(
        TatuOutputCondition, "{prefix}/{output_number}", condition_number="1")
    c2 = FormattedComponent(
        TatuOutputCondition, suffix="{prefix}/{output_number}", condition_number="2")
    c3 = FormattedComponent(
        TatuOutputCondition, suffix="{prefix}/{output_number}", condition_number="3")

    def __init__(self, prefix, output_number, **kwargs):
        self.output_number = output_number
        super().__init__(prefix=prefix, **kwargs)


class TatuBase(Device):

    activate = Component(
        EpicsSignal, "TatuActive", write_pv="Activate")
    master_mode = Component(EpicsSignal, "MasterMode", kind="config")
    tatu_stop = Component(EpicsSignal, "Stop", kind="config")
    fly_scan_trigger = Component(EpicsSignal, "FlyScan", kind="config")
    reset_pulses = Component(EpicsSignal, "Zeropulses", kind="config")
    record_readouts = Component(EpicsSignal, "Record", kind="config")

    master_pulse = DynamicDeviceComponent({
        "number": (EpicsSignal, "MasterPulseNumber", {"kind": "config"}),
        "period": (EpicsSignal, "MasterPulsePeriod", {"kind": "config"}),
        "length": (EpicsSignal, "MasterPulseLength", {"kind": "config"}),
        "active": (EpicsSignalRO, "MasterPulsing", {"kind": "config"}),
        "count": (EpicsSignalRO, "IssuedMasterPulses", {"kind": "config"})
    })

    fly_scan = DynamicDeviceComponent({
        "time": (EpicsSignal, "FlyScanTimePreset", {"kind": "config"}),
        "trigger_count": (EpicsSignalRO, "TriggerCounter", {"kind": "config"}),
        "file_path_1": (EpicsSignal, "FlyScanFilePath", {"kind": "config"}),
        "file_path_2": (EpicsSignal, "FlyScanFilePath2", {"kind": "config"}),
        "file_name": (EpicsSignal, "FlyScanFileName", {"kind": "config"}),
        "file_open": (EpicsSignalRO, "FlyScanFileOpen", {"kind": "config"}),
        "file_valid_path": (EpicsSignalRO, "FlyScanFileValidPath", {"kind": "config"}),
        "file_error_code": (EpicsSignalRO, "FlyScanErrorCode", {"kind": "config"}),
        "file_error_message": (EpicsSignalRO, "FlyScanErrorMsg", {"kind": "config"})
    })

    input = DynamicDeviceComponent({
        "p0": (TatuInput, "", {"input_number": "0"}),
        "p1": (TatuInput, "", {"input_number": "1"}),
        "p2": (TatuInput, "", {"input_number": "2"}),
        "p3": (TatuInput, "", {"input_number": "3"})
    })

    output = DynamicDeviceComponent({
        "io4": (TatuOutput, "", {"output_number": "4"}),
        "io5": (TatuOutput, "", {"output_number": "5"}),
        "io6": (TatuOutput, "", {"output_number": "6"}),
        "io7": (TatuOutput, "", {"output_number": "7"})
    })

    def __init__(self, prefix, **kwargs):
        self.prefix = prefix
        super().__init__(prefix=prefix, **kwargs)

    def stage(self):
        super().stage()
        self.activate.set(1).wait()

    def unstage(self):
        super().unstage()
        self.activate.set(0).wait()

    def stop(self):
        self.tatu_stop.set(1)

    def pause(self):
        self.master_mode_state = self.master_mode.get()
        self.tatu_stop.set(1)

    def resume(self):
        self.master_mode.set(self.master_mode_state).wait()
        self.activate.set(1).wait()

class Tatu9401(TatuBase):
    """

    """

class Tatu9403(TatuBase):
    """
        
    """

    input2 = DynamicDeviceComponent({
        "p8": (TatuInput, "", {"input_number": "8"}),
        "p9": (TatuInput, "", {"input_number": "9"}),
        "p10": (TatuInput, "", {"input_number": "10"}),
        "p11": (TatuInput, "", {"input_number": "11"})
    })

    input3 = DynamicDeviceComponent({
        "p16": (TatuInput, "", {"input_number": "16"}),
        "p17": (TatuInput, "", {"input_number": "17"}),
        "p18": (TatuInput, "", {"input_number": "18"}),
        "p19": (TatuInput, "", {"input_number": "19"})
    })

    output2 = DynamicDeviceComponent({
        "io12": (TatuOutput, "", {"output_number": "12"}),
        "io13": (TatuOutput, "", {"output_number": "13"}),
        "io14": (TatuOutput, "", {"output_number": "14"}),
        "io15": (TatuOutput, "", {"output_number": "15"})
    })

    output3 = DynamicDeviceComponent({
        "io20": (TatuOutput, "", {"output_number": "20"}),
        "io21": (TatuOutput, "", {"output_number": "21"}),
        "io22": (TatuOutput, "", {"output_number": "22"}),
        "io23": (TatuOutput, "", {"output_number": "23"})
    })
