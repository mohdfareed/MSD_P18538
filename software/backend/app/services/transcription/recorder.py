import asyncio
import queue

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER
from .engines import recognizer

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 1000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = True
"""Whether to dynamically adjust the energy threshold for recording audio."""

recording_loop = asyncio.get_event_loop()
"""Global recording event loop."""


async def start_recorder(mic_config: MicrophoneConfig, mic_event: Event):
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
    recognizer.energy_threshold = ENERGY_THRESHOLD
    recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

    # listen to the microphone
    source = BufferedAudioSource(mic_config)
    await mic_event.subscribe(source.audio_handler)
    await mic_event.until_triggered()  # wait for first audio packet
    await _adjust_for_ambient_noise(source)  # adjust for ambient noise

    # start recording in the background
    recording_event = Event[sr.AudioData]()
    recording_stopper = recognizer.listen_in_background(
        source,
        _create_trigger_wrapper(recording_event),
        phrase_time_limit=RECORD_TIMEOUT,
    )

    # stop recording when cancelled
    async def stop():
        nonlocal recording_stopper, mic_event
        recording_stopper()
        await mic_event.unsubscribe(source.audio_handler)
        LOGGER.debug("Transcription recording stopped")

    cancellation_event = Event()
    cancellation_handler = EventHandler(stop, one_shot=True)
    await cancellation_event.subscribe(cancellation_handler)
    return recording_event, cancellation_event


def _create_trigger_wrapper(event: Event):
    def trigger_wrapper(_, audio_data: sr.AudioData):
        global recording_loop

        async def async_wrapper():
            await event.trigger(audio_data)

        asyncio.run_coroutine_threadsafe(async_wrapper(), recording_loop)

    return trigger_wrapper


async def _adjust_for_ambient_noise(source: "BufferedAudioSource"):
    with source:  # adjust for ambient noise
        LOGGER.info("Adjusting recognizer for ambient noise")
        await recording_loop.run_in_executor(
            None, recognizer.adjust_for_ambient_noise, source
        )
        LOGGER.info("Recognizer adjusted")


class BufferedAudioSource(sr.AudioSource):
    def __init__(self, mic_config: MicrophoneConfig):
        self.stream = self.AudioStream(mic_config)
        self.audio_handler = EventHandler(self.stream.write, sequential=True)

        self.SAMPLE_RATE = mic_config.sample_rate
        self.SAMPLE_WIDTH = mic_config.sample_width
        self.CHUNK = mic_config.chunk_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    class AudioStream(object):
        def __init__(self, mic_config: MicrophoneConfig) -> None:
            self.buffer = queue.Queue()
            self.config = mic_config

        def write(self, data: bytes):
            for byte in data:
                self.buffer.put(byte)

        def read(self, size: int) -> bytes:
            data = bytearray()
            num_bytes = (
                size * self.config.sample_width * self.config.num_channels
            )

            for _ in range(num_bytes):
                try:  # stop if no data is available for 0.5 seconds
                    data.append(self.buffer.get(timeout=0.5))
                except queue.Empty:
                    return b""
            return data
