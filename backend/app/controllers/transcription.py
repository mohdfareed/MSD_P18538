import asyncio
import logging

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)

from ..services import transcription as transcription_service
from ..services.events import EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/transcription")
async def stream_transcription(websocket: WebSocket):
    transcription_event = transcription_service.event()
    if transcription_event is None:
        LOGGER.error("Transcription requested but service is not running")
        raise WebSocketException(
            reason="Transcription service is not running",
            code=status.WS_1002_PROTOCOL_ERROR,
        )

    socket = WebSocketConnection(websocket)
    await socket.connect()
    handler = EventHandler(socket.send)
    await transcription_event.subscribe(handler)
    LOGGER.info("Transcription client connected")

    async def stop():
        await transcription_event.unsubscribe(handler)
        LOGGER.info("Transcription client disconnected")

    stop_callback = EventHandler(stop, one_shot=True)
    await socket.disconnection_event.subscribe(stop_callback)

    while True:
        try:  # keep connection alive
            await socket.send("")
        except WebSocketDisconnect:
            break
        await asyncio.sleep(1)
