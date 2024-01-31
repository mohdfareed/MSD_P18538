import asyncio
import io
import wave

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER
from .engines import RecognitionEngine

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 1000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = False
"""Whether to dynamically adjust the energy threshold for recording audio."""


async def start_recorder(
    engine: RecognitionEngine, mic_config: MicrophoneConfig, mic_event: Event
):
    """Start recording audio from a microphone using a speech recognition
    engine.

    Args:
        engine (RecognitionEngine): The speech recognition engine.
        mic_config (MicrophoneConfig): The microphone configuration.
        mic_event (Event): The audio event triggered on new microphone data.

    Returns:
        Tuple[Event[sr.AudioData], CancellationToken]: The recording event and
            the cancellation token.
    """

    # configure the engine's recognizer
    engine.recognizer.energy_threshold = ENERGY_THRESHOLD
    engine.recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

    # buffer = io.BytesIO()
    # with wave.open(buffer, "wb") as f:
    #     f.setnchannels(mic_config.num_channels)
    #     f.setsampwidth(mic_config.sample_width)
    #     f.setframerate(mic_config.sample_rate)
    #     f.writeframes(b"\x00" * 0)  # write empty header (placeholder)
    # source = sr.AudioSource()

    # def write_to_buffer(data):
    #     nonlocal buffer

    source = BufferedAudioSource(mic_config)
    await mic_event.subscribe(source.audio_handler)
    await mic_event.until_triggered()  # wait for first audio packet

    with source:  # adjust for ambient noise
        LOGGER.info("Adjusting recognizer for ambient noise")
        engine.recognizer.adjust_for_ambient_noise(source)
        LOGGER.info("Recognizer adjusted")

    # start recording in the background
    recording_event = Event[sr.AudioData]()
    stopper = engine.recognizer.listen_in_background(
        source,
        recording_event.trigger,
        phrase_time_limit=RECORD_TIMEOUT,
    )

    # stop recording when cancelled
    async def stop():
        nonlocal stopper
        stopper()
        await mic_event.unsubscribe(source.audio_handler)

    cancellation_event = Event()
    handler = EventHandler(stop, one_shot=True)
    await cancellation_event.subscribe(handler)
    return recording_event, cancellation_event


class BufferedAudioSource(sr.AudioSource):
    def __init__(self, mic_config: MicrophoneConfig):
        self.stream = io.BytesIO()
        self.audio_handler = EventHandler(self.stream.write)

        self.SAMPLE_RATE = mic_config.sample_rate
        self.SAMPLE_WIDTH = mic_config.sample_width
        self.CHUNK = mic_config.chunk_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
