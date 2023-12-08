import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from ..services import microphone, transcription
from ..services.events import Event

LOGGER = logging.getLogger(__name__)

router = APIRouter()
_transcription: Event[str] | None = None  # transcription event


@router.websocket("/transcription/stream")
async def stream_transcription(websocket: WebSocket):
    global _transcription
    assert _transcription is not None, "Transcription service is not running"
    await websocket.accept()

    async def broadcast(transcript: str):
        """Broadcast a transcript to a client."""
        try:  # try to send transcript to client
            await websocket.send_bytes(str(transcript).encode())
        except WebSocketDisconnect:  # client disconnected
            pass

    await _transcription.subscribe(callback=broadcast)
    LOGGER.warning("Transcription client connected")

    # keep websocket alive
    while websocket.client_state == WebSocketState.CONNECTED:
        await asyncio.sleep(1)

    LOGGER.warning("Transcription client disconnected")
    await _transcription.unsubscribe(callback=broadcast)


@router.websocket("/transcription/start")
async def start_transcription(websocket: WebSocket):
    global _transcription
    assert _transcription is None, "Transcription service is already running"
    await websocket.accept()

    # create microphone
    (
        mic_event,
        mic_config,
        mic_token,
    ) = await microphone.start_websocket_microphone(websocket)

    # start transcription
    engine = transcription.engines.WhisperEngine()
    (
        _transcription,
        transcription_token,
    ) = await transcription.start_transcription(engine, mic_config, mic_event)

    # keep websocket alive
    while websocket.client_state == WebSocketState.CONNECTED:
        await asyncio.sleep(1)

    # stop transcription
    _transcription = None
    transcription_token()
    mic_token()
