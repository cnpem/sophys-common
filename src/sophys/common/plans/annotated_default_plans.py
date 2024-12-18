"""
This is essentially a copy of https://github.com/bluesky/bluesky/pull/1610,
with some stuff for queueserver annotation added.

The typing part should be removed once that PR is merged.

----

For the motor arguments, the plans expect a list of misc. stuff. To make stuff make sense
in our GUI applications, we developed a simple CSV-like comment to put in the argument's description,
for specifying what each argument in the list means.

The comment starts and ends with the ``-.-`` string, and between those, it has three CSV row entries,
separated by a ';' character, like so:

``-.-row one; row two; row three-.-``

Row one represents the name of each argument in that list, in sequence. For instance, ``grid_scan``
would have the following as their first row: ``motor,start,stop,num``. Meanwhile, ``list_scan`` would
instead have something like ``motor,start,stop``, since it has no ``num`` parameter.

Row two represents the description for each argument, in sequence. It must be the same length as the
first row, though any or all elements in there can be empty (``,,``).

Row three represents the type of each argument, in sequence. As with row two, it must be the same length
as the first row, but unlike the second row, it must have all elements be non-empty, even if it's all just
``typing.Any``.
"""

import functools
import typing

import cycler
from bluesky import plans, plan_stubs, protocols, Msg

from .queueserver_annotation import parameter_annotation_decorator, DEFAULT_ANNOTATION


__all__ = [
    "count",
    "scan",
    "rel_scan",
    "list_scan",
    "rel_list_scan",
    "list_grid_scan",
    "rel_list_grid_scan",
    "log_scan",
    "rel_log_scan",
    "grid_scan",
    "rel_grid_scan",
    "scan_nd",
    "spiral",
    "spiral_fermat",
    "spiral_square",
    "rel_spiral",
    "rel_spiral_fermat",
    "rel_spiral_square",
    "adaptive_scan",
    "rel_adaptive_scan",
    "tune_centroid",
    "tweak",
    "fly",
    "mv",
    "read",
]


DETECTORS_TYPE = typing.Sequence[protocols.Readable]
FLYERS_TYPE = typing.Sequence[protocols.Flyable]
MD_TYPE = typing.Optional[dict]

#: Return type of a plan, usually None. Always optional for dry-runs.
P = typing.TypeVar("P")

MSG_GENERATOR_TYPE = typing.Generator[Msg, typing.Any, typing.Optional[P]]

#: Any plan function that takes a reading given a list of Readables
TAKE_READING_TYPE = typing.Callable[
    [list[protocols.Readable]],
    MSG_GENERATOR_TYPE[typing.Mapping[str, protocols.Reading]],
]

#: Plan function that can be used for each shot in a detector acquisition involving no actuation
PER_SHOT_TYPE = typing.Callable[
    [typing.Sequence[protocols.Readable], typing.Optional[TAKE_READING_TYPE]],
    MSG_GENERATOR_TYPE[None],
]

#: Plan function that can be used for each step in a scan
PER_STEP_TYPE = typing.Callable[
    [
        typing.Sequence[protocols.Readable],
        typing.Mapping[protocols.Movable, typing.Any],
        typing.Mapping[protocols.Movable, typing.Any],
        typing.Optional[TAKE_READING_TYPE],
    ],
    MSG_GENERATOR_TYPE[None],
]


# https://docs.python.org/3/library/functools.html#functools.update_wrapper
# This removes __annotations__, so our type hints get through.
WRAPPER_ASSIGNMENTS = ["__module__", "__name__", "__qualname__", "__doc__"]
__update_wrapper = functools.partial(
    functools.update_wrapper, assigned=WRAPPER_ASSIGNMENTS
)


