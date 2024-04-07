import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services import transcription
from ..services.audio import microphones, player, speakers
from ..services.events import EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/audio")
async def stream_audio(websocket: WebSocket):
    socket = WebSocketConnection(websocket)
    try:
        mic, config, mic_token = await microphones.create_websocket_mic(socket)
    except WebSocketDisconnect:
        return
    LOGGER.info("Microphone connected")

    # start speaker and transcription
    audio_event, player_token = await player.start_audio_player(mic)
    speaker_token = await speakers.start_speaker(config, audio_event)
    LOGGER.info("Speaker started")
    transcription_token = await transcription.start(config, audio_event)
    LOGGER.info("Transcription started")

    async def shutdown():
        await transcription_token()
        await speaker_token()
        await player_token()
        await mic_token()

    shutdown_callback = EventHandler(shutdown, one_shot=True)
    await socket.disconnection_event.subscribe(shutdown_callback)
    await socket.disconnection_event.until_triggered()
    LOGGER.info("Audio source disconnected")
