"""
Speech recognition engines.

This module provides an interface for speech recognition engines. It defines
methods for converting audio data to text.
"""

import asyncio
from abc import ABC, abstractmethod

import speech_recognition as sr


class RecognitionEngine(ABC):
    """A speech recognition engine.

    Provides an interface for converting audio date to text. It holds a speech
    recognition engine from the SpeechRecognition library as the underlying
    engine for speech recognition."""

    def __init__(self, recognizer: sr.Recognizer = sr.Recognizer()):
        self.recognizer = recognizer
        """The speech recognition engine."""

    async def recognize(self, audio_data: sr.AudioData) -> str:
        """Recognize audio data.

        Args:
            audio_data (AudioData): The audio to recognize.

        Returns:
            str: The transcription of the audio.
        """
        try:
            return await asyncio.to_thread(
                self.recognition_function, audio_data
            )
        except sr.UnknownValueError as e:
            raise UnrecognizedAudioError from e
        except sr.RequestError as e:
            raise RecognitionEngineError from e

    @abstractmethod
    def recognition_function(self, audio_data: sr.AudioData) -> str:
        """The speech recognition function."""
        ...


class GoogleEngine(RecognitionEngine):
    """A speech recognition engine that uses Google's speech recognition
    engine."""

    def recognition_function(self, audio_data: sr.AudioData) -> str:
        return self.recognizer.recognize_google(audio_data)  # type: ignore


class WhisperEngine(RecognitionEngine):
    """A speech recognition engine that uses OpenAI's Whisper speech
    recognition engine."""

    def __init__(self, recognizer: sr.Recognizer = sr.Recognizer()):
        # TODO: add API key check
        super().__init__(recognizer)

    def recognition_function(self, audio_data: sr.AudioData) -> str:
        return self.recognizer.recognize_whisper(audio_data)


class RecognitionEngineError(Exception):
    """An error raised by a recognition engine."""

    ...


class UnrecognizedAudioError(RecognitionEngineError):
    """An error raised when the audio is not recognized."""

    ...
