import asyncio
import fcntl
import logging
import os
import subprocess

from fastapi import APIRouter, WebSocket, WebSocketException, status

from ..models.microphone import MicrophoneConfig
from ..services import transcription
from ..services.audio import speakers
from ..services.events import Event
from ..services.websocket import WebSocketConnection

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/audio")
async def stream_audio(websocket: WebSocket):
    socket = WebSocketConnection(websocket)
    await socket.connect()
    LOGGER.info("Audio source connected")

    # receive audio config
    mic_config = await socket.receive_obj(MicrophoneConfig)
    mic_config.sample_width //= 8  # convert bits to bytes
    LOGGER.debug(f"Audio config: {mic_config}")

    # start speaker and transcription
    audio_event = Event[bytes]()
    speaker_token = await speakers.start_speaker(mic_config, audio_event)
    # transcription_token = await transcription.start(mic_config, audio_event)

    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            "pipe:0",
            "-f",
            "s16le",
            "-ar",
            str(mic_config.sample_rate),
            "-ac",
            str(mic_config.num_channels),
            "pipe:1",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # stderr=subprocess.DEVNULL,
        bufsize=10**8,
    )

    if not process.stdout or not process.stdin:
        raise WebSocketException(
            reason="Error starting ffmpeg audio decoding process",
            code=status.WS_1011_INTERNAL_ERROR,
        )

    flags = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
    fcntl.fcntl(process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    LOGGER.debug(f"Starting audio decoding process: {process.pid}")

    try:
        while True:
            audio_chunk = await socket.receive_bytes()
            if not audio_chunk:
                break
            LOGGER.debug(f"Received audio data: {len(audio_chunk)} bytes")

            # Write the .webm audio chunk to ffmpeg's stdin
            process.stdin.write(audio_chunk)
            process.stdin.flush()
            LOGGER.debug(f"Decoding audio data: {len(audio_chunk)} bytes")

            # Play the decoded PCM data from ffmpeg's stdout
            while True:
                try:  # read all available data from the pipe
                    pcm_chunk = os.read(process.stdout.fileno(), 10**8)
                    break
                except BlockingIOError:
                    pass
            LOGGER.debug(f"Decoded audio data: {len(pcm_chunk)} bytes")
            await audio_event.trigger(pcm_chunk)

    except Exception as e:
        LOGGER.exception(f"Error streaming audio: {e}")
    finally:
        LOGGER.warning("Audio source disconnected")
        await speaker_token.trigger()
        # await transcription_token.trigger()
        process.terminate()  # terminate the ffmpeg process
        await asyncio.sleep(0.5)  # time for resources to clean up
        process.kill()
        process.stdin.close()
        process.stdout.close()
