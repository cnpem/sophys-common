# numpydoc ignore=GL08
import asyncio
import functools

from typing import TypeVar, Generic, cast

import numpy as np

from ophyd_async.core import (
    AsyncStatus,
    SignalR,
    SignalW,
    SignalRW,
    StandardReadable,
    WatchableAsyncStatus,
    WatcherUpdate,
    Ignore,
    observe_value,
    DEFAULT_TIMEOUT,
)

from bluesky.protocols import Reading


T = TypeVar("T", bound=int | float)


class BasePositioner(StandardReadable, Generic[T]):
    """
    Base class for a positioner device in ophyd-async.

    This works similarly to the PVPositioner* devices in regular ophyd.
    """

    readback: SignalR[T]
    setpoint: SignalRW[T]

    actuate: SignalW[float] | Ignore
    actuate_value: float = 1.0

    done: SignalR[float] | Ignore
    done_value: float = 1.0

    atol: float = 1.0e-8
    rtol: float = 1.0e-5

    def set_name(
        self, name: str, *, child_name_separator: str | None = None
    ) -> None:  # numpydoc ignore=GL08
        super().set_name(name, child_name_separator=child_name_separator)

        self.readback.set_name(name)

    def _check_done_signal(  # numpydoc ignore=GL08
        self, reading: dict[str, Reading], is_done_event: asyncio.Event
    ):
        if reading[cast(SignalR, self.done).name]["value"] == self.done_value:
            is_done_event.set()

    @WatchableAsyncStatus.wrap
    async def set(self, value: float, timeout=DEFAULT_TIMEOUT):  # numpydoc ignore=PR01
        """Send the positioner to a new position."""
        initial_value = await self.readback.get_value()

        await self.setpoint.set(value)

        if hasattr(self, "actuate"):
            await cast(SignalW, self.actuate).set(self.actuate_value)

        is_done_signal_done = asyncio.Event()

        done_status = None
        if hasattr(self, "done"):
            cast(SignalR, self.done).subscribe_reading(
                functools.partial(
                    self._check_done_signal, is_done_event=is_done_signal_done
                )
            )
            done_status = AsyncStatus(is_done_signal_done.wait())
        else:
            is_done_signal_done.set()

        async for current_value in observe_value(
            self.readback, done_status=done_status, done_timeout=timeout
        ):
            yield WatcherUpdate(
                current=current_value,
                initial=initial_value,
                target=value,
                name=self.name,
            )

            if (
                np.isclose(current_value, value, atol=self.atol, rtol=self.rtol)
                and is_done_signal_done.is_set()
            ):
                break
