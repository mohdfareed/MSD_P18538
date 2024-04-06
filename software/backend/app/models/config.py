from dataclasses import dataclass


@dataclass
class Config:
    """Configuration model. Contains all configurable settings."""

    transcription_engine: str = "whisper"
    """The transcription engine to use."""
    BluetoothOn: bool = false
    """Bluetooth control is enabled"""
    AdhocOn: bool = false
    """If self hosted network is enabled"""
