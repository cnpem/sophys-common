"""
This is essentially a copy of https://github.com/bluesky/bluesky/pull/1610,
with some stuff for queueserver annotation added.

The typing part should be removed once that PR is merged.
"""

import copy
import functools
import inspect
import typing

from bluesky import plans


__all__ = ["count"]


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


@parameter_annotation_decorator(
    {
        "description": "Take one or more readings from detectors.",
        "parameters": {
            "detectors": {
                "description": "List of 'readable' devices.",
                "annotation": "typing.Sequence[bluesky.protocols.Readable]",
                "convert_device_names": True,
            },
            "num": {
                "description": "Number of readings to take\nIf None, capture data until canceled.",
            },
            "delay": {
                "description": "Time delay in seconds between successive readings.",
            },
            "per_shot": {
                "description": "Hook for customizing action of inner loop (messages per step).",
            },
            "md": {
                "description": "Metadata.",
                "convert_device_names": False,
            },
        },
    }
)
@functools.wraps(plans.count)
def count(
    detectors,
    num: typing.Optional[int] = 1,
    delay: typing.Union[float, typing.Iterable, None] = None,
    *,
    per_shot: typing.Optional[typing.Callable] = None,
    md: typing.Optional[dict] = None,
):
    return (
        yield from plans.count(
            detectors=detectors, num=num, delay=delay, per_shot=per_shot, md=md
        )
    )
