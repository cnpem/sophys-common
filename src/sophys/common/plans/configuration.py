import typing
from bluesky import protocols
from bluesky.plan_stubs import mv


def configure_picolo_acquisition(
    picolo: protocols.Readable,
    ch1: typing.Optional[bool] = False,
    ch2: typing.Optional[bool] = False,
    ch3: typing.Optional[bool] = False,
    ch4: typing.Optional[bool] = False,
    sample_per_trigger: typing.Optional[int] = 1,
    sample_rate: typing.Optional[int] = None,
    acquisition_time: typing.Optional[float] = None,
    auto_range: typing.Optional[bool] = True,
):
    """
    Configure picoammeter to execute the acquisition.

    Parameters
    ----------
        picolo: Picolo device
            Picolo device to be configured
        ch1: bool = False
            Enable channel 1 configuration
        ch2: bool = False
            Enable channel 2 configuration
        ch3: bool = False
            Enable channel 3 configuration
        ch4: bool = False
            Enable channel 4 configuration
        sample_per_trigger : int
            Number of samples to be acquired by trigger
        sample_rate : int
            Int value based on GIE table to choose the sample rate
        acquisition_time: float
            The time for the acquisition of one sample in seconds.
        auto_range: bool
            Enable auto range.
    """
    picolo.reset_data()

    picolo_channels = []
    if ch1:
        picolo_channels.append(picolo.ch1)
    if ch2:
        picolo_channels.append(picolo.ch2)
    if ch3:
        picolo_channels.append(picolo.ch3)
    if ch4:
        picolo_channels.append(picolo.ch4)

    # Enabling pico channels and setting their acquisition mode as continuous
    yield from mv(
        picolo.ch1.enable,
        0,
        picolo.ch2.enable,
        0,
        picolo.ch3.enable,
        0,
        picolo.ch4.enable,
        0,
    )

    for channel in picolo_channels:
        yield from mv(
            channel.enable,
            1,
            channel.auto_range,
            1 if auto_range else 0,
            channel.acquire_mode,
            1,
        )

    yield from mv(picolo.samples_per_trigger, sample_per_trigger)

    if acquisition_time:
        picolo.set_value(acquisition_time)
    if sample_rate:
        yield from mv(picolo.sample_rate, sample_rate)
