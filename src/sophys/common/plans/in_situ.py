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
)
from logging import getLogger, Logger


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
    logger: Optional[Logger] = None,
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
    logger : Logger, optional
        Optional logger for the plan.

    Notes
    -----
    This plan always program the segment in the same slot of the available segments of the device.

    In this manner, it is possible to program a lot more segments than the slots available
    in the devices.

    This means, that the first segment is always used to program the 'segment_type'
    and that the second segment is always programmed as an END segment with 'end_type'.
    """
    if logger is None:
        logger = getLogger(__file__)
    logger.info(f"Programming {heating_device.name}")
    logger.info(f"Programming segment type as {segment_type}")
    yield from mv(
        heating_device.segment.s0.type, segment_type_enum_map[segment_type]
    )  # write segment type

    if segment_type_enum_map[segment_type] == SegmentType.RAMP_RATE:
        if any(param is None for param in [temperature, ramp_rate]):
            raise EU3508ProgrammingError(
                "The parameters 'temperature' and 'ramp_rate' are both required when programming a Ramp segment."
            )

        if temperature < 30:
            logger.warning(
                f"Received target temperature: {temperature}°C bellow minimum of 30°C."
            )
            logger.warning("Changing target temperature to 30°C.")
            temperature = 30

        if temperature > 1000:
            logger.warning(
                f"Received target temperature: {temperature}°C above maximum of 1000°C."
            )
            logger.warning("Changing target temperature to 1000°C.")
            temperature = 1000

        if ramp_rate > 10:
            logger.warning(
                f"Received ramp rate: {ramp_rate}°C/min above maximum of 10°C/min."
            )
            logger.warning("Changing ramp rate to 10°C/min.")
            ramp_rate = 10

        if temperature > 400 and ramp_rate > 5:
            logger.warning(
                f"Received {ramp_rate}°C/min as ramp rate for target {temperature}°C. "
                "The maximum rate for targets higher than 400°C is 5°C/min."
            )
            logger.warning("Changing ramp rate to 5°C/min.")
            ramp_rate = 5

        logger.info(
            f"Segment configuration - Ramp Rate: {ramp_rate} °C/min; Target temperature: {temperature} °C"
        )

        yield from mv(heating_device.segment.s0.temperature, temperature)
        yield from mv(heating_device.segment.s0.ramp_rate, ramp_rate)

    elif segment_type_enum_map[segment_type] == SegmentType.DWELL:
        if duration is None:
            raise EU3508ProgrammingError(
                "The parameter 'duration' is required when programming a Dwell segment."
            )
        logger.info(f"Segment configuration - Dwell duration: {duration} min")
        yield from mv(heating_device.segment.s0.duration, duration * 60)

    yield from mv(heating_device.segment.s1.type, SegmentType.END)
    yield from mv(heating_device.segment.s1.end_type, end_type_enum_map[end_type])

    def inner():  # numpydoc ignore=GL08
        if block_queue:
            logger.info(f"Starting {heating_device.name} and blocking queue!")
            yield from kickoff(heating_device, wait=True)
            yield from complete(heating_device, wait=True)
            yield from collect(heating_device)
        else:
            logger.info(f"Starting {heating_device.name} whithout blocking queue!")
            yield from mv(heating_device.start, 1)

    if run:
        yield from inner()
    logger.info("Plan finished successfully!")


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
    logger: Optional[Logger] = None,
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
    logger : Logger, optional
        Optional logger for the plan.

    See Also
    --------
    program_blower_segment :  Plan to program individual segments in the heating devices.
    """
    if logger is None:
        getLogger(__file__)
    if heating_device.running.get() != EU3508ProgStatusType.NOT_RUNNING:
        logger.warning(
            f"Device {heating_device.name} is not in 'Not Running' state, so the device will be stopped."
        )
        yield from stop(heating_device)
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
                    logger=logger,
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
            logger=logger,
        )
        yield from unmonitor(heating_device.readback)
        yield from unmonitor(heating_device.setpoint)

    yield from open_run(md=_md)
    yield from inner()
    yield from close_run("success")
