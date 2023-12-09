"""
WebSocket abstraction. This module provides a WebSocketConnection class that
abstracts away the WebSocket connection. It provides methods for sending and
receiving data from the WebSocket connection.

Status codes:
https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code
"""

import asyncio
import logging
from typing import Any, Coroutine, Type, TypeVar

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

LOGGER = logging.getLogger(__name__)
"""WebSockets logger."""
T = TypeVar("T")


class WebSocketConnection:
    """WebSocket connection."""

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def connect(self):
        """Accept the WebSocket connection."""
        try:
            await self._websocket.accept()
        # reraise but add a more descriptive message
        except Exception as e:
            await self.disconnect()
            raise e.__class__(
                f"Failed to accept WebSocket connection: {e}"
            ) from e

    async def send(self, data: Any):
        """Send data through the WebSocket."""
        try:
            if self._websocket.client_state != WebSocketState.CONNECTED:
                raise RuntimeError("WebSocket client is not connected")

            if isinstance(data, bytes):
                await self._websocket.send_bytes(data)
            elif isinstance(data, str):
                await self._websocket.send_text(data)
            else:
                await self._websocket.send_json(data)
        except WebSocketDisconnect:  # treat as a cancelled operation
            await self.disconnect()
            raise asyncio.CancelledError("WebSocket disconnected")

    async def receive_bytes(self) -> bytes:
        """Receive bytes from the WebSocket."""
        return await self._receive(self._websocket.receive_bytes())

    async def receive_text(self) -> str:
        """Receive text from the WebSocket."""
        return await self._receive(self._websocket.receive_text())

    async def receive_obj(self, cls: Type[T]) -> T:
        """Receive an object from the WebSocket."""
        return cls(**await self._receive(self._websocket.receive_json()))

    async def _receive(self, receiver: Coroutine):
        try:
            if self._websocket.client_state != WebSocketState.CONNECTED:
                raise RuntimeError("WebSocket client is not connected")
            return await receiver
        except WebSocketDisconnect:
            await self.disconnect()
            raise asyncio.CancelledError("WebSocket disconnected")

    async def until_disconnected(self):
        """Wait until the WebSocket is disconnected."""
        while self._websocket.state == WebSocketState.CONNECTED:
            await asyncio.sleep(1)

    async def disconnect(self):
        """Disconnect the WebSocket."""
        if self._websocket.state != WebSocketState.CONNECTED:
            return  # already disconnected

        try:
            await self._websocket.close()
        except Exception as e:
            LOGGER.exception(e)

    def __del__(self):
        if self._websocket.state == WebSocketState.CONNECTED:
            asyncio.create_task(self.disconnect())
