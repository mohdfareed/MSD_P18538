from dataclasses import dataclass


@dataclass
class MicrophoneConfig:
    """Microphone configuration model."""

    sample_rate: int
    """The sample rate of the microphone."""
    sample_width: int
    """The sample width of the microphone, in bytes."""
    num_channels: int = 1
    """The number of channels of the microphone."""
    chunk_size: int = 1024
    """The chunk size of the microphone."""
