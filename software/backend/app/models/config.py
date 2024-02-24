from dataclasses import dataclass


@dataclass
class Config:
    """Configuration model. Contains all configurable settings."""

    transcription_engine: str = "whisper"
    """The transcription engine to use."""
