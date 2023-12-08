import asyncio
import logging

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketState

from ..models.microphone import MicrophoneConfig
from ..services import transcription
from ..services.audio import microphone, speaker
from ..services.events import Event
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()
_transcription: Event[str] | None = None  # transcription event


@router.websocket("/transcription/stream")
async def stream_transcription(websocket: WebSocket):
    global _transcription
    # if _transcription is None:
    #     raise WebSocketException(
    #         reason="Transcription service is not running",
    #         code=status.WS_1002_PROTOCOL_ERROR,
    #     )
    socket = WebSocketConnection(websocket)
    await socket.connect()

    # await _transcription.subscribe(callback=socket.send)
    LOGGER.warning("Transcription client connected")

    # keep websocket alive
    await socket.until_disconnected()
    LOGGER.warning("Transcription client disconnected")
    # await _transcription.unsubscribe(callback=broadcast)


@router.websocket("/transcription/start")
async def start_transcription(websocket: WebSocket):
    global _transcription
    assert _transcription is None, "Transcription service is already running"
    await websocket.accept()
    LOGGER.debug("Transcription websocket connection accepted")
    config_text = await websocket.receive_json()
    LOGGER.debug(f"Config received: {config_text}")
    config = MicrophoneConfig(**await websocket.receive_json())
    LOGGER.debug(f"Microphone config received: {config}")

    # create microphone
    mic_event, mic_token = await microphone.start_microphone(
        websocket.receive_bytes
    )
    LOGGER.error("websocket microphone started")
    speaker_token = await speaker.start_speaker(config, mic_event)

    # # start transcription
    # engine = transcription.engines.WhisperEngine()
    # (
    #     _transcription,
    #     transcription_token,
    # ) = await transcription.start_transcription(engine, mic_config, mic_event)

    # keep websocket alive
    while websocket.client_state == WebSocketState.CONNECTED:
        await asyncio.sleep(1)

    # stop transcription
    _transcription = None
    # transcription_token()
    speaker_token()
    mic_token()
