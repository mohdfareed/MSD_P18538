"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import asyncio

import speech_recognition as sr

from ..configurator import config, register_validator

recognizer = sr.Recognizer()
"""The speech recognition engine."""


async def recognize(audio_data: sr.AudioData) -> str:
    """Recognize audio data.

    Args:
        audio_data (AudioData): The audio to recognize.

    Returns:
        str: The transcription of the audio.
    """
    global recognizer, config, active_engine

    try:
        return await asyncio.to_thread(active_engine, audio_data)
    except sr.UnknownValueError as e:
        raise UnrecognizedAudioError from e
    except sr.RequestError as e:
        raise RecognitionEngineError from e


def _google_recognize(audio_data: sr.AudioData) -> str:
    global recognizer
    return recognizer.recognize_google(audio_data)  # type: ignore


def _whisper_recognize(audio_data: sr.AudioData) -> str:
    global recognizer
    return recognizer.recognize_whisper(audio_data)


class RecognitionEngineError(Exception):
    """An error raised by a recognition engine."""

    ...


class UnrecognizedAudioError(RecognitionEngineError):
    """An error raised when the audio is not recognized."""

    ...


# CONFIGURATION ###############################################################

engines = {
    "google": _google_recognize,
    "whisper": _whisper_recognize,
}


def validate_engine():
    global active_engine
    try:
        active_engine = engines[config.transcription_engine]
    except KeyError:
        raise ValueError(f"Invalid engine: {config.transcription_engine}")


register_validator(validate_engine)
