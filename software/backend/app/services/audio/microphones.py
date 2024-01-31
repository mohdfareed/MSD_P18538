"""
Microphone service.

Provides interfaces for various microphone sources.
"""

import asyncio
import io
import wave

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

    return player, config


async def create_websocket_mic(websocket: WebSocketConnection):
    """Creates a websocket microphone that returns audio chunks from a
    websocket.

    Args:
        websocket (WebSocketConnection): The websocket to read from.

    Returns:
        Callable[[], Coroutine[bytes]]: The audio source.
        MicrophoneConfig: The audio configuration.
    """

    await websocket.connect()
    config = await websocket.receive_obj(MicrophoneConfig)
    config.sample_width //= 8  # convert bits to bytes
    LOGGER.debug(f"Received microphone config: {config}")

    async def receive_audio():
        nonlocal websocket
        audio_bytes = await websocket.receive_bytes()

        audio_stream = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(
            audio_stream,
            format="webm",
            codec="opus",
        )  # FIXME: fails on second chunk due to missing header

        wav_stream = io.BytesIO()
        audio_segment.export(wav_stream, format="wav")
        return wav_stream.getvalue()

    return receive_audio, config


def create_local_mic():
    """Creates a microphone audio player that returns audio chunks from a
    physical microphone.

    Returns:
        Callable[[], Coroutine[bytes]]: The audio source.
        MicrophoneConfig: The audio configuration.
        EventHandler: The cancellation handler.
    """

    mic_config = MicrophoneConfig(
        sample_rate=48000,
        chunk_size=1024,
        sample_width=2,
        num_channels=1,
    )

    mic = LOCAL_AUDIO_SOURCE.open(
        format=LOCAL_AUDIO_SOURCE.get_format_from_width(
            mic_config.sample_width
        ),
        channels=mic_config.num_channels,
        rate=mic_config.sample_rate,
        input=True,
        frames_per_buffer=mic_config.chunk_size,
    )

    def receive_audio():
        nonlocal mic
        return mic.read(mic_config.chunk_size, exception_on_overflow=False)

    async def close_mic():
        nonlocal mic
        mic.stop_stream()
        mic.close()
        LOGGER.debug("Microphone stopped")

    cancellation_handler = EventHandler(close_mic, one_shot=True)

    return receive_audio, mic_config, cancellation_handler
