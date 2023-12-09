"""
Events system. This is used to process outputs from services asynchronously.

Callback functions can be registered to an event. When the event is triggered,
all registered callbacks are called. Callbacks either be coroutines, coroutine
functions, or standard functions. Callbacks are called with the arguments
passed to the event trigger when callbacks are coroutine functions. Callbacks
are called without arguments when callbacks are coroutines.

This allows long running tasks to be executed asynchronously without blocking
the main thread. This is useful for services that require long running tasks.
It can also be used an cancellation token to stop long running tasks by simply
adding a cancellation callback to the event; triggering the event will cancel
the task.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Coroutine, Generic, get_args

from typing_extensions import ParamSpec, TypeVar

LOGGER = logging.getLogger(__name__)
"""Events system logger."""

P = ParamSpec("P")  # event data type definition
EVENT_TIMEOUT = 2.5  # seconds
LONG_EVENT_TIMEOUT = 15  # seconds


class EventHandler(Generic[P]):
    """A callback handler of an event. Used to subscribe to events."""

    def __init__(
        self,
        callback: Callable[P, Any] | Coroutine,
        one_shot: bool = False,
        blocking: bool = False,
        long_running: bool = False,
    ):
        assert (
            asyncio.iscoroutinefunction(callback)
            or asyncio.iscoroutine(callback)
            or callable(callback)
        ), "Invalid callback type"
        assert not (
            asyncio.iscoroutine(callback) and not one_shot
        ), "Coroutines must be one-shot"

        self.callback = callback
        """The callback function."""
        self.one_shot = one_shot
        """Whether the callback is only triggered once."""
        self.blocking = blocking
        """Whether the callback blocks the event trigger."""
        self._triggered = False  # whether the callback has been triggered
        self._long_running = long_running  # whether timeout is long

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the callback."""
        assert not self._triggered or not self.one_shot, "Callback is one-shot"

        @timeout(LONG_EVENT_TIMEOUT if self._long_running else EVENT_TIMEOUT)
        async def handler(*args: P.args, **kwargs: P.kwargs):
            return await self._handler(*args, **kwargs)

        if self.blocking:
            await handler(*args, **kwargs)
        else:
            asyncio.create_task(handler(*args, **kwargs))

        self._triggered = True

    async def _handler(self, *args: P.args, **kwargs: P.kwargs):
        if asyncio.iscoroutinefunction(self.callback):
            return self.callback(*args, **kwargs)
        elif asyncio.iscoroutine(self.callback):
            return self.callback
        else:
            return asyncio.to_thread(self.callback, *args, **kwargs)  # type: ignore

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        await self.trigger(*args, **kwargs)

    def __eq__(self, other: "EventHandler[P]") -> bool:
        return self.callback == other.callback

    def __hash__(self) -> int:
        return hash(self.callback)

    def __repr__(self) -> str:
        type = self.callback.__class__.__qualname__
        return f"{self.callback.__qualname__}({type})"


class Event(Generic[P]):
    """An event. Calls a set of event handlers managed through a subscription
    system. When triggered, all subscribers are notified."""

    def __init__(self):
        self.handlers: set[EventHandler[P]] = set()
        """The callback handlers of the event."""
        self._handlers_lock = asyncio.Lock()
        self._event = asyncio.Event()

    async def subscribe(self, handler: EventHandler[P]):
        """Subscribe to the event."""
        async with self._handlers_lock:
            LOGGER.debug(f"{self}: Subscribing {handler}")
            self.handlers.add(handler)

    async def unsubscribe(self, handler: EventHandler[P]):
        """Unsubscribe from the event."""
        async with self._handlers_lock:
            LOGGER.debug(f"{self}: Unsubscribing {handler}")
            self.handlers.remove(handler)

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the event."""
        self._event.set()
        async with self._handlers_lock:
            for handler in self.handlers:
                LOGGER.debug(f"{self}: Triggering {handler}")
                try:
                    await handler(*args, **kwargs)
                except Exception as e:
                    LOGGER.exception(f"Error executing {handler}: {e}")
                if handler.one_shot:  # done in background to avoid deadlocks
                    asyncio.create_task(self.unsubscribe(handler))
        self._event.clear()

    async def is_subscribed(
        self, callback: Callable[P, Any] | Coroutine
    ) -> bool:
        """Check if a callback is subscribed to the event."""
        async with self._handlers_lock:
            return callback in self.handlers

    async def until_triggered(self):
        """Wait until the event is triggered."""
        await self._event.wait()

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return await self.trigger(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}{get_args(self)}"


def timeout(duration: float):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), duration)
            except asyncio.TimeoutError:
                LOGGER.exception(
                    f"Execution of {func} timed out after {timeout} seconds"
                )

        return wrapper

    return decorator
