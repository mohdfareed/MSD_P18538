"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import asyncio
import os
from collections.abc import Callable

import openai
import openai.error
import speech_recognition as sr  # type: ignore

from ...models.config import Config
from ..configurator import config, register_validator

OPENAI_API_KEY = ""
"""The OpenAI API key."""
recognizer = sr.Recognizer()
"""The speech recognition engine."""
active_engine: Callable[[sr.AudioData], str]
"""The active recognition engine."""


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
    except Exception as e:
        raise RecognitionEngineError from e


def _google_recognize(audio_data: sr.AudioData) -> str:
    global recognizer
    return recognizer.recognize_google(audio_data)  # type: ignore


def _whisper_recognize(audio_data: sr.AudioData) -> str:
    global recognizer
    return recognizer.recognize_whisper_api(audio_data)  # type: ignore


class RecognitionEngineError(Exception):
    """An error raised by a recognition engine."""

    ...


class UnrecognizedAudioError(RecognitionEngineError):
    """An error raised when the audio is not recognized."""

    ...


# CONFIGURATION ###############################################################


def validate_engine(config: Config):
    global active_engine
    engines = {
        "google": _google_recognize,
        "whisper": _whisper_recognize,
    }

    try:
        active_engine = engines[config.transcription_engine]
    except KeyError:
        raise ValueError(f"Invalid engine: {config.transcription_engine}")


def validate_api_key(config: Config):
    global OPENAI_API_KEY, recognizer
    os.environ["OPENAI_API_KEY"] = config.openai_api_key

    try:
        openai.Model.list()
    except openai.error.AuthenticationError as e:
        raise ValueError("Invalid OpenAI API key") from e


register_validator(validate_engine)
register_validator(validate_api_key)
