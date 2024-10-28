from bluesky import preprocessors as bpp, plan_stubs as bps

from .annotated_default_plans import mv, read


def _read_many(devices):
    yield from bps.create()
    for device in devices:
        yield from read(device)
    yield from bps.save()


@bpp.run_decorator()
def read_many(devices):
    """Take a reading of many devices, and bundle them into a single Bluesky document."""
    yield from _read_many(devices)


@bpp.run_decorator()
def mov(*args):
    """Move many devices, and bundle their start and end positions in Bluesky documents."""
    devices = [d for i, d in enumerate(args) if i % 2 == 0]

    yield from _read_many(devices)
    yield from mv(*args)
    yield from _read_many(devices)
