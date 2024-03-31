"""
Microphone service.

Provides interfaces for various microphone sources.
"""

import asyncio
import fcntl
import os
import subprocess
import wave

from fastapi import WebSocketException, status
from pydub import AudioSegment

from ...models.microphone import MicrophoneConfig
from ..events import EventHandler
from ..websocket import WebSocketConnection
from . import LOCAL_AUDIO_SOURCE, LOGGER


def create_file_mic(filename: str, chunk_size: int = 1024):
    """Creates a file microphone that returns audio chunks from a file.

    Args:
        filename (str): The audio file to read from.
        chunk_size (int, optional): The chunk size. Defaults to 1024.

    Returns:
        Callable[[], Coroutine[bytes]]: The audio source.
        MicrophoneConfig: The audio configuration.
        CancelHandler: The cancellation handler.
    """

    with wave.open(filename, "rb") as file:
        config = MicrophoneConfig(
            sample_rate=file.getframerate(),
            chunk_size=chunk_size,
            sample_width=file.getsampwidth(),
            num_channels=file.getnchannels(),
        )

        data = file.readframes(file.getnframes())
        data_queue = asyncio.Queue[bytes]()
        while data:
            chunk = data[:chunk_size]
            data = data[chunk_size:]
            asyncio.run_coroutine_threadsafe(
                data_queue.put(chunk), asyncio.get_event_loop()
            )

    async def player():
        nonlocal data_queue
        return await data_queue.get()

    cancellation_handler = EventHandler(data_queue.join, one_shot=True)

    return player, config, cancellation_handler


async def create_websocket_mic(websocket: WebSocketConnection):
    """Creates a websocket microphone that returns audio chunks from a
    websocket.

    Args:
        websocket (WebSocketConnection): The websocket to read from.

    Returns:
        Callable[[], Coroutine[bytes]]: The audio source.
        MicrophoneConfig: The audio configuration.
        EventHandler: The cancellation handler.
    """

    await websocket.connect()

    # receive audio config
    config = await websocket.receive_obj(MicrophoneConfig)
    config.sample_width //= 8  # convert bits to bytes
    assert config.sample_width == 2  # only supported sample width
    assert config.num_channels == 1  # only supported number of channels
    LOGGER.debug(f"Received microphone config: {config}")

    process = subprocess.Popen(  # audio stream decoding process
        [
            "ffmpeg",
            "-i",
            "pipe:0",
            "-f",
            "wav",
            "-ar",
            str(config.sample_rate),
            "-ac",
            str(config.num_channels),
            "pipe:1",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=10**8,
    )

    # ensure process pipes are open
    if not process.stdout or not process.stdin:
        raise WebSocketException(
            reason="Error starting ffmpeg audio decoding process",
            code=status.WS_1011_INTERNAL_ERROR,
        )

    # start process with stdout as non-blocking
    flags = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
    fcntl.fcntl(process.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    LOGGER.debug(f"Starting audio decoding process: {process.pid}")

    async def receive_audio():
        nonlocal websocket, process
        audio_bytes = await websocket.receive_bytes()
        if not audio_bytes:
            return b""

        # ensure process pipes are still open
        if not process.stdout or not process.stdin:
            raise WebSocketException(
                reason="Error starting ffmpeg audio decoding process",
                code=status.WS_1011_INTERNAL_ERROR,
            )

        # decode audio data from webm to wav
        process.stdin.write(audio_bytes)
        process.stdin.flush()

        # read decoded audio data
        audio_bytes = b""
        while True:
            try:  # read all available data from the pipe
                return os.read(process.stdout.fileno(), 10**8)
            except BlockingIOError:
                pass

    async def shutdown():
        nonlocal websocket, process
        process.terminate()  # terminate the ffmpeg process
        await asyncio.sleep(0.5)  # time for resources to clean up
        process.kill()
        process.stdin.close() if process.stdin else None
        process.stdout.close() if process.stdout else None
        LOGGER.debug("Audio decoding process terminated")

    cancellation_handler = EventHandler(shutdown, one_shot=True)
    return receive_audio, config, cancellation_handler
