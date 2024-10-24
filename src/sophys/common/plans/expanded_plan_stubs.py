from bluesky import preprocessors as bpp, plan_stubs as bps

from .annotated_default_plans import read


@bpp.run_decorator()
def read_many(devices):
    """Take a reading of many devices, and bundle them into a single Bluesky document."""
    yield from bps.create()
    for device in devices:
        yield from read(device)
    yield from bps.save()
