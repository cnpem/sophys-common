# numpydoc ignore=GL08

import time as ttime
from collections.abc import Generator

from bluesky.protocols import Status
from ophyd import (
    Component,
    Device,
    DynamicDeviceComponent,
    EpicsSignal,
    EpicsSignalRO,
    FormattedComponent,
    Signal,
)
from ophyd.flyers import FlyerInterface

from ..utils.status import PremadeStatus
from .crio import CRIO_9403


class TatuInput(Device):
    """
    Base configuration and status PVs for a TATU Input port.

    Parameters
    ----------
    prefix : str
        The PV prefix for all components of the device.
    input_number : str
        The number for tatu input port.
    **kwargs
        Arbitrary keyword arguments.
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

    def __init__(self, prefix, input_number, **kwargs):  # numpydoc ignore=GL08
        self.input_number = input_number
        super().__init__(prefix=prefix, **kwargs)


class TatuInputV2(TatuInput):
    """
    PVs for a TATU V2 Input port.

    Parameters
    ----------
    prefix : str
        The PV prefix for all components of the device.
    input_number : str
        The number for tatu input port.
    **kwargs
        Arbitrary keyword arguments.
    """

    trigger_hold_time = FormattedComponent(
        EpicsSignal, "{prefix}TriggerHoldTimeIO{input_number}"
    )

    def __init__(self, prefix, input_number, **kwargs):  # numpydoc ignore=GL08
        self.input_number = input_number
        super().__init__(prefix, input_number, **kwargs)


class TatuOutputBase(Device):
    """
    Base configuration and status PVs for a TATU Output port condition.

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    condition_number : str
        The number for TATU Output port condition.
    **kwargs
        Arbitrary keyword arguments.
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

    def __init__(self, prefix, condition_number, **kwargs):  # numpydoc ignore=GL08
        split_prefix = prefix.split("/")
        self.condition_number = condition_number
        self.output_number = split_prefix[1]
        super().__init__(prefix=split_prefix[0], **kwargs)


class TatuOutputConditionV2(TatuOutputBase):
    """
    Configuration and status PVs for a TATU V2 Output port condition.

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    condition_number : str
        The number for TATU V2 Output port condition.
    **kwargs
        Arbitrary keyword arguments.
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

    def __init__(self, prefix, condition_number, **kwargs):  # numpydoc ignore=GL08
        super().__init__(prefix, condition_number, **kwargs)


class TatuOutputCondition(TatuOutputBase):
    """
    Configuration and status PVs for a TATU Output port condition.

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    condition_number : str
        The number for TATU Output port condition.
    **kwargs
        Arbitrary keyword arguments.
    """

    pulse = FormattedComponent(
        EpicsSignal, "{prefix}PulseIO{output_number}:c{condition_number}"
    )

    def __init__(self, prefix, condition_number, **kwargs):  # numpydoc ignore=GL08
        super().__init__(prefix, condition_number, **kwargs)


class TatuOutputV2(Device):
    """
    All the conditions PVs for a TATU V2 Output port.

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    output_number : str
        The number for TATU V2 Output port.
    **kwargs
        Arbitrary keyword arguments.
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

    def __init__(self, prefix, output_number, **kwargs):  # numpydoc ignore=GL08
        self.output_number = output_number
        super().__init__(prefix=prefix, **kwargs)


