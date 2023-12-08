"""
Microphone service.

Provides an interface for capturing audio from a microphone and broadcasting it
to listeners. It uses the events service to broadcast the audio data.
"""

import asyncio
import json
import logging
from typing import Callable, Coroutine

from fastapi import WebSocket, WebSocketDisconnect

from ..models.microphone import MicrophoneConfig
from .events import CancellationToken, Event

LOGGER = logging.getLogger(__name__)
"""Microphone service logger."""


async def start_websocket_microphone(websocket: WebSocket):
    """Start a websocket microphone.

    Args:
        websocket (WebSocket): The websocket to listen to.

    Returns:
        Tuple[Event[bytes], MicrophoneConfig, CancellationToken]: The audio
            capture event, the reported microphone configuration, and the
            cancellation token to stop listening.
    """

    async def socket_listener():
        try:  # read streamed audio data
            return await websocket.receive_bytes()
        except WebSocketDisconnect:
            raise asyncio.CancelledError

    # create microphone
    audio_capture_event: Event[bytes] = Event()
    config = MicrophoneConfig(**json.loads(await websocket.receive_text()))
    LOGGER.info(f"Microphone configuration: {config}")

    # start listening to microphone
    listen_task = asyncio.create_task(
        _listen_to_stream(socket_listener, audio_capture_event)
    )
    canceller = CancellationToken(listen_task.cancel)
    return audio_capture_event, config, canceller


async def _listen_to_stream(
    listener: Callable[[], Coroutine[None, None, bytes]], event: Event[bytes]
):
    while True:
        try:  # read streamed audio data
            data = await listener()
        except asyncio.CancelledError:
            LOGGER.info("Websocket microphone stream shutdown")
            break

        # trigger audio data
        await event.trigger(data)
        await asyncio.sleep(0)  # important for multithreading
