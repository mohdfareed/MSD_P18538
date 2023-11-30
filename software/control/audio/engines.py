"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import speech_recognition as sr
from audio.transcription import recorder


def google_recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio using Google's speech recognition engine.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """

    return recorder.recognize_google(audio_data)  # type: ignore


def whisper_recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio using OpenAI's Whisper speech recognition engine.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """

    return recorder.recognize_whisper_api(audio_data)  # type: ignore
