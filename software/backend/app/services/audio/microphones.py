"""
Microphone service.

Provides interfaces for various microphone sources.
"""

import asyncio
import os
import subprocess
import wave

from fastapi import WebSocketDisconnect, WebSocketException, status

from ...models.microphone import MicrophoneConfig
from ..events import EventHandler
from ..websocket import WebSocketConnection
from . import LOGGER


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

    filename = os.path.abspath(os.path.expanduser(filename))
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
        LOGGER.debug(f"Loaded audio file: {filename}")

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

    # audio stream decoding process
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i",
        "pipe:0",
        "-f",
        "s16le",
        "-ar",
        str(config.sample_rate),
        "-ac",
        str(config.num_channels),
        "pipe:1",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    async def receive_audio():
        nonlocal websocket, process
        try:
            audio_bytes = await websocket.receive_bytes()
        except WebSocketDisconnect as e:
            raise asyncio.CancelledError from e
        if not audio_bytes:
            return b""

        # ensure process pipes are still open
        if not process.stdout or not process.stdin:
            raise WebSocketException(
                reason="Audio decoding process terminated unexpectedly",
                code=status.WS_1011_INTERNAL_ERROR,
            )

        try:
            # decode audio data from webm to wav
            process.stdin.write(audio_bytes)
            await process.stdin.drain()

            # read decoded audio data
            audio_bytes = await asyncio.wait_for(process.stdout.read(10**8), 1)
            return audio_bytes
        except (BrokenPipeError, asyncio.CancelledError):
            return b""
        except asyncio.TimeoutError:
            LOGGER.error("Audio decoding process timed out")
            return b""

    async def shutdown():
        nonlocal websocket, process
        process.terminate()  # terminate the ffmpeg process
        await asyncio.sleep(0.5)  # time for resources to clean up
        process.kill()
        process.stdin.close() if process.stdin else None
        LOGGER.debug("Audio decoding process terminated")

    cancellation_handler = EventHandler(shutdown, one_shot=True)
    return receive_audio, config, cancellation_handler
