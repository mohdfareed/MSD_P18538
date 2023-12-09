import logging

from fastapi import APIRouter, WebSocket

from ..models.microphone import MicrophoneConfig
from ..services import transcription
from ..services.audio import microphone, speaker
from ..services.events import Event, EventHandler
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


@router.websocket("/transcription/start")
async def start_transcription(websocket: WebSocket):
    global _transcription
    assert _transcription is None, "Transcription service is already running"
    socket = WebSocketConnection(websocket)
    await socket.connect()
    LOGGER.debug("Microphone source connected")
    config = await socket.receive_obj(MicrophoneConfig)
    LOGGER.info(f"Microphone config received: {config}")

    # create microphone
    mic_event, mic_token = await microphone.start_microphone(
        socket.receive_bytes
    )
    LOGGER.debug("Websocket microphone started")

    # speaker_token = await speaker.start_speaker(config, mic_event)
    # speaker_token = await speaker.start_file_speaker(
    #     config, mic_event, "test.wav"
    # )
    # LOGGER.debug("Speaker started")

    # start transcription
    # engine = transcription.engines.WhisperEngine()
    # (
    #     _transcription,
    #     transcription_token,
    # ) = await transcription.start_transcription(engine, mic_config, mic_event)

    async def shutdown():
        global _transcription
        # await transcription_token()
        # await speaker_token()
        await mic_token()
        _transcription = None
        LOGGER.debug("Transcription stopped")

    shutdown_callback = EventHandler(shutdown, one_shot=True)
    await socket.disconnection_event.subscribe(shutdown_callback)
