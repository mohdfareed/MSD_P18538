"""
Speech recognition module.

This module is responsible for speech recognition. It uses the SpeechRecognition
library to recognize speech from the microphone. It provides an interface that
can be extended to support different speech recognition engines.

SpeechRecognition docs:
https://github.com/Uberi/speech_recognition#readme

The following discussions were used to implement real-time speech recognition:
https://github.com/openai/whisper/discussions/608
https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py
"""

import logging

LOGGER = logging.getLogger(__name__)
"""Audio module logger."""
