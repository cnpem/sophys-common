import time


def _wait(
    f: callable,
    timeout=5.0,
    timeout_msg="Monitor took too long to complete handling the documents.",
):
    _t = time.time()
    while not f():
        if time.time() - _t >= timeout:
            assert False, timeout_msg
        time.sleep(0.1)
