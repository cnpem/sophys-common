from ophyd import (
    Component,
    FormattedComponent,
    DynamicDeviceComponent,
    Device,
    EpicsSignal,
    EpicsSignalRO,
)
from ophyd.flyers import FlyerInterface
from ophyd.status import StatusBase
from .crio import CRIO_9403


class TatuInput(Device):
    """
    Base configuration and status PVs for a TATU Input port.
    """

    current_value = FormattedComponent(EpicsSignal, "{prefix}P{input_number}")
    trigger_value = FormattedComponent(
        EpicsSignal, "{prefix}InputTriggerIO{input_number}"
    )
    edges_to_trigger = FormattedComponent(
        EpicsSignal, "{prefix}EdgestoTrigIO{input_number}"
    )
    analog_threshold = FormattedComponent(
        EpicsSignal, "{prefix}AnalogThresholdCh{input_number}"
    )
    analog_assoc = FormattedComponent(
        EpicsSignal, "{prefix}AnalogAssocCh{input_number}"
    )

    def __init__(self, prefix, input_number, **kwargs):
        self.input_number = input_number
        super().__init__(prefix=prefix, **kwargs)


class TatuOutputCondition(Device):
    """
    Base configuration and status PVs for a TATU Output port condition.
    """

    changed = FormattedComponent(EpicsSignal, "{prefix}IO{output_number}changed")
    condition = FormattedComponent(
        EpicsSignal, "{prefix}ConditionIO{output_number}:c{condition_number}"
    )
    condition_combo = FormattedComponent(
        EpicsSignal, "{prefix}ConditionComboIO{output_number}:c{condition_number}"
    )
    output = FormattedComponent(
        EpicsSignal, "{prefix}OutputIO{output_number}:c{condition_number}"
    )
    output_copy = FormattedComponent(
        EpicsSignal, "{prefix}OutputCOPYIO{output_number}:c{condition_number}"
    )
    delay = FormattedComponent(
        EpicsSignal, "{prefix}DelayIO{output_number}:c{condition_number}"
    )
    pulse = FormattedComponent(
        EpicsSignal, "{prefix}PulseIO{output_number}:c{condition_number}"
    )

    def __init__(self, prefix, condition_number, **kwargs):
        split_prefix = prefix.split("/")
        self.condition_number = condition_number
        self.output_number = split_prefix[1]
        super().__init__(prefix=split_prefix[0], **kwargs)


class TatuOutput(Device):
    """
    All the conditions PVs for a TATU Output port.
    """

    c1 = FormattedComponent(
        TatuOutputCondition, "{prefix}/{output_number}", condition_number="0"
    )
    c2 = FormattedComponent(
        TatuOutputCondition, "{prefix}/{output_number}", condition_number="1"
    )
    c3 = FormattedComponent(
        TatuOutputCondition, "{prefix}/{output_number}", condition_number="2"
    )

    def __init__(self, prefix, output_number, **kwargs):
        self.output_number = output_number
        super().__init__(prefix=prefix, **kwargs)


class TatuBase(Device):
    """
    Base device for the TATU software, which produces or a distribute digital
    signals to coordinate events and actions to achieve a synchronized operation at a beamline.

    Documentation: http://bit.ly/tatu-sirius
    """

    activate = Component(EpicsSignal, "TatuActive", write_pv="Activate")
    master_mode = Component(EpicsSignal, "MasterMode", kind="config")
    tatu_stop = Component(EpicsSignal, "Stop", kind="config")
    reset_pulses = Component(EpicsSignal, "Zeropulses", kind="config")

    master_pulse = DynamicDeviceComponent(
        {
            "number": (EpicsSignal, "MasterPulseNumber", {"kind": "config"}),
            "period": (EpicsSignal, "MasterPulsePeriod", {"kind": "config"}),
            "length": (EpicsSignal, "MasterPulseLength", {"kind": "config"}),
            "active": (EpicsSignalRO, "MasterPulsing", {"kind": "config"}),
            "count": (EpicsSignalRO, "IssuedMasterPulses", {"kind": "config"}),
        }
    )

    input = DynamicDeviceComponent(
        {
            "p0": (TatuInput, "", {"input_number": "0"}),
            "p1": (TatuInput, "", {"input_number": "1"}),
            "p2": (TatuInput, "", {"input_number": "2"}),
            "p3": (TatuInput, "", {"input_number": "3"}),
        }
    )

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutput, "", {"output_number": "4"}),
            "io5": (TatuOutput, "", {"output_number": "5"}),
            "io6": (TatuOutput, "", {"output_number": "6"}),
            "io7": (TatuOutput, "", {"output_number": "7"}),
        }
    )

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


class TatuFlyScan(FlyerInterface):
    
    def kickoff(self):
        return self.activate.set(1)

    def complete(self):
        sts = StatusBase()
        sts.set_finished()
        return sts

    def describe_collect(self):
        return {}

    def collect(self):
        self.activate.set(0).wait()
        self.reset_pulses.set(1).wait()
        return []


class Tatu9401(TatuBase, TatuFlyScan):
    """
    TATU device adapted to work with the C-Series module 9401.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output.
    """

    pass


class Tatu9403(TatuBase, TatuFlyScan, CRIO_9403):
    """
    TATU device adapted to work with the C-Series module 9403.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output,

    This same sequence is repeated for the other channels in the sequence, four inputs, four outputs, for the first 24 IO ports.
    """

    input2 = DynamicDeviceComponent(
        {
            "p8": (TatuInput, "", {"input_number": "8"}),
            "p9": (TatuInput, "", {"input_number": "9"}),
            "p10": (TatuInput, "", {"input_number": "10"}),
            "p11": (TatuInput, "", {"input_number": "11"}),
        }
    )

    input3 = DynamicDeviceComponent(
        {
            "p16": (TatuInput, "", {"input_number": "16"}),
            "p17": (TatuInput, "", {"input_number": "17"}),
            "p18": (TatuInput, "", {"input_number": "18"}),
            "p19": (TatuInput, "", {"input_number": "19"}),
        }
    )

    output2 = DynamicDeviceComponent(
        {
            "io12": (TatuOutput, "", {"output_number": "12"}),
            "io13": (TatuOutput, "", {"output_number": "13"}),
            "io14": (TatuOutput, "", {"output_number": "14"}),
            "io15": (TatuOutput, "", {"output_number": "15"}),
        }
    )

    output3 = DynamicDeviceComponent(
        {
            "io20": (TatuOutput, "", {"output_number": "20"}),
            "io21": (TatuOutput, "", {"output_number": "21"}),
            "io22": (TatuOutput, "", {"output_number": "22"}),
            "io23": (TatuOutput, "", {"output_number": "23"}),
        }
    )
