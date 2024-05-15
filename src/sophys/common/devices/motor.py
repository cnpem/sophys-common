from ophyd import EpicsMotor, Component, EpicsSignal


class ControllableMotor(EpicsMotor):
    """
        Custom EpicsMotor that enabled control before a plan and disables it after.
    """
    control_enabled = Component(EpicsSignal, ".CNEN", kind="config", auto_monitor=True)

    def stage(self):
        super().stage()
        self.control_enabled.set(1)

    def unstage(self):
        super().unstage()
        self.control_enabled.set(0)
