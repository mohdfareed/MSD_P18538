import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Callable, Coroutine

import speech_recognition as sr

from . import LOGGER

# globals
recorder: sr.Recognizer = sr.Recognizer()
"""The speech recognition engine."""

# constants
PHRASE_TERMINATOR = "\n"
"""The indicator of an end of a phrase."""

_PHRASE_TIMEOUT = 2.5  #  the maximum pause between phrases (seconds)
_RECORD_TIMEOUT = 0.5  # the maximum recording chunk size (seconds)
_MAX_RECORD_DURATION = 5  # the maximum recording duration (seconds)
_MIN_RECORD_DURATION = 0.15  # the minimum recording duration (seconds)

# configure the recorder
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False


async def transcribe(
    source: sr.AudioSource,
    recognizer: Callable[[sr.AudioData], Coroutine[None, None, str]],
) -> AsyncGenerator[str, None]:
    """Generate transcription of audio from a source using a recognition engine
    progressively. Yields the transcription of the audio, separated as phrases.

    Args:
        source (AudioSource): The audio source to record from.
        recognizer (AudioData -> str): The recognition engine. Defaults to
        Google's speech recognition engine.

    Yields:
        str: The transcription of the audio in the provided queue.
        PHRASE_TERMINATOR indicates the start of a new phrase.
    """

    # start listening in the background
    recordings, data_event, stopper = _record(source)
    transcription = _transcribe(recordings, recognizer, data_event)
    try:  # transcribe the audio
        async for transcript in transcription:
            await asyncio.sleep(0)  # important for multithreading
            yield transcript
    finally:
        transcription.aclose()  # close generator
        stopper()  # stop listening


async def _transcribe(
    recordings: asyncio.Queue[sr.AudioData],
    recognizer: Callable[[sr.AudioData], Coroutine[None, None, str]],
    data_event: asyncio.Event,
) -> AsyncGenerator[str, None]:
    phrase_time = datetime.min  # last time new audio was received
    phrase_buffer = bytes()  # buffer of current (incomplete) phrase audio
    sample_rate = 0  # the sample rate of the audio
    sample_width = 0  # the sample width of the audio

    while True:  # wait for new audio data
        if recordings.empty():
            await data_event.wait()
            data_event.clear()

        # check for a new phrase (pause in speech)
        now = datetime.utcnow()
        if now - phrase_time > timedelta(seconds=_PHRASE_TIMEOUT):
            phrase_buffer = bytes()
            yield PHRASE_TERMINATOR  # indicate a pause between phrases
        phrase_time = now  # update last time new audio was received

        # build phrase audio data
        while not recordings.empty():
            audio_data = await recordings.get()
            if not sample_rate or not sample_width:
                sample_rate = audio_data.sample_rate
                sample_width = audio_data.sample_width

            # add audio data to buffer
            phrase_buffer += audio_data.get_raw_data()
            if len(phrase_buffer) > sample_rate * _MAX_RECORD_DURATION:
                phrase_time = datetime.min  # start a new phrase
                break  # stop if the buffer is too large
            if len(phrase_buffer) < sample_rate * _MIN_RECORD_DURATION:
                continue  # wait for more audio data

        try:  # transcribe the audio
            audio_data = sr.AudioData(phrase_buffer, sample_rate, sample_width)
            yield await recognizer(audio_data)
        except sr.UnknownValueError:
            continue  # unrecognized audio
        except sr.RequestError as e:
            LOGGER.warning("Transcription failed: %s", e)
            continue  # recognition engine error


def _record(source: sr.AudioSource = sr.Microphone(sample_rate=16000)):
    recordings: asyncio.Queue[sr.AudioData] = asyncio.Queue()
    new_data_event = asyncio.Event()
    main_loop = asyncio.get_event_loop()

    with source:  # adjust for ambient noise
        LOGGER.debug("Adjusting listener for ambient noise")
        recorder.adjust_for_ambient_noise(source)

    def callback(_, audio: sr.AudioData):
        # add audio data to the queue and trigger new data event
        asyncio.run_coroutine_threadsafe(recordings.put(audio), main_loop)
        main_loop.call_soon_threadsafe(new_data_event.set)

    stopper = recorder.listen_in_background(
        source, callback, phrase_time_limit=_RECORD_TIMEOUT
    )  # start listening in the background

    # stopper is a function that stops the background listening
    return recordings, new_data_event, stopper
