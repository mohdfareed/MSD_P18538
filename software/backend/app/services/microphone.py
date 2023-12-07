import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

from .events import Event

LOGGER = logging.getLogger(__name__)


class WebSocketMicrophone:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        """The websocket source of the audio data."""
        self.audio_capture_event: Event[bytes] = Event()
        """An event that is triggered when audio is captured."""
        self.sample_width: int = 1
        """The sample width of the microphone."""
        self.chunk_size: int = 1024
        """The chunk size of the microphone."""
        self._sample_rate = None

    @property
    def sample_rate(self) -> int:
        """The sample rate of the microphone."""
        if not self._sample_rate:
            raise RuntimeError("Sample rate is not set yet")
        return self._sample_rate

    async def startup(self):
        # establish websocket connection
        await self.websocket.accept()
        # read microphone configuration
        self._sample_rate = await self.websocket.receive_json()
        # start listening to audio
        asyncio.create_task(self._stream())

    async def shutdown(self):
        try:  # close websocket
            await self.websocket.close()
        except Exception as e:
            LOGGER.error(f"Error closing websocket: {e}")

    async def _stream(self):
        try:
            while True:
                # read audio data
                data = await self.websocket.receive_bytes()
                # dispatch audio data to listeners
                await self.audio_capture_event.trigger(data)
                await asyncio.sleep(0)  # important for multithreading
        except asyncio.CancelledError or WebSocketDisconnect:
            LOGGER.info("Microphone stream shutdown")
        except Exception as e:
            LOGGER.error(f"Microphone stream error: {e}")
            raise e