# Wrapper salad to remove __wrapped__ from the wrapper, so that typehints go through inspect.signature
def wraps(wrapped_func):
    def __wrapper__(wrapper_func):
        wrapped = __update_wrapper(wrapper_func, wrapped_func)
        del wrapped.__wrapped__
        return wrapped

    return __wrapper__


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.count)
def count(
    detectors: DETECTORS_TYPE,
    num: typing.Optional[int] = 1,
    delay: typing.Union[float, typing.Sequence[float], None] = None,
    *,
    per_shot: PER_SHOT_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.count(
            detectors=detectors, num=num, delay=delay, per_shot=per_shot, md=md
        )
    )


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, start, stop``, meaning
``motor`` will go from ``start`` to ``stop``.

In general:

.. code-block:: python

    motor1, start1, stop1,
    motor2, start2, stop2,
    ...,
    motorN, startN, stopN,

-.-motor,start,stop;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory,the ending point in the motor's trajectory;__MOVABLE__,typing.Any,typing.Any-.-
""",
            },
        },
    }
)
@wraps(plans.scan)
def scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    num: int = None,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (yield from plans.scan(detectors, *args, num=num, per_step=per_step, md=md))


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, start, stop``, meaning
``motor`` will go from ``start`` to ``stop``.

In general:

.. code-block:: python

    motor1, start1, stop1,
    motor2, start2, stop2,
    ...,
    motorN, startN, stopN,

-.-motor,start,stop;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory relative to the current position,the ending point in the motor's trajectory relative to the current position;__MOVABLE__,typing.Any,typing.Any-.-
""",
            },
        },
    }
)
@wraps(plans.rel_scan)
def rel_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    num: int = None,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_scan(detectors, *args, num=num, per_step=per_step, md=md)
    )


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, [point1, point2, ....]``.
In general:

.. code-block:: python

    motor1, [point1, point2, ...],
    motor2, [point1, point2, ...],
    ...,
    motorN, [point1, point2, ...]

-.-motor,point list;the n-th motor to move (all of them move simultaneously),the list of points that motor will stop by;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.list_scan)
def list_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (yield from plans.list_scan(detectors, *args, per_step=per_step, md=md))


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, [point1, point2, ....]``.
In general:

.. code-block:: python

    motor1, [point1, point2, ...],
    motor2, [point1, point2, ...],
    ...,
    motorN, [point1, point2, ...]

-.-motor,point list;the n-th motor to move (all of them move simultaneously),the list of points that motor will stop by relative to the starting position;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.rel_list_scan)
def rel_list_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (yield from plans.rel_list_scan(detectors, *args, per_step=per_step, md=md))


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, [point1, point2, ....]``.
In general:

.. code-block:: python

    motor1, [point1, point2, ...],
    motor2, [point1, point2, ...],
    ...,
    motorN, [point1, point2, ...]

