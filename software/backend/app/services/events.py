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
    """A callback handler of an event. Used to subscribe to events.

    NOTE: wrap built-in functions with a descriptive name for better logging
    of events and callbacks.
    """

    def __init__(
        self,
        callback: Callable[P, Any],
        one_shot: bool = False,
        blocking: bool = False,
        timeout: float = EVENT_TIMEOUT,
    ):
        assert asyncio.iscoroutinefunction(callback) or callable(
            callback
        ), "Invalid callback type"

        self.callback = callback
        """The callback function."""
        self.one_shot = one_shot
        """Whether the callback is only triggered once."""
        self.blocking = blocking
        """Whether the callback blocks future callbacks."""

        self._triggered = False  # whether the callback has been triggered
        self._timeout = timeout  # the timeout of the callback (seconds)

        self._blocking_queue: asyncio.Queue = asyncio.Queue()
        # queue of callbacks for blocking handlers
        self._running_tasks: set[asyncio.Task] = set()
        # set of all running tasks, including queue processing task

    async def trigger(self, *args: P.args, **kwargs: P.kwargs):
        """Trigger the callback."""
        assert not self._triggered or not self.one_shot, "Callback is one-shot"

        @self._timeout_wrapper(self._timeout)
        async def handler_with_timeout(*args: P.args, **kwargs: P.kwargs):
            try:
                return await self._handler(*args, **kwargs)
            except asyncio.CancelledError:
                LOGGER.debug(f"{self}: Cancelled")
            except Exception as e:
                LOGGER.exception(f"{self}: Error executing callback: {e}")
            finally:
                self._triggered = True  # callback was triggered

        if self.blocking:
            await self._blocking_queue.put(
                (handler_with_timeout, args, kwargs)
            )  # schedule callback
            if len(self._running_tasks) != 0:  # queue is already processing
                return
            task = asyncio.create_task(self._process_blocking_queue())
        else:
            task = asyncio.create_task(handler_with_timeout(*args, **kwargs))

        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)

    async def _process_blocking_queue(self):
        while not self._blocking_queue.empty():
            (
                handler_with_timeout,
                args,
                kwargs,
            ) = await self._blocking_queue.get()
            await handler_with_timeout(*args, **kwargs)
            self._blocking_queue.task_done()

    async def _handler(self, *args: P.args, **kwargs: P.kwargs):
        if asyncio.iscoroutinefunction(self.callback):
            return self.callback(*args, **kwargs)
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
                        await func(*args, **kwargs), duration
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
        try:
            await self._event.wait()
        except asyncio.CancelledError:
            pass

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return await self.trigger(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}{get_args(self)}"

    def __del__(self):
        for handler in set(self.handlers):
            del handler
