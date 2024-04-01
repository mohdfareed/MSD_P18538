"""
Speech recognition service.

This service is responsible for speech recognition. It uses the
SpeechRecognition library to recognize speech from audio sources. It provides
interfaces that allow for real-time speech recognition.

The service consists of 3 main components:

- The recorder: This component is responsible for recording audio from an audio
  source. It uses the SpeechRecognition library apply filters to the audio,
  which can be extended.
- The engine: This component is responsible for converting audio data to text.
  It also holds the Recognizer object from the SpeechRecognition library.
- The transcription: This component is responsible for transcribing the audio
  data progressively, as it is received from the recorder.

The service heavily relies on the events service. It uses the events service to
listen to an audio source, filter it using the recording then transmitting the
data to the transcription process, and then broadcasting the transcription to
the rest of the application.

SpeechRecognition docs:
https://github.com/Uberi/speech_recognition#readme
The following discussions were used to implement real-time speech recognition:
https://github.com/openai/whisper/discussions/608
https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py
"""

import logging

LOGGER = logging.getLogger(__name__)
"""Audio module logger."""

from .core import event, start