-.-motor,point list;the n-th motor to move from slowest to fastest,the list of points that motor will stop by;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.list_grid_scan)
def list_grid_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    snake_axes: typing.Union[bool, typing.Sequence[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.list_grid_scan(
            detectors,
            *args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, [point1, point2, ....]``.
In general:

.. code-block:: python

    motor1, [point1, point2, ...],
    motor2, [point1, point2, ...],
    ...,
    motorN, [point1, point2, ...]

-.-motor,point list;the n-th motor to move from slowest to fastest,the list of points that motor will stop by relative to the starting position;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.rel_list_grid_scan)
def rel_list_grid_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    snake_axes: typing.Union[bool, typing.Sequence[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_list_grid_scan(
            detectors,
            *args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.log_scan)
def log_scan(
    detectors: DETECTORS_TYPE,
    motor: protocols.Movable,
    start: float,
    stop: float,
    num: typing.Optional[int] = 1,
    *,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.log_scan(
            detectors=detectors,
            motor=motor,
            start=start,
            stop=stop,
            num=num,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.rel_log_scan)
def rel_log_scan(
    detectors: DETECTORS_TYPE,
    motor: protocols.Movable,
    start: float,
    stop: float,
    num: typing.Optional[int] = 1,
    *,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_log_scan(
            detectors=detectors,
            motor=motor,
            start=start,
            stop=stop,
            num=num,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, start, stop, num``, meaning
``motor`` will go from ``start`` to ``stop`` in ``num`` steps.

In general:

.. code-block:: python

    motor1, start1, stop1, num1,
    motor2, start2, stop2, num2,
    ...,
    motorN, startN, stopN, numN

-.-motor,start,stop,num;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory,the ending point in the motor's trajectory,the number of steps to take in each iteration;__MOVABLE__,typing.Any,typing.Any,int-.-
""",
            },
        },
    }
)
@wraps(plans.grid_scan)
def grid_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    snake_axes: typing.Union[bool, typing.Sequence[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.grid_scan(
            detectors,
            *args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(
    DEFAULT_ANNOTATION
    | {
        "parameters": {
            "args": {
                "description": """
For one dimension, ``motor, start, stop, num``, meaning
``motor`` will go from ``start`` to ``stop`` in ``num`` steps.

In general:

.. code-block:: python

    motor1, start1, stop1, num1,
    motor2, start2, stop2, num2,
    ...,
    motorN, startN, stopN, numN

-.-motor,start,stop,num;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory relative to the origin,the ending point in the motor's trajectory relative to the origin,the number of steps to take in each iteration;__MOVABLE__,typing.Any,typing.Any,int-.-
""",
            },
        },
    }
)
@wraps(plans.rel_grid_scan)
def rel_grid_scan(
    detectors: DETECTORS_TYPE,
    /,
    *args,
    snake_axes: typing.Union[bool, typing.Sequence[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_grid_scan(
            detectors,
            *args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.scan_nd)
def scan_nd(
    detectors: DETECTORS_TYPE,
    cycler: cycler.Cycler,
    *,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.scan_nd(
            detectors=detectors, cycler=cycler, per_step=per_step, md=md
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.spiral)
def spiral(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_start: float,
    y_start: float,
    x_range: float,
    y_range: float,
    dr: float,
    nth: float,
    *,
    dr_y: typing.Optional[float] = None,
    tilt: float = 0.0,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.spiral(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_start=x_start,
            y_start=y_start,
            x_range=x_range,
            y_range=y_range,
            dr=dr,
            nth=nth,
            dr_y=dr_y,
            tilt=tilt,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.spiral_fermat)
def spiral_fermat(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_start: float,
    y_start: float,
    x_range: float,
    y_range: float,
    dr: float,
    factor: float,
    *,
    dr_y: typing.Optional[float] = None,
    tilt: float = 0.0,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.spiral_fermat(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_start=x_start,
            y_start=y_start,
            x_range=x_range,
            y_range=y_range,
            dr=dr,
            factor=factor,
            dr_y=dr_y,
            tilt=tilt,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.spiral_square)
def spiral_square(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_center: float,
    y_center: float,
    x_range: float,
    y_range: float,
    x_num: float,
    y_num: float,
    *,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.spiral_square(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_center=x_center,
            y_center=y_center,
            x_range=x_range,
            y_range=y_range,
            x_num=x_num,
            y_num=y_num,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.rel_spiral)
def rel_spiral(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_range: float,
    y_range: float,
    dr: float,
    nth: float,
    *,
    dr_y: typing.Optional[float] = None,
    tilt: float = 0.0,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_spiral(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_range=x_range,
            y_range=y_range,
            dr=dr,
            nth=nth,
            dr_y=dr_y,
            tilt=tilt,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.rel_spiral_fermat)
def rel_spiral_fermat(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_range: float,
    y_range: float,
    dr: float,
    factor: float,
    *,
    dr_y: typing.Optional[float] = None,
    tilt: float = 0.0,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_spiral_fermat(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_range=x_range,
            y_range=y_range,
            dr=dr,
            factor=factor,
            dr_y=dr_y,
            tilt=tilt,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.rel_spiral_square)
def rel_spiral_square(
    detectors: DETECTORS_TYPE,
    x_motor: protocols.Movable,
    y_motor: protocols.Movable,
    x_range: float,
    y_range: float,
    x_num: float,
    y_num: float,
    *,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_spiral_square(
            detectors=detectors,
            x_motor=x_motor,
            y_motor=y_motor,
            x_range=x_range,
            y_range=y_range,
            x_num=x_num,
            y_num=y_num,
            per_step=per_step,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.adaptive_scan)
def adaptive_scan(
    detectors: DETECTORS_TYPE,
    target_field: str,
    motor: protocols.Movable,
    start: float,
    stop: float,
    min_step: float,
    max_step: float,
    target_delta: float,
    backstep: bool,
    threshold: float = 0.8,
    *,
    md: MD_TYPE = None,
):
    return (
        yield from plans.adaptive_scan(
            detectors=detectors,
            target_field=target_field,
            motor=motor,
            start=start,
            stop=stop,
            min_step=min_step,
            max_step=max_step,
            target_delta=target_delta,
            backstep=backstep,
            threshold=threshold,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.rel_adaptive_scan)
def rel_adaptive_scan(
    detectors: DETECTORS_TYPE,
    target_field: str,
    motor: protocols.Movable,
    start: float,
    stop: float,
    min_step: float,
    max_step: float,
    target_delta: float,
    backstep: bool,
    threshold: float = 0.8,
    *,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_adaptive_scan(
            detectors=detectors,
            target_field=target_field,
            motor=motor,
            start=start,
            stop=stop,
            min_step=min_step,
            max_step=max_step,
            target_delta=target_delta,
            backstep=backstep,
            threshold=threshold,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.tune_centroid)
def tune_centroid(
    detectors: DETECTORS_TYPE,
    signal: str,
    motor: protocols.Movable,
    start: float,
    stop: float,
    min_step: float,
    num: int = 10,
    step_factor: float = 3.0,
    snake: bool = False,
    *,
    md: MD_TYPE = None,
):
    return (
        yield from plans.tune_centroid(
            detectors=detectors,
            signal=signal,
            motor=motor,
            start=start,
            stop=stop,
            min_step=min_step,
            num=num,
            step_factor=step_factor,
            snake=snake,
            md=md,
        )
    )


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.tweak)
def tweak(
    detectors: DETECTORS_TYPE,
    target_field: str,
    motor: protocols.Movable,
    step: float,
    *,
    md: MD_TYPE = None,
):
    return (
        yield from plans.tweak(
            detectors=detectors,
            target_field=target_field,
            motor=motor,
            step=step,
            md=md,
        )
    )


@parameter_annotation_decorator(
    {
        "parameters": {
            "flyers": {
                "convert_device_names": True,
            },
            "md": {
                "convert_device_names": False,
            },
        },
    }
)
@wraps(plans.fly)
def fly(flyers: FLYERS_TYPE, *, md: MD_TYPE = None):
    return (yield from plans.fly(flyers=flyers, md=md))


@parameter_annotation_decorator(
    {
        "parameters": {
            "args": {
                "description": """
device1,value1,device2,value2, ...
-.-device,value;device to be moved,value to be setted;__MOVABLE__,typing.Any-.-
"""
            }
        }
    }
)
@wraps(plan_stubs.mv)
def mv(*args, group: typing.Any = None, **kwargs: typing.Optional[dict]):
    return (yield from plan_stubs.mv(*args, group=group, **kwargs))


@parameter_annotation_decorator(
    {
        "parameters": {
            "args": {
                "description": """
device1,value1,device2,value2, ...
-.-device,value;device to be moved,value to be setted;__MOVABLE__,typing.Any-.-
"""
            }
        }
    }
)
@wraps(plan_stubs.mvr)
def mvr(*args, group: typing.Any = None, **kwargs: typing.Optional[dict]):
    return (yield from plan_stubs.mvr(*args, group=group, **kwargs))


@parameter_annotation_decorator(
    {
        "parameters": {
            "device": {
                "description": """
-.-device;device to be read;__READABLE__-.-
"""
            }
        }
    }
)
@wraps(plan_stubs.read)
def read(device):
    return (yield from plan_stubs.read(device))
