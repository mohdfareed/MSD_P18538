"""
Speaker service.

Provides an interface for playing audio to a speaker. It uses the events
service to listen to audio data and play it.
"""

import logging
import wave

import pyaudio

from ...models.microphone import MicrophoneConfig
from ..events import Event

LOGGER = logging.getLogger(__name__)
"""Speaker service logger."""


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
    await mic_event.subscribe(play_audio)
    cancellation_event = Event()
    await cancellation_event.subscribe(mic_event.unsubscribe(play_audio))
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
        with wave.open(file_path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(mic_config.sample_width)
            f.setframerate(mic_config.sample_rate)
            f.writeframes(data)

    # start listening to microphone
    await mic_event.subscribe(write_audio)
    cancellation_event = Event()
    await cancellation_event.subscribe(mic_event.unsubscribe(write_audio))
    return cancellation_event
