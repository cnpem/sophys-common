import multiprocessing

from caproto.server import PVGroup, SubGroup, pvproperty, run as run_caproto_server
from caproto.server.records import MotorFields


async def broadcast_precision_to_fields(record):
    """Update precision of all fields to that of the given record."""

    precision = record.precision
    for field, prop in record.field_inst.pvdb.items():
        if hasattr(prop, "precision"):
            await prop.write_metadata(precision=precision)


async def motor_record_simulator(instance, async_lib, defaults=None, tick_rate_hz=10.0):
    """
    A simple motor record simulator.

    Parameters
    ----------
    instance : pvproperty (ChannelDouble)
        Ensure you set ``record='motor'`` in your pvproperty first.

    async_lib : AsyncLibraryLayer

    defaults : dict, optional
        Defaults for velocity, precision, acceleration, limits, and resolution.

    tick_rate_hz : float, optional
        Update rate in Hz.
    """
    if defaults is None:
        defaults = dict(
            velocity=0.1,
            precision=3,
            acceleration=1.0,
            resolution=1e-6,
            tick_rate_hz=10.0,
            user_limits=(0.0, 100.0),
        )

    fields: MotorFields = instance.field_inst
    have_new_position = False

    async def value_write_hook(fields, value):
        nonlocal have_new_position
        # This happens when a user puts to `motor.VAL`
        # print("New position requested!", value)
        have_new_position = True

    fields.value_write_hook = value_write_hook

    await instance.write_metadata(precision=defaults["precision"])
    await broadcast_precision_to_fields(instance)

    await fields.velocity.write(defaults["velocity"])
    await fields.seconds_to_velocity.write(defaults["acceleration"])
    await fields.motor_step_size.write(defaults["resolution"])
    await fields.user_low_limit.write(defaults["user_limits"][0])
    await fields.user_high_limit.write(defaults["user_limits"][1])

    dwell = 1.0 / tick_rate_hz
    while True:
        if fields.stop.value != 0:
            await fields.stop.write(0)

        target_pos = instance.value
        diff = target_pos - fields.user_readback_value.value
        if abs(diff) < 1e-9 and not have_new_position:
            await async_lib.library.sleep(dwell)
            continue

        # Support .CNEN
        if fields.enable_control.value == 0:
            await async_lib.library.sleep(dwell)
            continue

        await fields.done_moving_to_value.write(0)
        await fields.motor_is_moving.write(1)

        # compute the total movement time based an velocity
        total_time = abs(diff / fields.velocity.value)
        # compute how many steps, should come up short as there will
        # be a final write of the return value outside of this call
        num_steps = int(total_time // dwell)

        readback = fields.user_readback_value.value
        step_size = diff / num_steps if num_steps > 0 else 0.0
        resolution = max((fields.motor_step_size.value, 1e-10))

        for _ in range(num_steps):
            if fields.stop.value != 0:
                await fields.stop.write(0)
                await instance.write(readback)
                break
            if fields.stop_pause_move_go.value == "Stop":
                await instance.write(readback)
                break

            readback += step_size
            raw_readback = readback / resolution
            await fields.user_readback_value.write(readback)
            await fields.dial_readback_value.write(readback)
            await fields.raw_readback_value.write(raw_readback)
            await async_lib.library.sleep(dwell)
        else:
            # Only executed if we didn't break
            await fields.user_readback_value.write(target_pos)

        await fields.motor_is_moving.write(0)
        await fields.done_moving_to_value.write(1)
        have_new_position = False


class FakeMotor(PVGroup):
    motor = pvproperty(value=0.0, name="", record="motor", precision=3)

    def __init__(
        self,
        *args,
        velocity=0.1,
        precision=3,
        acceleration=1.0,
        resolution=1e-6,
        user_limits=(0.0, 100.0),
        tick_rate_hz=10.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._have_new_position = False
        self.tick_rate_hz = tick_rate_hz
        self.defaults = {
            "velocity": velocity,
            "precision": precision,
            "acceleration": acceleration,
            "resolution": resolution,
            "user_limits": user_limits,
        }

    @motor.startup
    async def motor(self, instance, async_lib):
        # Start the simulator:
        await motor_record_simulator(
            self.motor,
            async_lib,
            self.defaults,
            tick_rate_hz=self.tick_rate_hz,
        )


SOFT_IOC_PREFIX = "TEST:"


class MockSlitIOC(PVGroup):
    top = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="TOP"
    )
    bottom = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="BOTTOM"
    )
    left = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="LEFT"
    )
    right = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="RIGHT"
    )

    v_gap = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-20, 20), prefix="VGAP"
    )
    v_offset = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="VOFF"
    )
    h_gap = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-20, 20), prefix="HGAP"
    )
    h_offset = SubGroup(
        FakeMotor, velocity=100.0, precision=4, user_limits=(-10, 10), prefix="HOFF"
    )


class TestIOC(PVGroup):
    slit = SubGroup(MockSlitIOC, prefix="SLIT:")


def _ioc_init():
    ioc = TestIOC(SOFT_IOC_PREFIX)
    run_caproto_server(ioc.pvdb)


def start_soft_ioc() -> tuple[str, callable]:
    # NOTE: This is needed so epics-base doesn't complain about 'forking with threads' on Linux.
    ctx = multiprocessing.get_context("spawn")
    p = ctx.Process(target=_ioc_init)
    p.start()

    def stop_soft_ioc():
        p.terminate()
        # NOTE: Arbitrary value, not too long as to make the test ending take too long in case this happens.
        p.join(2.0)
        if p.is_alive():
            p.kill()

    return SOFT_IOC_PREFIX, stop_soft_ioc
