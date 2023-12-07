"""
Event system. This is used to process outputs from services asynchronously.

Callback functions can be registered to an event. When the event is triggered,
all registered callbacks are called asynchronously. Callbacks either be
coroutines or coroutine functions. Callbacks are called with the arguments
passed to the event trigger when callbacks are coroutine functions. Callbacks
are called without arguments when callbacks are coroutines.
"""

import asyncio
import logging
from typing import Callable, Coroutine, Generic

from typing_extensions import ParamSpec

LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")


class Event(Generic[P]):
    """An event. When triggered, all subscribers are notified."""

    def __init__(self):
        self._typing = P
        self._subscribers: list[Callable[P, Coroutine] | Coroutine] = []
        self._trigger_event = asyncio.Event()
        self._subscriber_tasks: list[asyncio.Task] = []

    def subscribe(self, callback: Callable[P, Coroutine] | Coroutine):
        """Subscribe to the event."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[P, Coroutine] | Coroutine):
        """Unsubscribe from the event."""
        self._subscribers.remove(callback)

    def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the event."""
        self._trigger_event.set()
        for subscriber in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    task = asyncio.create_task(subscriber(*args, **kwargs))
                elif asyncio.iscoroutine(subscriber):
                    task = asyncio.create_task(subscriber)
                else:
                    raise TypeError(
                        f"Subscriber {subscriber} is not a coroutine or coroutine function"
                    )

                self._subscriber_tasks.append(task)
                task.add_done_callback(self._subscriber_tasks.remove)
            except Exception as e:
                LOGGER.error(f"Error in subscriber {subscriber}: {e}")
        self._trigger_event.clear()

    async def until_triggered(self):
        """Wait until the event is triggered."""
        await self._trigger_event.wait()

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the event."""
        self.trigger(*args, **kwargs)

    def __iadd__(self, callback):
        """Subscribe to the event."""
        self.subscribe(callback)
        return self

    def __isub__(self, callback):
        """Unsubscribe from the event."""
        self.unsubscribe(callback)
        return self

    def __await__(self):
        """Wait until the event is triggered."""
        return self.until_triggered().__await__()

    def __del__(self):
        """Cancel all subscriber tasks."""
        for task in self._subscriber_tasks:
            task.cancel()
        self._subscriber_tasks.clear()
