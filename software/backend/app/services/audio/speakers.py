"""
Speaker service.

Provides an interface for playing audio to a speaker. It uses the events
service to listen to audio data and play it.
"""

import wave

import pyaudio  # type: ignore

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER

LOCAL_AUDIO_SOURCE = pyaudio.PyAudio()
"""The local audio source."""
DEVICE_INDEX = int(
    LOCAL_AUDIO_SOURCE.get_default_output_device_info()["index"]
)
"""The default audio device index."""


async def start_speaker(mic_config: MicrophoneConfig, mic_event: Event[bytes]):
    """Start a speaker.

    Args:
        mic_config (MicrophoneConfig): The microphone configuration.
        mic_event (Event[bytes]): The audio event triggered on new microphone
            data.

    Returns:
        Tuple[Event[bytes], MicrophoneConfig, CancellationToken]: The audio
            capture event, the reported microphone configuration, and the
            cancellation token to stop listening.
    """

    stream = LOCAL_AUDIO_SOURCE.open(
        format=LOCAL_AUDIO_SOURCE.get_format_from_width(
            mic_config.sample_width
        ),
        channels=mic_config.num_channels,
        rate=mic_config.sample_rate,
        output=True,
        output_device_index=DEVICE_INDEX,
    )

    def write_audio(data: bytes):
        try:
            stream.write(data)
        except OSError:
            pass  # disconnected

    # start listening to microphone
    handler = EventHandler(write_audio, sequential=True, timeout=1)
    await mic_event.subscribe(handler)

    async def stop_speaker():
        try:
            await mic_event.unsubscribe(handler)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            LOGGER.error(f"Exception stopping speaker: {e}")
        finally:
            LOGGER.debug("Speaker stopped")

    # create cancellation token
    cancellation_event: Event[...] = Event()
    cancellation_handler = EventHandler(stop_speaker, one_shot=True)
    await cancellation_event.subscribe(cancellation_handler)
    return cancellation_event


async def start_file_speaker(
    mic_config: MicrophoneConfig, mic_event: Event[bytes], file_path: str
):
    """Start a speaker that writes audio to a file.

    Args:
        mic_config (MicrophoneConfig): The microphone configuration.
        mic_event (Event[bytes]): The audio event triggered on new microphone
            data.
        file_path (str): The file path to write audio data to.

    Returns:
        Tuple[Event[bytes], MicrophoneConfig, CancellationToken]: The audio
            cancellation token to stop listening.
    """
    buffer = bytes()

    async def write_audio(data: bytes):
        nonlocal buffer
        buffer += data
        with wave.open(file_path, "wb") as f:
            f.setnchannels(mic_config.num_channels)
            f.setsampwidth(mic_config.sample_width)
            f.setframerate(mic_config.sample_rate)
            f.writeframes(buffer)

    # start listening to microphone
    handler = EventHandler(write_audio)
    await mic_event.subscribe(handler)

    async def stop_speaker():
        await mic_event.unsubscribe(handler)
        LOGGER.debug("Speaker stopped")

    # create cancellation token
    cancellation_event: Event[...] = Event()
    cancellation_handler = EventHandler(stop_speaker, one_shot=True)
    await cancellation_event.subscribe(cancellation_handler)
    return cancellation_event
