"""
Speaker service.

Provides an interface for playing audio to a speaker. It uses the events
service to listen to audio data and play it.
"""

import wave

import pyaudio

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER


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

    def sample_width_to_format(width: int):
        return {
            1: pyaudio.paInt8,
            2: pyaudio.paInt16,
            3: pyaudio.paInt24,
            4: pyaudio.paInt32,
        }[width]

    p = pyaudio.PyAudio()
    stream = p.open(
        format=sample_width_to_format(mic_config.sample_width),
        channels=1,  # mono
        rate=mic_config.sample_rate,
        output=True,
    )

    async def play_audio(data: bytes):
        """Play audio data."""
        stream.write(data)

    # start listening to microphone
    handler = EventHandler(play_audio)
    await mic_event.subscribe(handler)

    # create cancellation token
    cancellation_event = Event()
    cancellation_handler = EventHandler(
        mic_event.unsubscribe(handler), one_shot=True
    )
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

    async def write_audio(data: bytes):
        """Play audio data."""
        LOGGER.error(f"Writing audio data to {file_path}")
        with wave.open(file_path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(mic_config.sample_width)
            f.setframerate(mic_config.sample_rate)
            f.writeframes(data)

    # start listening to microphone
    handler = EventHandler(write_audio)
    await mic_event.subscribe(handler)

    # create cancellation token
    cancellation_event = Event()
    cancellation_handler = EventHandler(
        mic_event.unsubscribe(handler), one_shot=True
    )
    await cancellation_event.subscribe(cancellation_handler)
    return cancellation_event
