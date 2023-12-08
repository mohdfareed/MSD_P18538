from dataclasses import dataclass


@dataclass
class MicrophoneConfig:
    """Microphone configuration model."""

    sample_rate: int
    """The sample rate of the microphone."""
    sample_width: int = 2
    """The sample width of the microphone."""
    chunk_size: int = 1024
    """The chunk size of the microphone."""
