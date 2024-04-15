import os
from dataclasses import dataclass

import pyaudio  # type: ignore


@dataclass
class Config:
    """Configuration model. Contains all configurable settings."""

    transcription_engine: str = "whisper"
    """The transcription engine to use."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    """The OpenAI API key."""

    audio_device: int = int(
        pyaudio.PyAudio().get_default_output_device_info()["index"]
    )
    """The audio device to use."""
