from gpiozero import Servo

from . import LOGGER

# servo = Servo(18)
# servo.mid()


def turn(angle: float):
    """Turn the car. Positive angle is right, negative angle is left.

    Args:
        angle (float): The angle to turn the car at. Must be between -1 and 1.
        Zero is straight.
    """
    if abs(angle) > 1:
        LOGGER.error("Invalid angle: %s", angle)
        raise ValueError("Angle must be between -1 and 1")

    # servo.value = angle
