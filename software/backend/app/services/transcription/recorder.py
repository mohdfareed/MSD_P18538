import asyncio
import io
import threading

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER
from .engines import recognizer

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 1000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = False
"""Whether to dynamically adjust the energy threshold for recording audio."""


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

    with source:  # adjust for ambient noise
        LOGGER.info("Adjusting recognizer for ambient noise")
        recognizer.adjust_for_ambient_noise(source)
        LOGGER.info("Recognizer adjusted")

    # start recording in the background
    recording_event = Event[sr.AudioData]()
    recording_loop, loop_stopper = _create_recording_loop()
    recording_stopper = recognizer.listen_in_background(
        source,
        _create_trigger_wrapper(recording_event, recording_loop),
        phrase_time_limit=RECORD_TIMEOUT,
    )

    # stop recording when cancelled
    async def stop():
        nonlocal recording_stopper, loop_stopper
        recording_stopper()
        await loop_stopper()
        await mic_event.unsubscribe(source.audio_handler)

    cancellation_event = Event()
    handler = EventHandler(stop, one_shot=True)
    await cancellation_event.subscribe(handler)
    return recording_event, cancellation_event


def _create_trigger_wrapper(event, recording_loop):
    def trigger_wrapper(_, audio_data: sr.AudioData):
        async def async_wrapper():
            await event.trigger(audio_data)

        asyncio.run_coroutine_threadsafe(async_wrapper(), recording_loop)

    return trigger_wrapper


def _create_recording_loop():
    recording_loop = asyncio.new_event_loop()

    def start_loop():
        nonlocal recording_loop
        asyncio.set_event_loop(recording_loop)
        recording_loop.run_forever()

    async def stop_loop():
        nonlocal recording_loop
        tasks = [
            t
            for t in asyncio.all_tasks(recording_loop)
            if t is not asyncio.current_task()
        ]
        [task.cancel() for task in tasks]
        recording_loop.stop()

    # create a loop for recording and run it in a dedicated thread
    threading.Thread(target=start_loop).start()
    return recording_loop, stop_loop


class BufferedAudioSource(sr.AudioSource):
    def __init__(self, mic_config: MicrophoneConfig):
        self.stream = self.AudioStream()
        self.audio_handler = EventHandler(self.stream.write)

        self.SAMPLE_RATE = mic_config.sample_rate
        self.SAMPLE_WIDTH = mic_config.sample_width
        self.CHUNK = mic_config.chunk_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    class AudioStream(object):
        def __init__(self) -> None:
            self.buffer = io.BytesIO()
            self.read_position = 0

        def read(self, size: int = -1) -> bytes:
            self.buffer.seek(self.read_position)
            data = self.buffer.read(size)
            self.read_position += len(data)
            if size == -1 or len(data) < size:
                self._reset_buffer()
            return data

        def close(self) -> None:
            self.buffer.close()

        def write(self, data: bytes) -> None:
            self.buffer.write(data)
            self.buffer.seek(0, io.SEEK_END)

        def _reset_buffer(self):
            # reset the buffer only if all data has been read
            if self.buffer.tell() == self.read_position:
                self.buffer.seek(0)
                self.buffer.truncate()
                self.read_position = 0
