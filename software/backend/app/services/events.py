"""
Events service. This is used to process outputs from services asynchronously.

Callback functions can be registered to an event. When the event is triggered,
all registered callbacks are called asynchronously. Callbacks either be
coroutines or coroutine functions. Callbacks are called with the arguments
passed to the event trigger when callbacks are coroutine functions. Callbacks
are called without arguments when callbacks are coroutines.

This allows long running tasks to be executed asynchronously without blocking
the main thread. This is useful for services that require long running tasks.
"""

import asyncio
import logging
from typing import Callable, Coroutine, Generic

from typing_extensions import ParamSpec

LOGGER = logging.getLogger(__name__)
"""Events service logger."""
P = ParamSpec("P")  # event data type definition


class Event(Generic[P]):
    """An event. When triggered, all subscribers are notified."""

    def __init__(self):
        self.handlers: set[Callable[P, Coroutine] | Coroutine] = set()
        """The handlers of the event."""
        self.trigger_event = asyncio.Event()
        """Event set for the duration of the event trigger."""
        self._handlers_lock = asyncio.Lock()

    async def subscribe(self, callback: Callable[P, Coroutine] | Coroutine):
        """Subscribe to the event."""
        async with self._handlers_lock:
            LOGGER.debug(f"Handler {callback} subscribing to event '{self}'")
            self.handlers.add(callback)

    async def unsubscribe(self, callback: Callable[P, Coroutine] | Coroutine):
        """Unsubscribe from the event."""
        async with self._handlers_lock:
            LOGGER.debug(
                f"Handler {callback} unsubscribing from event '{self}'"
            )
            self.handlers.remove(callback)

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the event."""
        self.trigger_event.set()
        async with self._handlers_lock:
            LOGGER.debug(
                f"Triggering event '{self}' with arguments: {args}, {kwargs}"
            )
            for handler in self.handlers:
                LOGGER.debug(f"Executing handler '{handler}'")
                await self._execute_handler(handler, *args, **kwargs)
        self.trigger_event.clear()

    async def until_triggered(self):
        """Wait until the event is triggered."""
        await self.trigger_event.wait()

    async def _execute_handler(self, handler, *args, **kwargs):
        # execute event handler
        if asyncio.iscoroutinefunction(handler):
            asyncio.create_task(handler(*args, **kwargs))
        elif asyncio.iscoroutine(handler):
            asyncio.create_task(handler)
        else:  # only allow coroutines
            raise TypeError(
                f"Event handler '{handler}' is not a coroutine or coroutine function"
            )
