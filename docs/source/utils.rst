Utility
=======

Callbacks
---------

.. automodule:: sophys.common.utils.callbacks
    :members:
    :show-inheritance:

----

Registry
--------

.. note::
    The functionality in this module can only be used if ``ophyd-registry`` is installed.
    If you installed the package via ``pip``, either adding the ``registry`` extra, or using ``all`` ought to work.

.. automodule:: sophys.common.utils.registry
    :members:

----

Signals
-------

.. automodule:: sophys.common.utils.signals
    :members:
    :show-inheritance:

----

Data access
-----------

Acessing recently generated data inside a plan can sometimes be useful, allowing
an additional degree of liberty in automating procedures in a plan. However, it
conflicts with the fact that local storage is not the end location of that data:
for information to be processed and analized for its scientific merits, it needs
to be accessible at a later time, and for that to happen, it's end storage medium
is Ibira. And, as with any other EPICS-based data collection procedure, area detectors
save directly to Ibira, bypassing the orchestration layer.

Because of that, local reasoning based on generated data from a recent run is limited
in scope, and can only do so much. It is, nonetheless, still useful in some cases, and
is supported directly in Bluesky, through the :py:func:`bluesky.plan_stubs.subscribe` and
:py:func:`bluesky.plan_stubs.unsubscribe` stub plans, which allows us to configure callbacks
in the :py:class:`bluesky.RunEngine` inside a plan, so we can attach a local databroker
instance to collect the data right there.

Below is an example of such:

.. code-block:: python

    from bluesky import RunEngine, plan_stubs as bps
    from bluesky.plans import count

    from ophyd.sim import hw

    from databroker.v2 import temp as db_temp

    from sophys.common.plans.annotated_default_plans import DETECTORS_TYPE, MD_TYPE
    from sophys.common.utils.data_access import setup_databroker


    def example_plan(detectors: DETECTORS_TYPE, *, num=10, md: MD_TYPE = None):
        md = md or {}
        _md = {**md, "my_other_thing_key": "my_other_thing_value"}

        db = db_temp()

        # Make all Bluesky events go to the databroker catalog
        token = (yield from bps.subscribe("all", db.v1.insert))

        uid = (yield from count(detectors, num=num, delay=0, md=_md))

        # Remove the databroker catalog callback
        yield from bps.unsubscribe(token)

        data_from_count = db[uid]

        # Do some (basic) stuff with our data!
        data_from_count = data_from_count.primary.read()

        data_med = float(sum(data_from_count.rand) / len(data_from_count.rand))
        print("Median (n={}): {:.5f}".format(num, data_med))

        if abs(data_med - 0.5) > 0.0025:
            new_num = num * 2
            print("Not enough data! Will retry with n={}".format(new_num))

            yield from example_plan(detectors, num=new_num, md=md)


    if __name__ == "__main__":
        RE = RunEngine({})

        # No need to call setup_databroker, but doing so won't break anything.
        setup_databroker(RE)

        rand = hw().rand
        rand.kind = "hinted"     # Specific to the simulated random device
        rand.start_simulation()  # Specific to the simulated random device

        RE(example_plan([rand]))

----

Misc.
-----

.. automodule:: sophys.common.utils
    :members:
    :undoc-members:
    :show-inheritance:
