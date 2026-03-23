from bluesky.plans import scan
from bluesky.plan_stubs import move_per_step, sleep, trigger_and_read
from sophys.common.plans.annotated_default_plans import (
    DETECTORS_TYPE,
    PER_STEP_TYPE,
    MD_TYPE,
)


def scan_with_delay(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    num: int = None,
    delay: float = 0.2,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    """
    Scan over one multi-motor trajectory.

    Parameters
    ----------
    detectors : list or tuple
        list of 'readable' objects
    *args :
        For one dimension, ``motor, start, stop``.
        In general:

        .. code-block:: python

            motor1, start1, stop1,
            motor2, start2, stop2,
            ...,
            motorN, startN, stopN

        -.-motor,start,stop;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory relative to the current position,the ending point in the motor's trajectory relative to the current position;__MOVABLE__,typing.Any,typing.Any-.-
    num : integer
        number of points
    delay : integer
        Delay between the triggers of the scan.
    per_step : callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md : dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.rel_grid_scan`
    :func:`bluesky.plans.inner_product_scan`
    :func:`bluesky.plans.scan_nd`
    """

    def one_nd_step_with_delay(detectors, step, pos_cache):
        "This is a copy of bluesky.plan_stubs.one_nd_step with a sleep added."
        motors = step.keys()
        yield from move_per_step(step, pos_cache)
        yield from sleep(delay)
        yield from trigger_and_read(list(detectors) + list(motors))

    per_step_scan = one_nd_step_with_delay
    if per_step is not None:
        per_step_scan = per_step

    yield from scan(detectors, *args, num=num, per_step=per_step_scan, md=md)
