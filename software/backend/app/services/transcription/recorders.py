"""
This module contains classes that record audio data and write it to a queue.

Recorders are used in the transcription module to record audio data from a
source of audio data and write them to a queue. The queue is then used to
transcribe the audio data.
"""

import asyncio
import io
from abc import ABC

import speech_recognition as sr

from ..audio.microphone import Microphone
from . import LOGGER
from .engines import RecognitionEngine

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 2000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = False
"""Whether to dynamically adjust the energy threshold for recording audio."""

_main_loop = asyncio.get_event_loop()


class Recorder(ABC):
    """A class that records audio data and writes it to a queue.

    Implementations are different types of audio recorders, such as a
    microphone or a byte stream."""

    def __init__(self, source: sr.AudioSource, engine: RecognitionEngine):
        self._stopper = None
        self._recognizer = engine.recognizer
        self._recognizer.energy_threshold = ENERGY_THRESHOLD
        self._recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

        self.engine = engine
        """The speech recognition engine."""
        self.source = source
        """The source of the audio data."""
        self.audio_queue = asyncio.Queue[sr.AudioData]()
        """The queue of audio data."""
        self.data_event = asyncio.Event()
        """The event that is triggered when new audio data is available."""

    async def start(self) -> None:
        """Start recording by listening to the source in the background."""
        if self._stopper is not None:
            raise RuntimeError("Recorder is already running")
        LOGGER.error("Core of recorder started")
        with self.source:  # adjust for ambient noise
            LOGGER.error("Adjusting recognizer for ambient noise")
            self._recognizer.adjust_for_ambient_noise(self.source)

        self._stopper = self._recognizer.listen_in_background(
            self.source, self._callback, phrase_time_limit=RECORD_TIMEOUT
        )

    def stop(self) -> None:
        """Stop recording by stopping the background listening."""
        if self._stopper is None:
            raise RuntimeError("Recorder is not running")
        self._stopper()
        self._stopper = None

    def _callback(self, _, audio: sr.AudioData) -> None:
        # REVIEW: add better audio filtering
        asyncio.run_coroutine_threadsafe(
            self.audio_queue.put(audio), _main_loop
        )
        _main_loop.call_soon_threadsafe(self.data_event.set)


class MicrophoneRecorder(Recorder):
    """A recorder that records audio from the default microphone."""

    def __init__(self, engine: RecognitionEngine):
        self.source = sr.Microphone(sample_rate=16000)
        super().__init__(self.source, engine)


class ByteStreamRecorder(Recorder):
    """A recorder that records audio from a byte stream."""

    def __init__(self, engine: RecognitionEngine, microphone: Microphone):
        self.source = self.ByteStreamMicrophone(microphone)
        super().__init__(self.source, engine)

    class ByteStreamMicrophone(sr.AudioSource):
        def __init__(self, microphone: Microphone):
            self.SAMPLE_RATE = microphone.sample_rate
            self.SAMPLE_WIDTH = microphone.sample_width
            self.CHUNK = microphone.chunk_size
            self.stream = None

            self._mic_event = microphone.audio_capture_event

        def __enter__(self):
            self.stream = self.ByteStream()
            self._mic_event.subscribe(self.stream.write_async)
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            if self.stream is None:
                return
            self._mic_event.unsubscribe(self.stream.write_async)
            self.stream = None

        class ByteStream(io.RawIOBase):
            def __init__(self):
                # self.queue: queue.Queue[bytes] = queue.Queue()
                self.queue = asyncio.Queue[bytes]()

            def read(self, size: int = -1) -> bytes:
                return asyncio.run_coroutine_threadsafe(
                    self.read_async(size), _main_loop
                ).result()

            def write(self, data: bytes) -> None:
                asyncio.run_coroutine_threadsafe(
                    self.write_async(data), _main_loop
                ).result()

            async def write_async(self, data: bytes) -> None:
                await self.queue.put(data)

            async def read_async(self, size: int = -1) -> bytes:
                chunk = b""
                while len(chunk) < size:
                    chunk += await self.queue.get()
                return chunk
