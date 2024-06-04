from ophyd import Component, EpicsSignalRO
from ophyd.device import create_device_from_components


def __createAnalogIn(num: int) -> dict:
    return {f"ai{i}": Component(EpicsSignalRO, f"ai{i}") for i in range(num)}


CRIO_9215 = create_device_from_components("CRIO_9215", **__createAnalogIn(4))
CRIO_9220 = create_device_from_components("CRIO_9220", **__createAnalogIn(16))
