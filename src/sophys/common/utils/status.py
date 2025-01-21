import typing

from ophyd.status import StatusBase


class PremadeStatus(StatusBase):
    """
    A dummy Status object useful for simple Ophyd <-> Bluesky compatibility methods.

    Parameters
    ----------
    success : bool
        Whether this Status object should be configured as having failed (False) or succeeded (True).
    exception : Exception, optional
        The exception to set on the Status object when failed. Defaults to an empty Exception object.
        NOTE: An exception cannot be set when the Status is successful.
    """

    def __init__(self, success: bool, *, exception: typing.Optional[Exception] = None):
        super().__init__()

        if success:
            assert (
                exception is None
            ), "Cannot pass an exception when creating a successful Status object."
            self.set_finished()
        else:
            _exc = exception
            if exception is None:
                _exc = Exception()

            self.set_exception(_exc)
