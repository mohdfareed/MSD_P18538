from dataclasses import dataclass


@dataclass
class Movement:
    """Movement instructions model."""

    speed: float
    angle: float
