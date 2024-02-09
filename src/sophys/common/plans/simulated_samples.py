import argparse

import functools

from ophyd.sim import hw as __simulated_hardware

from bluesky import RunEngine

from bluesky.plans import count, scan, grid_scan
import bluesky.preprocessors as bpp

from sophys.common.utils import set_debug_mode, make_kafka_callback


def with_simulated_hardware(func):
    """Provides the 'hw' argument with a newly generated simulated device set."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        yield from func(*args, hw=__simulated_hardware(), **kwargs)

    return _wrapper


@with_simulated_hardware
def sample_random_1d(*, hw):
    """Small test with a time-spaced random curve."""
    det = hw.rand
    det.kind = "hinted"
    det.start_simulation()

    return (yield from count([det], num=10, delay=0.2))


@with_simulated_hardware
def sample_gaussian_1d(*, hw):
    """Small test with a bell curve."""
    det = hw.det
    motor = hw.motor

    return (yield from scan([det], motor, -4, 4, num=32))


@with_simulated_hardware
def sample_random_2d(*, hw):
    """Small test with a random image."""
    det = hw.rand
    det.kind = "hinted"
    det.start_simulation()
    motor1 = hw.motor1
    motor2 = hw.motor2

    return (yield from grid_scan([det], motor1, -2, 2, 6, motor2, -2, 2, 6))


@with_simulated_hardware
def sample_gaussian_2d(*, hw):
    """Stress test with a big, fast grid scan"""
    det = hw.det4
    motor1 = hw.motor1
    motor2 = hw.motor2

    return (yield from grid_scan([det], motor1, -3, 3, 128, motor2, -3, 3, 128))


if __name__ == "__main__":
    sample_plans = {
        "random-1d": sample_random_1d,
        "gaussian-1d": sample_gaussian_1d,
        "random-2d": sample_random_2d,
        "gaussian-2d": sample_gaussian_2d,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "program_name", choices=sample_plans.keys(), help="Which program to run."
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=1,
        help="Number of times to run the program. (Default: 1)",
    )
    parser.add_argument(
        "--kafka-topic",
        type=str,
        default="swc-kafka-test",
        help="Kafka topic to connect to. (Default: swc-kafka-test)",
    )
    parser.add_argument(
        "--kafka-bootstrap",
        type=str,
        default="localhost:9092",
        help="Kafka bootstrap server address to connect to. (Default: localhost:9092)",
    )
    args = parser.parse_args()

    # TODO: Integrate with queueserver (minimal client)
    RE = RunEngine({})

    set_debug_mode(RE, mock_commands=False)

    for _ in range(args.num):
        plan = sample_plans[args.program_name]()
        final_plan = bpp.subs_wrapper(
            plan,
            [
                make_kafka_callback(
                    args.kafka_topic, bootstrap_servers=args.kafka_bootstrap
                )
            ],
        )
        RE(final_plan)
