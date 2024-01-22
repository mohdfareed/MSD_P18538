"""
This module contains classes that record audio data and write it to a queue.

Recorders are used in the transcription module to record audio data from a
source of audio data and write them to a queue. The queue is then used to
transcribe the audio data.
"""

import asyncio
import io
import re
import threading
import time

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER

physical_mic = sr.Microphone()
"""The device's physical microphone source."""

_event_loop = asyncio.get_running_loop()


class ByteStreamSource(sr.AudioSource):
    """Use a microphone as a source of audio data for speech recognition."""

    def __init__(self, mic_event: Event, mic_config: MicrophoneConfig):
        self.SAMPLE_RATE = mic_config.sample_rate
        self.SAMPLE_WIDTH = mic_config.sample_width
        self.CHUNK = mic_config.chunk_size
        self.stream = None
        self._mic_event = mic_event
        self._handler = None

    def __enter__(self):
        self.stream = self.ByteStream()
        self._handler = EventHandler(self.stream.write, blocking=True)
        asyncio.run_coroutine_threadsafe(
            self.startup(self._handler),
            asyncio.get_running_loop(),
        ).result()
        # asyncio.create_task(self.startup(self._handler))
        # while not task.done():
        #     print("Waiting for subscription to complete")
        #     pass
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream is None or self._handler is None:
            return

        asyncio.create_task(self._mic_event.unsubscribe(self._handler))
        self.stream = None
        self._handler = None

    async def startup(self, handler: EventHandler):
        LOGGER.debug("Microphone source starting up")
        await self._mic_event.subscribe(handler)
        LOGGER.debug("Microphone source started")

    class ByteStream(io.BytesIO):
        # def __init__(self):
        #     self.buffer
        #     self._event_loop = asyncio.get_running_loop()

        def read(self, size: int = -1) -> bytes:
            # def run_async_read():
            #     asyncio.new_event_loop().run_until_complete(
            #         self.read_async(size)
            #     )

            # thread = threading.Thread(target=run_async_read)
            # thread.start()
            # thread.join()  # Wait for the completion of the async startup
            # return thread.result()
            # print("Reading from stream")
            # return asyncio.run_coroutine_threadsafe(
            #     self.read_async(size), asyncio.get_running_loop()
            # ).result()

            # wait until buffer has enough data
            while not (data := super().read(size)):
                time.sleep(0.1)
            return data

        # async def read_async(self, size: int = -1) -> bytes:
        #     chunk = b""
        #     while len(chunk) < size:
        #         chunk += await self.queue.get()
        #     LOGGER.debug(f"Transcription stream sent {len(chunk)} bytes")
        #     return chunk

        # async def write_async(self, data: bytes) -> None:
        #     await self.queue.put(data)
