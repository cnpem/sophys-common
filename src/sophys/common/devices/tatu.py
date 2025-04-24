from ophyd import (
    Component,
    FormattedComponent,
    DynamicDeviceComponent,
    Device,
    EpicsSignal,
    EpicsSignalRO,
)
from ophyd.flyers import FlyerInterface
from sophys.common.utils.status import PremadeStatus

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


class TatuOutputBase(Device):
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

    def __init__(self, prefix, condition_number, **kwargs):
        split_prefix = prefix.split("/")
        self.condition_number = condition_number
        self.output_number = split_prefix[1]
        super().__init__(prefix=split_prefix[0], **kwargs)


class TatuOutputConditionV2(TatuOutputBase):
    """
    Configuration and status PVs for a TATU V2 Output port condition.
    """

    low = FormattedComponent(
        EpicsSignal, "{prefix}LowPeriodIO{output_number}:c{condition_number}"
    )
    high = FormattedComponent(
        EpicsSignal, "{prefix}HighPeriodIO{output_number}:c{condition_number}"
    )
    number_of_pulses = FormattedComponent(
        EpicsSignal, "{prefix}NPulsesIO{output_number}:c{condition_number}"
    )

    def __init__(self, prefix, condition_number, **kwargs):
        super().__init__(prefix, condition_number, **kwargs)


class TatuOutputCondition(TatuOutputBase):
    """
    Configuration and status PVs for a TATU Output port condition.
    """

    pulse = FormattedComponent(
        EpicsSignal, "{prefix}PulseIO{output_number}:c{condition_number}"
    )

    def __init__(self, prefix, condition_number, **kwargs):
        super().__init__(prefix, condition_number, **kwargs)


class TatuOutputV2(Device):
    """
    All the conditions PVs for a TATU V2 Output port.
    """

    c1 = FormattedComponent(
        TatuOutputConditionV2, "{prefix}/{output_number}", condition_number="0"
    )
    c2 = FormattedComponent(
        TatuOutputConditionV2, "{prefix}/{output_number}", condition_number="1"
    )
    c3 = FormattedComponent(
        TatuOutputConditionV2, "{prefix}/{output_number}", condition_number="2"
    )

    logic = FormattedComponent(EpicsSignal, "{prefix}OutputLogicIO{output_number}")

    def __init__(self, prefix, output_number, **kwargs):
        self.output_number = output_number
        super().__init__(prefix=prefix, **kwargs)


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


class TatuFlyScan(FlyerInterface):

    def kickoff(self):
        return self.activate.set(1)

    def complete(self):
        return PremadeStatus(success=True)

    def describe_collect(self):
        return {}

    def collect(self):
        return []


class TatuBase(Device, TatuFlyScan):
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
    TATU device adapted to work with the C-Series module 9401.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output.
    """

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutput, "", {"output_number": "4"}),
            "io5": (TatuOutput, "", {"output_number": "5"}),
            "io6": (TatuOutput, "", {"output_number": "6"}),
            "io7": (TatuOutput, "", {"output_number": "7"}),
        }
    )


class Tatu9401V2(Tatu9401):
    """
    TATU V2 device adapted to work with the C-Series module 9401.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output.
    """

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutputV2, "", {"output_number": "4"}),
            "io5": (TatuOutputV2, "", {"output_number": "5"}),
            "io6": (TatuOutputV2, "", {"output_number": "6"}),
            "io7": (TatuOutputV2, "", {"output_number": "7"}),
        }
    )

    file_name = FormattedComponent(EpicsSignal, "{global_prefix}Filename")

    def __init__(self, prefix, **kwargs):
        self.global_prefix = prefix[:-1].rpartition(":")[0] + ":"
        super().__init__(prefix, **kwargs)


class Tatu9403(TatuBase, CRIO_9403):
    """
    TATU device adapted to work with the C-Series module 9403.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output,

    This same sequence is repeated for the other channels in the sequence, four inputs, four outputs, for the first 24 IO ports.
    """

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutput, "", {"output_number": "4"}),
            "io5": (TatuOutput, "", {"output_number": "5"}),
            "io6": (TatuOutput, "", {"output_number": "6"}),
            "io7": (TatuOutput, "", {"output_number": "7"}),
        }
    )

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


class Tatu9403V2(Tatu9403):
    """
    TATU V2 device adapted to work with the C-Series module 9403.

    This module consists of four high-speed TTL channels as an input and the other four high-speed TTL channels as an output,

    This same sequence is repeated for the other channels in the sequence, four inputs, four outputs, for the first 24 IO ports.
    """

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutputV2, "", {"output_number": "4"}),
            "io5": (TatuOutputV2, "", {"output_number": "5"}),
            "io6": (TatuOutputV2, "", {"output_number": "6"}),
            "io7": (TatuOutputV2, "", {"output_number": "7"}),
        }
    )

    output2 = DynamicDeviceComponent(
        {
            "io12": (TatuOutputV2, "", {"output_number": "12"}),
            "io13": (TatuOutputV2, "", {"output_number": "13"}),
            "io14": (TatuOutputV2, "", {"output_number": "14"}),
            "io15": (TatuOutputV2, "", {"output_number": "15"}),
        }
    )

    output3 = DynamicDeviceComponent(
        {
            "io20": (TatuOutputV2, "", {"output_number": "20"}),
            "io21": (TatuOutputV2, "", {"output_number": "21"}),
            "io22": (TatuOutputV2, "", {"output_number": "22"}),
            "io23": (TatuOutputV2, "", {"output_number": "23"}),
        }
    )
