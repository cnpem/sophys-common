from bluesky import RunEngine as RE
import asyncio
from threading import Event, Thread


async def wait_msg_to_complete(msg):
    await asyncio.wait_for(RE._command_registry[msg[0]](msg), timeout=10**10)


def all_plans_have_finished(plan_has_finished_list):
    return all(
        plan_finished.is_set() for plan_finished in plan_has_finished_list.values()
    )


def parallel_plans_wrapper(*args):
    parallel_plan_list = list(args)
    plan_has_finished_list = {}
    current_event = {}
    current_thread = {}

    # Initialize dictionaries to store the thread, event and has_finished data
    for list_id, _ in enumerate(parallel_plan_list):
        plan_has_finished_list[list_id] = Event()
        current_event[list_id] = parallel_plan_list[list_id]
        current_thread[list_id] = None

    # Iterate through all the bluesky messages from all the plans
    while not all_plans_have_finished(plan_has_finished_list):
        for list_id, _ in enumerate(parallel_plan_list):
            try:
                if not plan_has_finished_list[list_id].is_set():
                    if current_thread[list_id] is None:
                        # Yield one message or yield it in a thread in case of a 'wait' message
                        current_event[list_id] = next(parallel_plan_list[list_id])
                        if current_event[list_id][0] in ["wait", "wait_for", "sleep"]:
                            current_thread[list_id] = Thread(
                                target=asyncio.run,
                                args=(wait_msg_to_complete(current_event[list_id]),),
                            )
                            current_thread[list_id].start()
                        else:
                            yield current_event[list_id]
                    else:
                        # Monitor 'wait' thread until its finished
                        if not current_thread[list_id].is_alive():
                            current_thread[list_id] = None
            except Exception as exception:
                plan_has_finished_list[list_id].set()
                print(exception)
