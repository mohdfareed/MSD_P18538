"""
Events system. This is used to process outputs from services asynchronously.

Callback functions can be registered to an event. When the event is triggered,
all registered callbacks are called asynchronously. Callbacks either be
coroutines or coroutine functions. Callbacks are called with the arguments
passed to the event trigger when callbacks are coroutine functions. Callbacks
are called without arguments when callbacks are coroutines.

This allows long running tasks to be executed asynchronously without blocking
the main thread. This is useful for services that require long running tasks.
It can also be used an cancellation token to stop long running tasks by simply
adding a cancellation callback to the event; triggering the event will cancel
the task.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Generic

from typing_extensions import ParamSpec

LOGGER = logging.getLogger(__name__)
"""Events system logger."""
P = ParamSpec("P")  # event data type definition


class Event(Generic[P]):
    """An event. Calls a set of event handlers managed through a subscription
    system. When triggered, all subscribers are notified."""

    def __init__(self):
        self.handlers: set[Callable[P, Any] | Coroutine] = set()
        """The handlers of the event."""
        self.trigger_event = asyncio.Event()
        """Event set for the duration of the event trigger."""
        self._handlers_lock = asyncio.Lock()

    async def subscribe(self, callback: Callable[P, Any] | Coroutine):
        """Subscribe to the event."""
        assert not await self.is_subscribed(
            callback
        ), f"Event handler '{callback}' is of invalid type"

        async with self._handlers_lock:
            self.handlers.add(callback)

    async def unsubscribe(self, callback: Callable[P, Any] | Coroutine):
        """Unsubscribe from the event."""
        assert await self.is_subscribed(
            callback
        ), f"Event handler '{callback}' is not subscribed to event '{self}'"

        async with self._handlers_lock:
            self.handlers.remove(callback)

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the event."""
        self.trigger_event.set()
        async with self._handlers_lock:
            for handler in self.handlers:
                LOGGER.debug(f"Executing handler '{handler}'")
                await self._execute_handler(handler, *args, **kwargs)
        self.trigger_event.clear()

    async def is_subscribed(
        self, callback: Callable[P, Any] | Coroutine
    ) -> bool:
        """Check if a callback is subscribed to the event."""
        async with self._handlers_lock:
            return callback in self.handlers

    async def until_triggered(self):
        """Wait until the event is triggered."""
        await self.trigger_event.wait()

    async def _execute_handler(self, handler, *args, **kwargs):
        # execute event handler asynchronously
        if asyncio.iscoroutinefunction(handler):
            asyncio.create_task(handler(*args, **kwargs))
        elif asyncio.iscoroutine(handler):
            asyncio.create_task(handler)
            # unsubscribe in the background to avoid deadlocks
            asyncio.create_task(self.unsubscribe(handler))
        else:  # execute non-async handler in thread
            asyncio.create_task(asyncio.to_thread(handler, *args, **kwargs))

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return await self.trigger(*args, **kwargs)
