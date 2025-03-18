from types import SimpleNamespace
from ophyd.sim import SynAxis, SynGauss, Syn2DGauss, SynPeriodicSignal


def instantiate_sim_devices():
    """Analogue of ophyd.sim.hw, but without overlapping device names."""

    simulated_hardware = SimpleNamespace()

    simulated_hardware.motor = SynAxis(name="motor", labels={"motors"})
    simulated_hardware.det = SynGauss(
        "det",
        simulated_hardware.motor,
        "motor",
        center=0,
        Imax=1,
        sigma=1,
        labels={"detectors"},
    )
    simulated_hardware.noisy_det = SynGauss(
        "noisy_det",
        simulated_hardware.motor,
        "motor",
        center=0,
        Imax=1,
        noise="uniform",
        sigma=1,
        noise_multiplier=0.1,
        labels={"detectors"},
    )

    simulated_hardware.motor1 = SynAxis(name="motor1", labels={"motors"})
    simulated_hardware.motor2 = SynAxis(name="motor2", labels={"motors"})
    simulated_hardware.det4 = Syn2DGauss(
        "det4",
        simulated_hardware.motor1,
        "motor1",
        simulated_hardware.motor2,
        "motor2",
        center=(0, 0),
        Imax=1,
        labels={"detectors"},
    )

    simulated_hardware.delayed_motor = SynAxis(
        name="delayed_motor", labels={"motors"}, delay=5.0
    )
    simulated_hardware.delayed_det = SynGauss(
        "delayed_det",
        simulated_hardware.delayed_motor,
        "delayed_motor",
        center=0,
        Imax=1,
        sigma=1,
        labels={"detectors"},
    )

    simulated_hardware.delayed_motor1 = SynAxis(
        name="delayed_motor1", labels={"motors"}, delay=5.0
    )
    simulated_hardware.delayed_motor2 = SynAxis(
        name="delayed_motor2", labels={"motors"}, delay=5.0
    )
    simulated_hardware.delayed_det4 = Syn2DGauss(
        "delayed_det4",
        simulated_hardware.delayed_motor1,
        "delayed_motor1",
        simulated_hardware.delayed_motor2,
        "delayed_motor2",
        center=(0, 0),
        Imax=1,
        labels={"detectors"},
    )

    simulated_hardware.rand = SynPeriodicSignal(name="rand", labels={"detectors"})
    simulated_hardware.rand.start_simulation()
    simulated_hardware.rand.kind = "hinted"

    return simulated_hardware
