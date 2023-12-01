"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import asyncio

import speech_recognition as sr
from transcription.core import recorder


async def google_recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio using Google's speech recognition engine.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """

    transcript = await asyncio.to_thread(recorder.recognize_google, audio_data)
    return transcript  # type: ignore


async def whisper_recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio using OpenAI's Whisper speech recognition engine.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """

    transcript = await asyncio.to_thread(
        recorder.recognize_whisper_api, audio_data
    )
    return transcript  # type: ignore
