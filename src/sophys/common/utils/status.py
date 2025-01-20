from ophyd.status import StatusBase


class PremadeStatus(StatusBase):
    """
    A dummy Status object useful for simple Ophyd <-> Bluesky compatibility methods.

    Parameters
    ----------
    success : bool
        Whether this Status object should be configured as having failed (False) or succeeded (True).
    """

    def __init__(self, success: bool):
        super().__init__()

        if success:
            self.set_finished()
        else:
            self.set_exception(Exception())
