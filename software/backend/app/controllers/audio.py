import asyncio
import logging

from fastapi import APIRouter, WebSocket

from ..services import transcription
from ..services.audio import microphones, player, speakers
from ..services.events import EventHandler
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/audio")
async def stream_audio(websocket: WebSocket):
    socket = WebSocketConnection(websocket)
    mic, config, mic_token = await microphones.create_websocket_mic(socket)
    # mic, config, mic_token = microphones.create_file_mic("~/Downloads/yt2.wav")
    LOGGER.info("Microphone connected")

    # start speaker and transcription
    audio_event, audio_token = await player.start_audio_player(mic)
    speaker_token = await speakers.start_speaker(config, audio_event)
    LOGGER.info("Speaker started")
    # transcription_token = await transcription.start(config, audio_event)
    # LOGGER.info("Transcription started")

    async def shutdown():
        await speaker_token()
        await audio_token()
        await mic_token()
        # await transcription_token()

    shutdown_callback = EventHandler(shutdown, one_shot=True)
    await socket.disconnection_event.subscribe(shutdown_callback)
    # await socket.disconnection_event.trigger()  # TODO: remove this line
    await socket.disconnection_event.until_triggered()
    LOGGER.info("Audio source disconnected")


async def play_effects():
    async def play():
        # play file every 5 seconds
        while True:
            mic, config, _ = microphones.create_file_mic(
                "~/Downloads/yt_effect.wav"
            )
            audio_event, _ = await player.start_audio_player(mic)
            speaker_token = await speakers.start_speaker(config, audio_event)
            await asyncio.sleep(5)
            await speaker_token()

    # play in background
    asyncio.create_task(play())
    LOGGER.info("Effects player started")
