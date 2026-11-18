from ..devices.eu3508 import (
    SegmentType,
    SegmentEndType,
    EU3508ProgStatusType,
    EU3508,
)  # numpydoc ignore=GL08
from types import MappingProxyType
from typing import Literal, Optional, List, Tuple
from bluesky.plan_stubs import (
    mv,
    kickoff,
    complete,
    collect,
    monitor,
    unmonitor,
    open_run,
    close_run,
    stop,
    sleep,
)
from logging import getLogger

logger = getLogger("sophys.common.plans.in_situ")


segment_type_enum_map = MappingProxyType(
    {"ramp": SegmentType.RAMP_RATE, "dwell": SegmentType.DWELL}
)  # read-only mapping dict
end_type_enum_map = MappingProxyType(
    {"reset": SegmentEndType.RESET, "dwell": SegmentEndType.DWELL}
)  # read-only mapping dict


class EU3508ProgrammingError(Exception):  # numpydoc ignore=GL08
    def __init__(self, *args):  # numpydoc ignore=GL08
        super().__init__(*args)


def program_eu3508_segment(
    heating_device: EU3508,
    segment_type: Literal["ramp", "dwell"],
    ramp_rate: Optional[float] = None,
    temperature: Optional[float] = None,
    duration: Optional[float] = None,
    end_type: Literal["reset", "dwell"] = "dwell",
    run: bool = False,
    block_queue: bool = True,
):
    """
    Program a segment in an Eurotherm EU3508 device.

    The allowed segments are 'ramp' and 'dwell'. Note that, if 'ramp' is selected,
    the parameters 'temperature' and 'ramp_rate' are required. Likewise, if 'dwell'
    is selected, the parameter 'duration' is required.

    Parameters
    ----------
    heating_device : EU3508
        Ophyd device object for EU3508.
    segment_type : str
        It can be either 'ramp' or 'dwell'.
    ramp_rate : float, optional
        The temperature rate in °C/min used in the ramp segment.
        For targets higher than 400°C, the maximum rate is 5°C/min.
    temperature : float, optional
        The target temperature in °C for the ramp segment.
    duration : float, optional
        The time spent in minutes during the dwell segment.
    end_type : str
        It can be either 'dwell' or 'reset'.
    run : bool, default=False
        Whether or not to start the programmed segment.
    block_queue : bool, default=True
        Whether or not to block the Queue when runnig the programed
        experiment.

    Returns
    -------
    Status
        Complete Status of the `heating_device`.
        If not blocking queue, the status will always be complete.

    Notes
    -----
    This plan always program the segment in the same slot of the available segments of the device.

    In this manner, it is possible to program a lot more segments than the slots available
    in the devices.

    This means, that the first segment is always used to program the 'segment_type'
    and that the second segment is always programmed as an END segment with 'end_type'.
    """
    logger.info(f"Programming {heating_device.name}")
    logger.info(f"Programming segment type as {segment_type}")
    yield from mv(
        heating_device.segment.s0.type, segment_type_enum_map[segment_type]
    )  # write segment type

    if segment_type_enum_map[segment_type] == SegmentType.RAMP_RATE:

        logger.info(
            f"Segment configuration - Ramp Rate: {ramp_rate} °C/min; Target temperature: {temperature} °C"
        )

        yield from mv(heating_device.segment.s0.temperature, temperature)
        yield from mv(heating_device.segment.s0.ramp_rate, ramp_rate)

    elif segment_type_enum_map[segment_type] == SegmentType.DWELL:

        logger.info(f"Segment configuration - Dwell duration: {duration} min")
        yield from mv(heating_device.segment.s0.duration, duration * 60)

    yield from mv(heating_device.segment.s1.type, SegmentType.END)
    yield from mv(heating_device.segment.s1.end_type, end_type_enum_map[end_type])

    def inner():  # numpydoc ignore=GL08
        logger.info(f"Starting {heating_device.name} device!")
        yield from kickoff(
            heating_device, wait=True
        )  # we can start for both cases and wait, since what actually is lenghty is the complete
        if block_queue:
            st = yield from complete(heating_device, wait=True)
            yield from collect(heating_device)
        else:
            st = yield from complete(heating_device, wait=False)
        return st

    if run:
        st = yield from inner()
        return st


