import asyncio
from datetime import datetime, timedelta

import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event, EventHandler
from . import LOGGER, recorder
from .engines import RecognitionEngineError, UnrecognizedAudioError, recognize

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 1000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = False
"""Whether to dynamically adjust the energy threshold for recording audio."""

PHRASE_TERMINATOR = "\n"
"""The indicator of an end of a phrase."""
_PHRASE_TIMEOUT = 2.5  #  the maximum pause between phrases (seconds)
_MIN_RECORD_DURATION = 0.5  # the minimum recording duration (seconds)

transcription_event: Event[str] | None = None
"""The global transcription event."""


async def start(mic_config: MicrophoneConfig, audio_source: Event[bytes]):
    """Start transcribing audio from a microphone using a speech recognition
    engine.

    Args:
        mic_config (MicrophoneConfig): The microphone configuration.
        audio_source (Event[bytes]): The audio event triggered on new audio
        data.

    Returns:
        CancellationToken: The transcription cancellation token.
    """
    global transcription_event
    assert transcription_event is None, "Transcription is already running"

    # start listening to the microphone
    audio_event, cancel_recorder = await recorder.start_recorder(
        mic_config, audio_source
    )
    # initialize transcription
    transcription_event, audio_handler = await _create_handler(mic_config)
    await audio_event.subscribe(audio_handler)

    async def stop():  # stop recording and transcribing
        global transcription_event
        transcription_event = None
        await audio_event.unsubscribe(audio_handler)
        await cancel_recorder()

    cancellation_event = Event()
    await cancellation_event.subscribe(EventHandler(stop, one_shot=True))
    return cancellation_event


def event():
    """Get the global transcription event.

    Returns:
        Event[str]: The transcription event.
    """
    global transcription_event
    return transcription_event


async def _create_handler(mic_config: MicrophoneConfig):
    """Create a transcription event that triggers when new transcriptions are
    available and an audio handler that processes audio data.

    Args:
        mic_config (MicrophoneConfig): The microphone configuration.

    Returns:
        Event[str]: The transcription event.
        EventHandler: The audio date handler.
    """
    transcript_event = Event[str]()
    phrase_time = datetime.min  # last time new audio was received
    phrase_buffer = bytes()  # buffer of incomplete phrase audio

    # mutex locks
    time_lock = asyncio.Lock()
    buffer_lock = asyncio.Lock()

    async def handler(audio_data: sr.AudioData):
        nonlocal phrase_time, phrase_buffer

        # check for a new phrase (pause in speech)
        async with time_lock:
            now = datetime.now()
            if now - phrase_time > timedelta(seconds=_PHRASE_TIMEOUT):
                # indicate a pause between phrases
                await transcript_event.trigger(PHRASE_TERMINATOR)
                phrase_buffer = bytes()
            phrase_time = now  # update last time new audio was received

        # add audio data to buffer
        async with buffer_lock:
            phrase_buffer += audio_data.get_raw_data()
            if (  # check if the buffer is too small
                len(phrase_buffer)
                < mic_config.sample_rate * _MIN_RECORD_DURATION
            ):  #  wait for more audio data (api minimum is 0.1s)
                return

        try:  # transcribe the audio
            audio_data = sr.AudioData(
                phrase_buffer,
                mic_config.sample_rate,
                mic_config.sample_width,
            )
            # broadcast the transcript
            await transcript_event.trigger(await recognize(audio_data))

        except UnrecognizedAudioError:
            return  # wait for more audio data
        except RecognitionEngineError as e:
            LOGGER.exception(f"Error recognizing audio: {e}")
            return

    return transcript_event, EventHandler(
        handler, timeout=None, sequential=True
    )


def create_console_display():
    """Create a display that prints transcriptions to the console."""

    max_lines = 5
    lines = []

    async def display(transcript: str):
        nonlocal lines
        if transcript == PHRASE_TERMINATOR:
            lines.append("")
            if len(lines) > max_lines:
                lines = lines[-max_lines:]
        else:
            lines[-1] = transcript

        print("Transcription:")
        print("\n".join(lines), end="\r", flush=True)

    return EventHandler(display)
