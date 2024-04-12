import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration model. Contains all configurable settings."""

    transcription_engine: str = "whisper"
    """The transcription engine to use."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    """The OpenAI API key."""
