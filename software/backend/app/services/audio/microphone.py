import asyncio
from abc import ABC, abstractmethod

from fastapi import WebSocket, WebSocketDisconnect

from ..events import Event
from . import LOGGER


class Microphone(ABC):
    """A microphone."""

    def __init__(self):
        self.audio_capture_event: Event[bytes] = Event()
        """An event that is triggered when audio is captured."""
        self.sample_rate: int
        """The sample rate of the microphone."""
        self.sample_width: int
        """The sample width of the microphone."""
        self.chunk_size: int
        """The chunk size of the microphone."""

    def startup(self):
        """Start up the microphone."""
        self._stream_task = asyncio.create_task(self._stream())

    def shutdown(self):
        """Shutdown the microphone."""
        self._stream_task.cancel() if self._stream_task else None
        self._stream_task = None

    async def _stream(self):
        try:
            while True:
                data = await self.capture()
                self.audio_capture_event.trigger(data)
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            LOGGER.info("Microphone stream shutdown")
        except Exception as e:
            LOGGER.error(f"Microphone stream error: {e}")
            raise e

    @abstractmethod
    async def capture(self) -> bytes:
        """Capture audio data from the microphone. Must be thread-safe."""
        ...


class WebSocketMicrophone(Microphone):
    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket
        self.chunk_size = 1024
        self.sample_width = 1
        self._sample_rate = None

    @property
    def sample_rate(self) -> int:
        if not self._sample_rate:
            raise RuntimeError("Sample rate is not set yet")
        return self._sample_rate

    async def startup(self):
        await self.websocket.accept()
        self._sample_rate = await self.websocket.receive_json()
        super().startup()

    async def shutdown(self):
        super().shutdown()
        try:  # close websocket
            await self.websocket.close()
        except Exception as e:
            LOGGER.error(f"Error closing websocket: {e}")

    async def capture(self) -> bytes:
        try:
            data = await self.websocket.receive_bytes()
            return data
        except WebSocketDisconnect:
            raise asyncio.CancelledError()
