import logging

from bluesky import RunEngine


__global_dbs = {}


def get_run_data(run_uid: str, run_metadata: dict, /):
    """
    Get the result data from the run with the given UID.

    Usually only the most recent run(s) are available via this method, so
    for more permanent data, access the relevant Ibira path.

    An example on how to use this is provided below:

    .. code-block:: python

        from bluesky import RunEngine
        from bluesky.plans import count

        from ophyd.sim import hw

        from sophys.common.plans.annotated_default_plans import DETECTORS_TYPE, MD_TYPE
        from sophys.common.utils.data_access import get_run_data, setup_databroker


        def example_plan(detectors: DETECTORS_TYPE, *, md: MD_TYPE = None):
            md = md or {}
            _md = {**md, "my_other_thing_key": "my_other_thing_value"}

            uid = (yield from count(detectors, num=10, delay=0.1, md=_md))

            try:
                data_from_count = get_run_data(uid, _md)
            except Exception:
                pass
            else:
                data_from_count.primary.read().to_dataframe().to_csv('my_count.csv', sep=' ', index=False)


        if __name__ == "__main__":
            RE = RunEngine({})

            # This may be ommited, and all it will do is not save the csv file at the end.
            setup_databroker(RE)

            RE(example_plan([hw().det]))

    Parameters
    ----------
    run_uid : str
        The UID of the run. Corresponds to the start document's UID.
    run_metadata : dict
        The metadata of that run. Usually the final ``md`` dict.

    Raises
    ------
    Exception
        If no data is available to search for. This is possibly due to not having
        called :func:`sophys.common.utils.data_access.setup_databroker` before-hand.
    KeyError
        The given UID does not map to a run in the broker.
    """
    global __global_dbs

    if len(__global_dbs) == 0:
        raise Exception(
            "No data available in Databroker. Did you call `sophys.common.utils.data_access.setup_databroker`?"
        )

    for re, (db, _) in __global_dbs.items():
        try:
            return db[run_uid]
        except KeyError:
            pass

    raise KeyError("No run with the given uid was found.")


def setup_databroker(run_engine: RunEngine):
    """
    Configure a Databroker instance in ``run_engine``.

    This is necessary for us to be able to access the most recent run data directly
    from a plan, in order to make runtime decisions on the plan's course.
    """
    global __global_dbs
    if run_engine in __global_dbs:
        return

    try:
        from databroker.v2 import temp
    except ImportError as e:
        logging.error("Databroker is not available in the current environment!")
        raise e

    db = temp()
    sub_ticket = run_engine.subscribe(db.v1.insert)
    __global_dbs[run_engine] = (db, sub_ticket)
