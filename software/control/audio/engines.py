"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import speech_recognition as sr
from audio.core import recorder


def google_recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio using Google's speech recognition engine.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """

    return recorder.recognize_google(audio_data)  # type: ignore
