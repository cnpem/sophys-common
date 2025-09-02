import bluesky.preprocessors as bpp
from .annotated_default_plans import scan, DETECTORS_TYPE, PER_STEP_TYPE, MD_TYPE

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition

__all__ = [
    "cumulative_rel_scan",
]


def cumulative_rel_scan(
    detectors: DETECTORS_TYPE,
    *args,
    num: int = None,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    """
    Scan over one multi-motor trajectory relative to current position.
    Without reseting the position after the end of the scan.

    Parameters
    ----------
    detectors : list
        list of 'readable' objects
    *args :
        For one dimension, ``motor, start, stop``, meaning
        ``motor`` will go from ``start`` to ``stop``.

        In general:

        .. code-block:: python

            motor1, start1, stop1,
            motor2, start2, stop2,
            ...,
            motorN, startN, stopN,

        -.-motor,start,stop;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory relative to the current position,the ending point in the motor's trajectory relative to the current position;__MOVABLE__,typing.Any,typing.Any-.-
    num : integer
        number of points
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
    _md = {"plan_name": "rel_linear_scan"}
    md = md or {}
    _md.update(md)
    motors = [motor for motor, start, stop in partition(3, args)]

    @bpp.relative_set_decorator(motors)
    def inner_rel_scan():
        return (yield from scan(detectors, *args, num=num, per_step=per_step, md=_md))

    return (yield from inner_rel_scan())
