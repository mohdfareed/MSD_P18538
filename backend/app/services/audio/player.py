"""
Audio player service.

Provides an interface for capturing audio from a microphone.
It uses the events service to broadcast the audio captured to speakers, which
subscribe to a player to receive the audio.
"""

import asyncio
from typing import Callable, Coroutine

from ..events import Event, EventHandler
from . import LOGGER


async def start_audio_player(
    mic: Callable[[], bytes | Coroutine[None, None, bytes]]
):
    """Start an audio player.

    Args:
        mic (Callable[[], bytes]): The audio source.

    Returns:
        Tuple[Event[bytes], CancellationToken]: The audio capture event and the
            cancellation token to stop playing audio.
    """

    # service events
    audio_capture_event = AudioCaptureEvent()
    cancellation_event = MicDisconnectionEvent()

    # service task
    listen_task = asyncio.create_task(
        _listen_to_stream(mic, audio_capture_event, cancellation_event)
    )

    # cancellation token
    handler = EventHandler(listen_task.cancel, one_shot=True)
    await cancellation_event.subscribe(handler)
    return audio_capture_event, cancellation_event


async def _listen_to_stream(
    listener: Callable[[], bytes | Coroutine[None, None, bytes]],
    event: Event[bytes],
    cancellation_event: Event,
):
    try:
        while True:  # read streamed audio data
            if asyncio.iscoroutinefunction(listener):
                data: bytes = await listener()
            else:
                data = listener()  # type: ignore

            # trigger audio data
            await event.trigger(data)
            await asyncio.sleep(0)  # important for multithreading

    except asyncio.CancelledError:
        pass  # cancelled
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
