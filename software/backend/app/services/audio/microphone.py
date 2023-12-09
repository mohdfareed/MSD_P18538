"""
Microphone service.

Provides an interface for capturing audio from a microphone and broadcasting it
to listeners. It uses the events service to broadcast the audio data.
"""

import asyncio
from typing import Callable, Coroutine

from ..events import Event, EventHandler
from . import LOGGER


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

    # service events
    audio_capture_event = AudioCaptureEvent()
    cancellation_event = MicDisconnectionEvent()

    # service task
    listen_task = asyncio.create_task(
        _listen_to_stream(source, audio_capture_event, cancellation_event)
    )

    # cancellation token
    handler = EventHandler(listen_task.cancel, one_shot=True)
    await cancellation_event.subscribe(handler)
    return audio_capture_event, cancellation_event


async def _listen_to_stream(
    listener: Callable[[], Coroutine[None, None, bytes]] | Coroutine,
    event: Event[bytes],
    cancellation_event: Event,
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
        LOGGER.info("Shutting down microphone")
    except Exception as e:
        LOGGER.exception(e)
    finally:  # cleanup
        await cancellation_event.trigger()


class AudioCaptureEvent(Event[bytes]):
    """An audio capture event."""

    pass


class MicDisconnectionEvent(Event):
    """An event triggered when the microphone disconnects."""

    pass
