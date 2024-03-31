import logging

from fastapi import APIRouter, WebSocket, WebSocketException, status

from ..services import transcription as transcription_service
from ..services.audio import microphones, player, speakers
from ..services.events import Event, EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()
_transcription: Event[str] | None = None  # transcription event


@router.websocket("/transcription/stream")
async def stream_transcription(websocket: WebSocket):
    global _transcription
    if _transcription is None:
        raise WebSocketException(
            reason="Transcription service is not running",
            code=status.WS_1002_PROTOCOL_ERROR,
        )

    socket = WebSocketConnection(websocket)
    await socket.connect()
    handler = EventHandler(socket.send)
    await _transcription.subscribe(handler)
    LOGGER.warning("Transcription client connected")