def check_eu3508_regions(regions: List[Tuple[Literal["ramp", "dwell"]]]):
    """
    Check the each region parameter of `regions` and raises `Exceptions` if needed.

    Parameters
    ----------
    regions : list of tuples
        A list of tuples where each contains the `segment_type`, `ramp_rate`, `temperature` and `duration`.
        The `segment_type` can be 'ramp' or 'dwell'.
    """
    if len(regions) == 0:
        raise EU3508ProgrammingError(
            "Received an empty list! At least one region is needed to program the device!"
        )
    for region in regions:
        (
            segment_type,
            segment_rate,
            segment_temp,
            segment_duration,
        ) = region
        if segment_type not in segment_type_enum_map.keys():  # Check segment type
            raise EU3508ProgrammingError(
                f"Received '{segment_type}' as segment type. Valid values are 'ramp' and 'dwell'."
            )
        if segment_type_enum_map[segment_type] == SegmentType.RAMP_RATE:

            if not isinstance(segment_temp, (int, float)):  # Check temp type
                raise EU3508ProgrammingError(
                    f"Non-valid type {type(segment_temp)} for temperature parameter. Valid types are int and float."
                )

            if not isinstance(segment_rate, (int, float)):  # Check rate type
                raise EU3508ProgrammingError(
                    f"Non-valid type {type(segment_rate)} for rate parameter. Valid types are int and float."
                )

            if segment_temp < 30 or segment_temp > 1000:  # Check temp range
                raise EU3508ProgrammingError(
                    f"Target temperature: {segment_temp} °C outside valid range of [30, 100] °C."
                )

            if segment_rate < 0 or segment_rate > 10:  # Check rate range
                raise EU3508ProgrammingError(
                    f"Segment rate: {segment_rate} °C/min outside valid range of [0, 10] °C/min."
                )

            if segment_temp > 400 and segment_rate > 5:  # Check temp and rate range
                raise EU3508ProgrammingError(
                    f"Received {segment_rate} °C/min as ramp rate for target {segment_temp} °C. The maximum rate for targets higher than 400 °C is 5 °C/min."
                )

        elif segment_type_enum_map[segment_type] == SegmentType.DWELL:

            if not isinstance(segment_duration, (int, float)):  # Check dwell type
                raise EU3508ProgrammingError(
                    f"Non-valid type {type(segment_duration)} for duration parameter. Valid types are int and float."
                )

            if segment_duration <= 0:  # Check dwell range
                raise EU3508ProgrammingError(
                    f"Negative value for dwell duration: {segment_duration}."
                )


def program_eu3508(
    heating_device: EU3508,
    regions: List[
        Tuple[
            Literal["ramp", "dwell"],
            float,
            float,
            float,
        ]
    ],
    last_region_end_type: Literal["reset", "dwell"] = "reset",
    md: dict = {},
):
    """
    Program and run a list of segments (or regions) with the 'EU3508' device.

    Parameters
    ----------
    heating_device : EU3508
        Ophyd device object for EU3508.
    regions : list of tuples
        A list of tuples where each contains the `segment_type`, `ramp_rate`, `temperature` and `duration`.
        The `segment_type` can be 'ramp' or 'dwell'.
    last_region_end_type : str, default="reset"
        EndType of the last segment. It can be either `reset` or `dwell`.
    md : dict, optional
        Optional metadata dictionary.

    See Also
    --------
    program_eu3508_segment :  Plan to program individual segments in the heating devices.
    """
    check_eu3508_regions(regions)  # first of all check regions parameter
    heating_device_status = heating_device.running.get()
    if heating_device_status not in {
        EU3508ProgStatusType.NOT_RUNNING,
        EU3508ProgStatusType.END,
    }:
        raise EU3508ProgrammingError(
            "EU308 device is not ready for a new programming. Please check if another program is in progress."
        )
    _md = {
        "plan_name": "program_eu3508",
        "plan_args": {
            "regions": regions,
            "last_region_end_type": last_region_end_type,
        },
        "devices": [f"{heating_device.name}"],
    }

    _md.update(md)
    *regions, last_region = regions  # separate the last region to set it's end_type.

    def inner():  # numpydoc ignore=GL08
        yield from monitor(
            heating_device.readback, name=f"{heating_device.name}_readback"
        )
        yield from monitor(
            heating_device.setpoint, name=f"{heating_device.name}_setpoint"
        )

        if len(regions) > 0:
            for i, (segment_type, ramp_rate, temperature, duration) in enumerate(
                regions
            ):
                logger.info(f"Configuring Segment # {i}")
                yield from program_eu3508_segment(
                    heating_device=heating_device,
                    segment_type=segment_type,
                    ramp_rate=ramp_rate,
                    temperature=temperature,
                    duration=duration,
                    run=True,
                )

        logger.info("Configuring Last Segment")
        (
            last_segment_type,
            last_segment_rate,
            last_segment_temp,
            last_segment_duration,
        ) = last_region
        yield from program_eu3508_segment(
            heating_device=heating_device,
            segment_type=last_segment_type,
            ramp_rate=last_segment_rate,
            temperature=last_segment_temp,
            duration=last_segment_duration,
            end_type=last_region_end_type,
            run=True,
        )
        yield from unmonitor(heating_device.readback)
        yield from unmonitor(heating_device.setpoint)

    yield from open_run(md=_md)
    yield from inner()
    yield from close_run("success")


def eu3508_contingency_plan(heating_device: EU3508):
    """
    Contingency plan for EU3508 device. It stops the equipment, bringing it's setopint to 11°C.

    Parameters
    ----------
    heating_device : EU3508
        An instance of the EU3508 Ophyd device object.
    """
    yield from stop(heating_device)