class TatuOutput(Device):
    """
    All the conditions PVs for a TATU Output port.

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    output_number : str
        The number for TATU Output port.
    **kwargs
        Arbitrary keyword arguments.
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

    def __init__(self, prefix, output_number, **kwargs):  # numpydoc ignore=GL08
        self.output_number = output_number
        super().__init__(prefix=prefix, **kwargs)


class TatuFlyScan(FlyerInterface):
    """
    Flyer base implementation for TATU devices.

    Extended classes should replace these methods with appropriate implementations for
    their use-case, especially the 'complete' method.
    """

    def kickoff(self):
        """Start a trigger pulse from pre-configured TATU parameters."""
        if not hasattr(self, "activate") or not isinstance(self.activate, Signal):
            raise RuntimeError(
                "Failed to kickoff TATU instance, due to a missing valid 'activate' signal."
            )

        return self.activate.set(1, timeout=10)

    def complete(self):
        """
        Wait for TATU to complete a scan.

        Since the device can be used only as a trigger forwarder, without internal scan logic,
        the default implementation doesn't wait for anything.
        """
        return PremadeStatus(success=True)

    def describe_collect(self) -> dict[str, dict]:  # numpydoc ignore=GL08
        return {"tatu_collect": {}}

    def collect(self) -> Generator[dict, None, None]:  # numpydoc ignore=GL08
        yield {
            "time": ttime.time(),
            "timestamps": {},
            "data": {},
        }


class TatuBase(Device, TatuFlyScan):
    """
    Base device for the TATU software, which produces or a distribute digital signals to coordinate events \
    and actions to achieve a synchronized operation at a beamline.

    Documentation: http://bit.ly/tatu-sirius

    Parameters
    ----------
    prefix : str
        The PV prefix for all components of the device.
    **kwargs
        Keyword arguments for the base Device class.
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

    def __init__(self, prefix, **kwargs):  # numpydoc ignore=GL08
        self.prefix = prefix

        self._old_master_mode_state = None

        super().__init__(prefix=prefix, **kwargs)

    def stage(self) -> Status:  # numpydoc ignore=GL08
        # NOTE: Don't use the Ophyd staging logic, use the Bluesky interface and return a Status object.
        return self.activate.set(1, timeout=10)

    def unstage(self) -> Status:  # numpydoc ignore=GL08
        # NOTE: Don't use the Ophyd staging logic, use the Bluesky interface and return a Status object.
        return self.activate.set(0, timeout=10)

    def stop(self, success: bool = True):  # numpydoc ignore=GL08
        self.pause()

        return super().stop(success=success)

    def pause(self):  # numpydoc ignore=GL08
        self._old_master_mode_state = self.master_mode.get()

        self.tatu_stop.set(1, timeout=10)
        self.activate.set(0, timeout=10).wait()

    def resume(self):  # numpydoc ignore=GL08
        if self._old_master_mode_state is not None:
            self.master_mode.set(self._old_master_mode_state, timeout=10).wait()

            self._old_master_mode_state = None

        self.activate.set(1, timeout=10).wait()


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

    Parameters
    ----------

    prefix : str
        The PV prefix for all components of the device.
    **kwargs
        Arbitrary keyword arguments.
    """

    input = DynamicDeviceComponent(
        {
            "p0": (TatuInputV2, "", {"input_number": "0"}),
            "p1": (TatuInputV2, "", {"input_number": "1"}),
            "p2": (TatuInputV2, "", {"input_number": "2"}),
            "p3": (TatuInputV2, "", {"input_number": "3"}),
        }
    )

    output = DynamicDeviceComponent(
        {
            "io4": (TatuOutputV2, "", {"output_number": "4"}),
            "io5": (TatuOutputV2, "", {"output_number": "5"}),
            "io6": (TatuOutputV2, "", {"output_number": "6"}),
            "io7": (TatuOutputV2, "", {"output_number": "7"}),
        }
    )

    file_name = FormattedComponent(EpicsSignal, "{global_prefix}Filename")

    def __init__(self, prefix, **kwargs):  # numpydoc ignore=GL08
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

    input = DynamicDeviceComponent(
        {
            "p0": (TatuInputV2, "", {"input_number": "0"}),
            "p1": (TatuInputV2, "", {"input_number": "1"}),
            "p2": (TatuInputV2, "", {"input_number": "2"}),
            "p3": (TatuInputV2, "", {"input_number": "3"}),
        }
    )

    input2 = DynamicDeviceComponent(
        {
            "p8": (TatuInputV2, "", {"input_number": "8"}),
            "p9": (TatuInputV2, "", {"input_number": "9"}),
            "p10": (TatuInputV2, "", {"input_number": "10"}),
            "p11": (TatuInputV2, "", {"input_number": "11"}),
        }
    )

    input3 = DynamicDeviceComponent(
        {
            "p16": (TatuInputV2, "", {"input_number": "16"}),
            "p17": (TatuInputV2, "", {"input_number": "17"}),
            "p18": (TatuInputV2, "", {"input_number": "18"}),
            "p19": (TatuInputV2, "", {"input_number": "19"}),
        }
    )

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
