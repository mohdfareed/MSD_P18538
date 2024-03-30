import asyncio
import fcntl
import logging
import os
import subprocess

import pyaudio
from fastapi import APIRouter, WebSocket, WebSocketException, status

LOGGER = logging.getLogger(__name__)

router = APIRouter()
audio_system = pyaudio.PyAudio()
output_stream = None


@router.websocket("/audio")
async def stream_audio(websocket: WebSocket):
    global output_stream

    await websocket.accept()
    LOGGER.info("Audio source connected")
    output_stream = audio_system.open(
        format=pyaudio.paInt16, channels=1, rate=48000, output=True
    )
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            "pipe:0",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-ac",
            "1",
            "pipe:1",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
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
            audio_chunk = await websocket.receive_bytes()
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
            output_stream.write(pcm_chunk)

    except WebSocketException:
        raise
    except Exception as e:
        LOGGER.exception(f"Error streaming audio: {e}")
    finally:
        LOGGER.warning("Audio source disconnected")
        output_stream.close()
        process.terminate()  # Make sure to terminate the ffmpeg process
        await asyncio.sleep(0.1)  # Give a moment for resources to clean up
        process.kill()
        process.stdin.close()
        process.stdout.close()
