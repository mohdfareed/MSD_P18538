"""
Microphone service.

Provides an interface for capturing audio from a microphone and broadcasting it
to listeners. It uses the events service to broadcast the audio data.
"""

import asyncio
import logging
from typing import Callable, Coroutine

from ..events import Event

LOGGER = logging.getLogger(__name__)
"""Microphone service logger."""


async def start_microphone(
    source: Callable[[], Coroutine[None, None, bytes]] | Coroutine,
):
    """Start a microphone.

    Args:
        config (MicrophoneConfig): The microphone configuration.
        source (Callable[[], bytes]): The audio source.

    Returns:
        Tuple[Event[bytes], CancellationToken]: The audio capture event and the
            cancellation token to stop listening.
    """

    # start listening to microphone
    audio_capture_event: Event[bytes] = Event()
    listen_task = asyncio.create_task(
        _listen_to_stream(source, audio_capture_event)
    )
    cancellation_event = Event()
    await cancellation_event.subscribe(listen_task.cancel)
    return audio_capture_event, cancellation_event


async def _listen_to_stream(
    listener: Callable[[], Coroutine[None, None, bytes]] | Coroutine,
    event: Event[bytes],
):
    try:
        while True:  # read streamed audio data
            if asyncio.iscoroutinefunction(listener):
                data = await listener()
            elif asyncio.iscoroutine(listener):
                data = await listener
            else:
                raise TypeError(f"Invalid listener type: {type(listener)}")

            # trigger audio data
            await event.trigger(data)
            await asyncio.sleep(0)  # important for multithreading
    except asyncio.CancelledError:
        LOGGER.info("Microphone shutdown")
    except Exception as e:
        LOGGER.exception(e)
