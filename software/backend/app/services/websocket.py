"""
WebSocket abstraction. This module provides a WebSocketConnection class that
abstracts away the WebSocket connection. It provides methods for sending and
receiving data from the WebSocket connection.

Status codes:
https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code
"""

import asyncio
import json
import logging
from typing import Any, Type

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

LOGGER = logging.getLogger(__name__)
"""WebSockets logger."""


class WebSocketConnection:
    """WebSocket connection."""

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def connect(self):
        try:
            await self._websocket.accept()
        except WebSocketDisconnect as e:
            LOGGER.error(f"Error accepting WebSocket connection: {e}")
            await self.disconnect()
            raise e

    async def send(self, data: Any):
        try:
            if self._websocket.client_state != WebSocketState.CONNECTED:
                LOGGER.error(
                    f"WebSocket client state is {self._websocket.client_state}"
                )
                raise RuntimeError("WebSocket client is not connected")

            if isinstance(data, bytes):
                await self._websocket.send_bytes(data)
            elif isinstance(data, str):
                await self._websocket.send_text(data)
            else:
                await self._websocket.send_json(data)
        except WebSocketDisconnect:
            LOGGER.info("WebSocket disconnected")
            await self.disconnect()
            raise
        except RuntimeError as e:
            LOGGER.error(f"Error sending message: {e}")
            await self.disconnect()
            raise e

    async def receive(self, cls: Type = str) -> str | dict | bytes:
        try:
            if self._websocket.client_state != WebSocketState.CONNECTED:
                LOGGER.error(
                    f"WebSocket client state is {self._websocket.client_state}"
                )
                raise RuntimeError("WebSocket client is not connected")

            if cls is bytes:
                return await self._websocket.receive_bytes()
            elif cls is str:
                return await self._websocket.receive_text()
            else:
                return cls(**json.loads(await self._websocket.receive_json()))
        except WebSocketDisconnect:
            LOGGER.info("WebSocket disconnected")
            await self.disconnect()
            raise
        except RuntimeError as e:
            LOGGER.error(f"Error sending message: {e}")
            await self.disconnect()
            raise e

    async def until_disconnected(self):
        """Wait until the WebSocket is disconnected."""
        while self._websocket.state == WebSocketState.CONNECTED:
            await asyncio.sleep(1)

    async def disconnect(self):
        await self._websocket.close()

    def __del__(self):
        if self._websocket.state == WebSocketState.CONNECTED:
            asyncio.create_task(self.disconnect())
