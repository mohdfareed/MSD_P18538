from datetime import datetime, timedelta
from queue import Queue  # thread-safe queue
from time import sleep
from typing import Any, Callable, Generator

import speech_recognition as sr
from audio import logger

# globals
recorder: sr.Recognizer = sr.Recognizer()
"""The speech recognition engine."""

# constants
PHRASE_TERMINATOR = "\n"
"""The indicator of an end of a phrase."""
_PHRASE_TIMEOUT = 2.5  #  the maximum pause between phrases (seconds)
_RECORD_TIMEOUT = 0.5  # the maximum recording chunk size (seconds)
_MAX_RECORD_DURATION = 5  # the maximum recording duration (seconds)

# configure the recorder
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False


def transcribe(
    source: sr.AudioSource, recognizer: Callable[[sr.AudioData], str]
) -> Generator[str, Any, None]:
    """Generate transcription of audio from a source using a recognition engine
    progressively. Yields the transcription of the audio, separated as phrases.

    Args:
        source (AudioSource): The audio source to record from.
        recognizer (AudioData -> str): The recognition engine. Defaults to
        Google's speech recognition engine.

    Yields:
        str: The transcription of the audio in the provided queue.
        PHRASE_TERMINATOR indicates the start of a new phrase.
        None: If the audio could not be recognized.
    """

    recordings = _record(source)  # start listening in the background
    phrase_time = datetime.min  # last time new audio was received
    phrase_buffer = bytes()  # buffer of current (incomplete) phrase audio
    sample_rate = 0  # the sample rate of the audio
    sample_width = 0  # the sample width of the audio

    while True:
        if recordings.empty():
            sleep(0.1)  # reduce cpu usage
            continue  # wait for new audio data

        # check for a new phrase (pause in speech)
        now = datetime.utcnow()
        if now - phrase_time > timedelta(seconds=_PHRASE_TIMEOUT):
            phrase_buffer = bytes()
            yield PHRASE_TERMINATOR  # indicate a pause between phrases
        phrase_time = now  # update last time new audio was received

        # build phrase audio data
        while not recordings.empty():
            audio_data = recordings.get()  # read from the queue
            # update sample rate and width
            if not sample_rate or not sample_width:
                sample_rate = audio_data.sample_rate
                sample_width = audio_data.sample_width
            # add audio data to buffer
            phrase_buffer += audio_data.get_raw_data()
            if len(phrase_buffer) > sample_rate * _MAX_RECORD_DURATION:
                phrase_time = datetime.min  # start a new phrase
                break  # stop if the buffer is too large
        audio_data = sr.AudioData(phrase_buffer, sample_rate, sample_width)

        try:  # transcribe the audio
            yield recognizer(audio_data)
        except sr.UnknownValueError:
            continue  # unrecognized audio
        except sr.RequestError as e:
            logger.error("Transcription failed: %s", e)
            continue  # recognition engine error
        sleep(0)  # important for multithreading


def _record(source: sr.AudioSource = sr.Microphone(sample_rate=16000)):
    """Start recording audio in the background.

    Args:
        source (AudioSource): The audio source to record from.

    Returns:
        Queue: The queue of recorded audio chunks. The chunks are raw audio
        data. The queue is thread-safe.
    """

    recordings: Queue[sr.AudioData] = Queue()
    with source:
        recorder.adjust_for_ambient_noise(source)

    def callback(_, audio: sr.AudioData) -> None:
        recordings.put(audio)

    recorder.listen_in_background(
        source, callback, phrase_time_limit=_RECORD_TIMEOUT
    )
    return recordings
