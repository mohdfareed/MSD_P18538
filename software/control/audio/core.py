import io
from datetime import datetime, timedelta
from queue import Queue  # thread-safe queue
from tempfile import NamedTemporaryFile  # os-level temporary file
from time import sleep

import speech_recognition as sr

# global variables
recordings = Queue()
"""The queue of recorded audio chunks."""
recorder = sr.Recognizer()
"""The speech recognition engine."""
source = sr.Microphone()  # default machine microphone
"""The audio source."""

# configure the recorder
record_timeout = 2
"""The maximum recording chunk size (seconds)."""
phrase_timeout = 3
"""The time between recordings before a new phrase is started (seconds)."""

# configure the microphone
recorder.energy_threshold = 10
recorder.dynamic_energy_threshold = False


def transcribe(recordings=recordings, recognize=recorder.recognize_google):
    """
    Transcribe audio in a recording queue using a recognition engine.

    Args:
        recordings (Queue): The queue of recorded audio chunks.
        recognize (AudioData -> str): The recognition engine. Defaults to Google.

    Yields:
        str: The transcription of the audio. Phrases are separated by empty
        lines (newlines). Unrecognized audio is represented by empty strings.
    """
    temp_file = NamedTemporaryFile().name  # temporary file to write audio to
    phrase_time = None  # the last time new audio data was received
    last_sample = bytes()  # current raw audio bytes

    while True:
        sleep(0.25)  # important for multithreading
        if recordings.empty():
            pass  # wait for new audio data

        # process the audio data
        phrase_complete, phrase_time = _check_for_phrase(phrase_time)
        if phrase_complete:  # clear working audio buffer
            last_sample = bytes()
        audio_data = _process_recording(last_sample, temp_file)

        try:  # transcribe the audio
            text = recognize(audio_data).strip()
        except sr.UnknownValueError or sr.RequestError:
            text = ""  # unrecognized audio or recognition engine error

        if phrase_complete:
            yield "\n"  # yield an newline to indicate a pause between phrases
        yield text  # yield the transcript of the audio


def startup():
    """Perform any necessary setup before recording."""
    with source:
        recorder.adjust_for_ambient_noise(source)


def record():
    """Start recording audio in the background."""
    recorder.listen_in_background(
        source, _record_callback, phrase_time_limit=record_timeout
    )


def _record_callback(_, audio: sr.AudioData) -> None:
    """Threaded callback function to receive audio data when recording."""

    data = audio.get_raw_data()
    recordings.put(data)


def _check_for_phrase(phrase_time):
    """Check if a phrase has been completed.

    Args:
        phrase_time (_type_): The last time new audio data was received

    Returns:
        bool: Whether a phrase has been completed
        _type_: The last time new audio data was received
    """

    phrase_complete = False  # start a new phrase
    now = datetime.utcnow()

    # complete phrase if enough time has passed since the last recording
    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
        phrase_complete = True

    # update the last time new audio data was received
    phrase_time = now
    return phrase_complete, phrase_time


def _process_recording(last_sample, temp_file):
    """Process the audio data in the recording queue.

    Args:
        last_sample (bytes): The current audio data
        temp_file (str): The temporary file to write the audio data to

    Returns:
        AudioData: The audio data
    """

    # concatenate current audio data with the latest audio data
    while not recordings.empty():
        data = recordings.get()
        last_sample += data

    # convert the raw data to wav data
    audio_data = sr.AudioData(
        last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH
    )
    wav_data = io.BytesIO(audio_data.get_wav_data())

    # write wav data to the temporary file
    with open(temp_file, "w+b") as f:
        f.write(wav_data.read())
    return audio_data
