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

from typing_extensions import ParamSpec

LOGGER = logging.getLogger(__name__)
"""Events system logger."""

P = ParamSpec("P")  # event data type definition
EVENT_TIMEOUT = 2.5  # seconds


class EventHandler(Generic[P]):
    """A callback handler of an event. Used to subscribe to events."""

    def __init__(
        self,
        callback: Callable[P, Any] | Coroutine,
        one_shot: bool = False,
        blocking: bool = False,
        timeout: float = EVENT_TIMEOUT,
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
        self._timeout = timeout  # the timeout of the callback (seconds)
        self._running_tasks: set[asyncio.Task] = set()

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the callback."""
        assert not self._triggered or not self.one_shot, "Callback is one-shot"

        @self._timeout_wrapper(self._timeout)
        async def handler_wrapper(*args: P.args, **kwargs: P.kwargs):
            coroutine = self._handler(*args, **kwargs)
            LOGGER.exception(f"Executing {coroutine} in background")
            return await coroutine

        if self.blocking:
            await handler_wrapper(*args, **kwargs)
        else:
            task = asyncio.create_task(handler_wrapper(*args, **kwargs))
            self._running_tasks.add(task)
            task.add_done_callback(self._running_tasks.discard)
        self._triggered = True

    async def _handler(self, *args: P.args, **kwargs: P.kwargs):
        if asyncio.iscoroutinefunction(self.callback):
            return self.callback(*args, **kwargs)
        elif asyncio.iscoroutine(self.callback):
            return self.callback
        elif callable(self.callback):
            return asyncio.to_thread(self.callback, *args, **kwargs)
        else:
            raise TypeError(f"Invalid callback type: {type(self.callback)}")

    def _timeout_wrapper(self, duration: float):
        # add timeout to callback
        def decorator(func: Callable[..., Coroutine]):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs), duration
                    )
                except asyncio.TimeoutError:
                    LOGGER.exception(
                        f"{func} timed out after {duration} seconds"
                    )

            return wrapper

        return decorator

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return await self.trigger(*args, **kwargs)

    def __eq__(self, other: "EventHandler[P]") -> bool:
        return self.callback == other.callback

    def __hash__(self) -> int:
        return hash(self.callback)

    def __repr__(self) -> str:
        type = self.callback.__class__.__qualname__
        return f"{self.callback.__qualname__}({type})"

    def __del__(self):
        for task in self._running_tasks:
            task.cancel()


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
        for handler in set(self.handlers):
            LOGGER.debug(f"{self}: Triggering {handler}")
            try:
                await handler(*args, **kwargs)
            except Exception as e:
                LOGGER.exception(f"Error executing {handler}: {e}")
            if handler.one_shot:  # done in background to avoid deadlocks
                await self.unsubscribe(handler)
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

    def __del__(self):
        for handler in set(self.handlers):
            del handler
