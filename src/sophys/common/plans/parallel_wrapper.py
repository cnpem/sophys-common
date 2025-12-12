import asyncio
from bluesky import RunEngine as RE
from threading import Event, Thread
from contextlib import contextmanager


async def wait_msg_to_complete(msg):
    await asyncio.wait_for(RE._command_registry[msg[0]](msg), timeout=10**10)


def run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


@contextmanager
def thread_loop_manager():
    loop = asyncio.new_event_loop()
    thread = Thread(target=run_loop, args=(loop,), daemon=True)
    thread.start()
    try:
        yield loop
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join()


def all_plans_have_finished(plan_has_finished_list):
    return all(
        plan_finished.is_set() for plan_finished in plan_has_finished_list.values()
    )


def parallel_plans_wrapper(*args):
    parallel_plan_list = list(args)
    plan_has_finished_list = {}
    current_event = {}
    current_thread = {}

    # Initialize dictionaries to store the thread and has_finished data
    for list_id, _ in enumerate(parallel_plan_list):
        plan_has_finished_list[list_id] = Event()
        current_thread[list_id] = None

    with thread_loop_manager() as loop:
        # Iterate through all the bluesky messages from all the plans
        while not all_plans_have_finished(plan_has_finished_list):
            for list_id, _ in enumerate(parallel_plan_list):
                try:
                    if not plan_has_finished_list[list_id].is_set():
                        if current_thread[list_id] is None:
                            # Yield one message or yield it in a thread in case of a 'wait' message
                            current_event[list_id] = next(parallel_plan_list[list_id])
                            if current_event[list_id][0] in [
                                "wait",
                                "wait_for",
                                "sleep",
                            ]:
                                current_thread[list_id] = (
                                    asyncio.run_coroutine_threadsafe(
                                        wait_msg_to_complete(current_event[list_id]),
                                        loop,
                                    )
                                )
                            else:
                                yield current_event[list_id]
                        else:
                            # Monitor 'wait' thread until its finished
                            if not current_thread[list_id].done():
                                current_thread[list_id] = None
                except Exception as exception:
                    plan_has_finished_list[list_id].set()
                    print(exception)
