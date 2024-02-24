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


async def start_transcription(mic_config: MicrophoneConfig, mic_event: Event):
    """Start transcribing audio from a microphone using a speech recognition
    engine.

    Args:
        engine (RecognitionEngine): The speech recognition engine.
        mic_config (MicrophoneConfig): The microphone configuration.
        mic_event (Event): The audio event triggered on new microphone data.

    Returns:
        Tuple[Event[str], CancellationToken]: The transcription event and the
            cancellation token.
    """

    # initialize transcription
    transcript_event = Event[str]()
    transcript_handler = await _create_handler(mic_config)
    # start recording and transcribing
    record_event, record_canceller = await recorder.start_recorder(
        mic_config, mic_event
    )
    await record_event.subscribe(transcript_handler)

    async def stop():  # stop recording and transcribing
        await record_event.unsubscribe(transcript_handler)
        await record_canceller()

    cancellation_event = Event()
    handler = EventHandler(stop, one_shot=True)
    await cancellation_event.subscribe(handler)
    return transcript_event, cancellation_event


async def _create_handler(mic_config: MicrophoneConfig):
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
            now = datetime.utcnow()
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

    return EventHandler(handler)


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
