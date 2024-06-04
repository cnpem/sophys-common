from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, Kind
from ophyd.device import create_device_from_components

# Useful resources:
# https://cnpemcamp.sharepoint.com/sites/lnls/groups/sol/SitePages/CRIO-PVs.aspx


class _BaseCRIO(Device):
    pv_averaging_time = Component(EpicsSignal, "PvAvgTime", kind=Kind.config)


def __createAnalogIn(num: int) -> dict:
    components = {}
    for i in range(num):
        components.update(
            {
                f"ai{i}": Component(EpicsSignalRO, f"ai{i}", kind=Kind.hinted),
                f"ai{i}_offset": Component(
                    EpicsSignal, f"ai{i}_Offset", kind=Kind.config
                ),
                f"ai{i}_scale_factor": Component(
                    EpicsSignal, f"ai{i}_SF", kind=Kind.config
                ),
            }
        )
    return components


CRIO_9215 = create_device_from_components(
    "CRIO_9215", base_class=_BaseCRIO, **__createAnalogIn(4)
)
CRIO_9220 = create_device_from_components(
    "CRIO_9220", base_class=_BaseCRIO, **__createAnalogIn(16)
)
