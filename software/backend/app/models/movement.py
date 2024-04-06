from dataclasses import dataclass


@dataclass
class Movement:
    """Movement instructions model."""

    direction: str
    enabled: bool
