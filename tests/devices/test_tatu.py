from bluesky import plans as bp

from ophyd import Signal

from sophys.common.devices.tatu import TatuFlyScan


class MockTATUFlyer(TatuFlyScan):
    def __init__(self):
        self.name = "mock_tatu_flyer"

        self.activate = Signal(name=self.name + "_activate")


def test_fly_device(run_engine_without_kafka):
    device = MockTATUFlyer()

    run_engine_without_kafka(bp.fly([device]))
