"""
Microphone service.

Provides an interface for capturing audio from a microphone and broadcasting it
to listeners. It uses the events service to broadcast the audio data.
"""

import asyncio
import logging
from typing import Callable, Coroutine

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import CancellationToken, Event

LOGGER = logging.getLogger(__name__)
"""Microphone service logger."""


async def start_microphone(
    source: Callable[[], Coroutine[None, None, bytes]],
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
    canceller = CancellationToken(listen_task.cancel)
    return audio_capture_event, canceller


async def _listen_to_stream(
    listener: Callable[[], Coroutine[None, None, bytes]],
    event: Event[bytes],
):
    while True:
        try:  # read streamed audio data
            data = await listener()
        except asyncio.CancelledError:
            LOGGER.info("Microphone shutdown")
            break

        # trigger audio data
        await event.trigger(data)
        await asyncio.sleep(0)  # important for multithreading
