from bluesky import preprocessors as bpp, plan_stubs as bps

from .annotated_default_plans import mv, mvr, read
from .queueserver_annotation import parameter_annotation_decorator


_ANNOTATION = {
    "parameters": {
        "md": {
            "convert_device_names": False,
        },
    },
}


def _read_many(devices):
    yield from bps.create()
    for device in devices:
        yield from read(device)
    yield from bps.save()


@parameter_annotation_decorator(_ANNOTATION)
def read_many(devices, md=None):
    """Take a reading of many devices, and bundle them into a single Bluesky document."""

    @bpp.run_decorator(md=md)
    def __inner():
        yield from _read_many(devices)

    return (yield from __inner())


@parameter_annotation_decorator(_ANNOTATION)
def mov(*args, md=None):
    """Move many devices, and bundle their start and end positions in Bluesky documents."""

    @bpp.run_decorator(md=md)
    def __inner():
        devices = [d for i, d in enumerate(args) if i % 2 == 0]

        yield from _read_many(devices)
        yield from mv(*args)
        yield from _read_many(devices)

    return (yield from __inner())


@parameter_annotation_decorator(_ANNOTATION)
def rmov(*args, md=None):
    """Move many devices, and bundle their start and end positions in Bluesky documents."""

    @bpp.run_decorator(md=md)
    def __inner():
        devices = [d for i, d in enumerate(args) if i % 2 == 0]

        yield from _read_many(devices)
        yield from mvr(*args)
        yield from _read_many(devices)

    return (yield from __inner())
