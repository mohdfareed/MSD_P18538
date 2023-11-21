from queue import Queue  # thread-safe queue

import speech_recognition as sr

# globals
recordings: Queue[bytes] = Queue()
"""The queue of recorded audio chunks."""
recorder: sr.Recognizer = sr.Recognizer()
"""The speech recognition engine."""
source: sr.Microphone = sr.Microphone(sample_rate=16000)
"""The audio source."""


_record_timeout = 0.5  # the maximum recording chunk size (seconds)

# configure the recorder
recorder.energy_threshold = 1000
recorder.dynamic_energy_threshold = False


def record():
    """Start recording audio in the background."""

    def callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        recordings.put(data)

    with source:
        recorder.adjust_for_ambient_noise(source)

    recorder.listen_in_background(
        source, callback, phrase_time_limit=_record_timeout
    )
