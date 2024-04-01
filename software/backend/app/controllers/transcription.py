import logging

from fastapi import APIRouter, WebSocket, WebSocketException, status

from ..services import transcription as transcription_service
from ..services.events import EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/transcription/stream")
async def stream_transcription(websocket: WebSocket):
    transcription_event = transcription_service.event()
    if transcription_event is None:
        raise WebSocketException(
            reason="Transcription service is not running",
            code=status.WS_1002_PROTOCOL_ERROR,
        )

    socket = WebSocketConnection(websocket)
    await socket.connect()
    handler = EventHandler(socket.send)
    await transcription_event.subscribe(handler)
    LOGGER.warning("Transcription client connected")
