import logging

from fastapi import APIRouter, WebSocket, WebSocketException, status

from ..services import transcription
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


@router.websocket("/transcription/start")
async def start_transcription(websocket: WebSocket):
    global _transcription
    assert _transcription is None, "Transcription service is already running"
    socket = WebSocketConnection(websocket)

    # start microphone
    mic, config, mic_token = await microphones.create_websocket_mic(socket)
    LOGGER.debug("Websocket microphone created. Config: %s", config)
    # mic, config, mic_token = microphones.create_local_mic()

    # connect mic and speaker through audio player
    audio_event, audio_token = await player.start_audio_player(mic)
    LOGGER.debug("Microphone started")
    speaker_token = await speakers.start_speaker(config, audio_event)
    LOGGER.debug("Speaker started")

    # start transcription
    # engine = transcription.engines.WhisperEngine()
    # (
    #     _transcription,
    #     transcription_token,
    # ) = await transcription.start_transcription(engine, config, audio_event)
    # await _transcription.subscribe(transcription.create_console_display())
    # LOGGER.debug("Transcription started")

    async def shutdown():
        global _transcription
        await speaker_token()
        await audio_token()
        await mic_token()
        # await transcription_token()
        _transcription = None
        LOGGER.debug("Transcription stopped")

    shutdown_callback = EventHandler(shutdown, one_shot=True)
    await socket.disconnection_event.subscribe(shutdown_callback)
    await socket.disconnection_event.until_triggered()
