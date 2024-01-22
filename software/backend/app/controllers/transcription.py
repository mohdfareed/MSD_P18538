import logging

import pyaudio
from fastapi import APIRouter, WebSocket, WebSocketException, status

from ..models.microphone import MicrophoneConfig
from ..services import transcription
from ..services.audio import microphone, player, speaker
from ..services.events import Event, EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()
_transcription: Event[str] | None = None  # transcription event

# TODO: add service for playing audio files (e.g. for testing)


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
    # source, config = await player.create_websocket_player(socket)
    # source, config = player.create_file_player("test.wav")
    source, config = player.create_mic_player()

    # create microphone
    mic_event, mic_token = await microphone.start_microphone(source)
    LOGGER.debug("Websocket microphone started")

    # speaker_token = await speaker.start_speaker(config, mic_event)
    file_speaker_token = await speaker.start_file_speaker(
        config, mic_event, "test_dup.wav"
    )
    # LOGGER.debug("Speaker started")

    # start transcription
    engine = transcription.engines.WhisperEngine()
    (
        _transcription,
        transcription_token,
    ) = await transcription.start_transcription(engine, config, mic_event)
    await _transcription.subscribe(transcription.create_console_display())

    async def shutdown():
        global _transcription
        await transcription_token()
        # await speaker_token()
        await file_speaker_token()
        await mic_token()
        _transcription = None
        LOGGER.debug("Transcription stopped")

    shutdown_callback = EventHandler(shutdown, one_shot=True)
    await socket.disconnection_event.subscribe(shutdown_callback)
    await socket.disconnection_event.until_triggered()
