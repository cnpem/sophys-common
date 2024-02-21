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

import copy
import functools
import inspect
import typing

from bluesky import plans, protocols, Msg


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
]


DETECTORS_TYPE = typing.Sequence[protocols.Readable]
MOTORS_TYPE = typing.Sequence[typing.Union[protocols.Movable, typing.Any]]
NUM_TYPE = typing.Optional[int]
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
    [typing.Iterable[protocols.Readable], typing.Optional[TAKE_READING_TYPE]],
    MSG_GENERATOR_TYPE,
]

#: Plan function that can be used for each step in a scan
PER_STEP_TYPE = typing.Callable[
    [
        typing.Iterable[protocols.Readable],
        typing.Mapping[protocols.Movable, typing.Any],
        typing.Mapping[protocols.Movable, typing.Any],
        typing.Optional[TAKE_READING_TYPE],
    ],
    MSG_GENERATOR_TYPE,
]


DEFAULT_ANNOTATION = {
    "parameters": {
        "detectors": {
            "convert_device_names": True,
        },
        "md": {
            "convert_device_names": False,
        },
    },
}


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


try:
    from bluesky_queueserver.manager.annotation_decorator import (
        parameter_annotation_decorator,
    )
except ImportError:

    def parameter_annotation_decorator(annotation):
        """
        Copy of the official one, without validation.
        See https://github.com/bluesky/bluesky-queueserver/blob/main/bluesky_queueserver/manager/annotation_decorator.py
        """

        def function_wrap(func):
            if inspect.isgeneratorfunction(func):

                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    return (yield from func(*args, **kwargs))

            else:

                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

            # Always create the copy (annotation dictionary may be reused)
            nonlocal annotation
            annotation = copy.deepcopy(annotation)

            sig = inspect.signature(func)
            parameters = sig.parameters

            param_unknown = []
            if "parameters" in annotation:
                for p in annotation["parameters"]:
                    if p not in parameters:
                        param_unknown.append(p)
            if param_unknown:
                msg = (
                    f"Custom annotation parameters {param_unknown} are not "
                    f"in the signature of function '{func.__name__}'."
                )
                raise ValueError(msg)

            setattr(wrapper, "_custom_parameter_annotation_", annotation)

            return wrapper

        return function_wrap


@parameter_annotation_decorator(DEFAULT_ANNOTATION)
@wraps(plans.count)
def count(
    detectors: DETECTORS_TYPE,
    num: NUM_TYPE = 1,
    delay: typing.Union[float, typing.Iterable, None] = None,
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
    *args: MOTORS_TYPE,
    num: NUM_TYPE = None,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.scan(
            detectors=detectors, args=args, num=num, per_step=per_step, md=md
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

-.-motor,start,stop;the n-th motor to move from slowest to fastest,the starting point in the motor's trajectory, relative to the current position,the ending point in the motor's trajectory, relative to the current position;__MOVABLE__,typing.Any,typing.Any-.-
""",
            },
        },
    }
)
@wraps(plans.rel_scan)
def rel_scan(
    detectors: DETECTORS_TYPE,
    *args: MOTORS_TYPE,
    num: NUM_TYPE = None,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_scan(
            detectors=detectors, args=args, num=num, per_step=per_step, md=md
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

-.-motor,point list;the n-th motor to move (all of them move simultaneously),the list of points that motor will stop by;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.list_scan)
def list_scan(
    detectors: DETECTORS_TYPE,
    *args: MOTORS_TYPE,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.list_scan(
            detectors=detectors, args=args, per_step=per_step, md=md
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

-.-motor,point list;the n-th motor to move (all of them move simultaneously),the list of points that motor will stop by, relative to the starting position;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.rel_list_scan)
def rel_list_scan(
    detectors: DETECTORS_TYPE,
    *args: MOTORS_TYPE,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_list_scan(
            detectors=detectors, args=args, per_step=per_step, md=md
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

-.-motor,point list;the n-th motor to move from slowest to fastest,the list of points that motor will stop by;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.list_grid_scan)
def list_grid_scan(
    detectors: DETECTORS_TYPE,
    *args: MOTORS_TYPE,
    snake_axes: typing.Union[bool, typing.Iterable[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.list_grid_scan(
            detectors=detectors,
            args=args,
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

-.-motor,point list;the n-th motor to move from slowest to fastest,the list of points that motor will stop by, relative to the starting position;__MOVABLE__,typing.List[typing.Any]-.-
""",
            },
        },
    }
)
@wraps(plans.rel_list_grid_scan)
def rel_list_grid_scan(
    detectors: DETECTORS_TYPE,
    *args: MOTORS_TYPE,
    snake_axes: typing.Union[bool, typing.Iterable[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.rel_list_grid_scan(
            detectors=detectors,
            args=args,
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
    num: NUM_TYPE = 1,
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
    num: NUM_TYPE = 1,
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
    *args: MOTORS_TYPE,
    snake_axes: typing.Union[bool, typing.Iterable[protocols.Movable]] = False,
    per_step: PER_STEP_TYPE = None,
    md: MD_TYPE = None,
):
    return (
        yield from plans.grid_scan(
            detectors=detectors,
            args=args,
            snake_axes=snake_axes,
            per_step=per_step,
            md=md,
        )
    )
