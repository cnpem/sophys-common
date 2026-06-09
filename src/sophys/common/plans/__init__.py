from .cumulative_scans import *  # noqa: F403  numpydoc ignore=GL08


from bluesky import plan_stubs as bps
from bluesky.utils import FailedStatus


RETRY_WARNING_MESSAGE = """Calling a plan (%s) with retry on errors.
This is not encouraged, as it can hide buggy behavior and increase dead times.
If possible, fix the underlying issue to avoid needing a retry.
Otherwise, to disable this warning, pass the `ignore_warning` keyword argument as True in the plan.
"""


def _with_retry_decorator(func):  # numpydoc ignore=PR01
    """Decorator for adding retries to an arbitrary Bluesky plan."""
    from functools import wraps

    @wraps(func)
    def __inner(*args, retry_count=3, ignore_warning=False):  # numpydoc ignore=PR01
        """Inner handler for dealing with plan retries."""
        _ret = None

        if not ignore_warning:
            import warnings

            warnings.warn(RETRY_WARNING_MESSAGE % func.__name__, RuntimeWarning)

        retries = 0
        while True:
            try:
                _ret = yield from func(*args)
            except FailedStatus as e:
                retries += 1

                if retries >= retry_count:
                    raise e
            else:
                break

        return _ret

    return __inner


@_with_retry_decorator
def mv_with_retry(*args):  # numpydoc ignore=PR02
    """
    A wrapper around ``bps.mv``, retrying the move if it fails.

    Parameters
    ----------
    *args
        Arguments to plan_stubs.mv.
    retry_count : int, optional
        Maximum amount of retries before failing the move. Defaults to 3.
    ignore_warning : bool, optional
        Ignore the 'not encouraged' warning on every usage. False by default.

    See Also
    --------
    bluesky.plan_stubs.mv : Base move plan stub.
    """
    return (yield from bps.mv(*args))
