from datetime import datetime, timedelta
from queue import Queue  # thread-safe queue
from time import sleep
from typing import Any, Callable, Generator

import speech_recognition as sr
from audio import core as audio
from audio import engines, logger

# constants
PHRASE_TERMINATOR = "\n"
"""The indicator of an end of a phrase."""

_phrase_timeout = 2.5  #  the maximum pause between phrases (seconds)


def transcribe(
    recordings: Queue[bytes] = audio.recordings,
    sample_rate: int = audio.source.SAMPLE_RATE,
    sample_width: int = audio.source.SAMPLE_WIDTH,
    recognize: Callable[[sr.AudioData], str] = engines.google_recognize,
) -> Generator[str, Any, None]:
    """
    Transcribe audio in a recording queue using a recognition engine
    progressively. Yields the transcription of the audio, separated by
    phrases.

    Args:
        recordings (Queue): The queue of recorded audio chunks.
        recognize (AudioData -> str): The recognition engine. Defaults to
        Google's speech recognition engine.

    Yields:
        str: The transcription of the audio. PHRASE_TERMINATOR indicates the
        start of a new phrase.
    """

    phrase_time: datetime = datetime.min  # last time new audio was received
    phrase_buffer = bytes()  # buffer of current (incomplete) phrase audio

    while True:
        if recordings.empty():
            continue  # wait for new audio data

        # check for a new phrase (pause in speech)
        now = datetime.utcnow()
        if now - phrase_time > timedelta(seconds=_phrase_timeout):
            phrase_buffer = bytes()
            yield PHRASE_TERMINATOR  # indicate a pause between phrases
        phrase_time = now

        # build phrase audio data
        while not recordings.empty():
            data = recordings.get()
            phrase_buffer += data
        audio_data = sr.AudioData(phrase_buffer, sample_rate, sample_width)

        try:  # transcribe the audio)
            yield recognize(audio_data)
        except sr.UnknownValueError:
            continue  # unrecognized audio
        except sr.RequestError as e:
            logger.error("Transcription failed: %s", e)
            continue  # recognition engine error
        sleep(0)  # important for multithreading
