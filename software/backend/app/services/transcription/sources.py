"""
This module contains classes that record audio data and write it to a queue.

Recorders are used in the transcription module to record audio data from a
source of audio data and write them to a queue. The queue is then used to
transcribe the audio data.
"""

import asyncio
import io

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event

physical_mic = sr.Microphone()
"""The device's physical microphone source."""


class ByteStreamSource(sr.AudioSource):
    """Use a microphone as a source of audio data for speech recognition."""

    def __init__(self, mic_event: Event, mic_config: MicrophoneConfig):
        self.SAMPLE_RATE = mic_config.sample_rate
        self.SAMPLE_WIDTH = mic_config.sample_width
        self.CHUNK = mic_config.chunk_size
        self.mic_event = mic_event
        self.stream = None

    def __enter__(self):
        self.stream = self.ByteStream()
        asyncio.create_task(self.mic_event.subscribe(self.stream.write_async))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream is None:
            return
        asyncio.create_task(
            self.mic_event.unsubscribe(self.stream.write_async)
        )
        self.stream = None

    class ByteStream(io.RawIOBase):
        def __init__(self):
            self.queue = asyncio.Queue[bytes]()
            self._event_loop = asyncio.get_event_loop()

        def read(self, size: int = -1) -> bytes:
            return asyncio.run_coroutine_threadsafe(
                self.read_async(size), self._event_loop
            ).result()

        async def read_async(self, size: int = -1) -> bytes:
            chunk = b""
            while len(chunk) < size:
                chunk += await self.queue.get()
            return chunk

        async def write_async(self, data: bytes) -> None:
            await self.queue.put(data)
