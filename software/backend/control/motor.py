from gpiozero import Motor

from . import LOGGER

# motor_left = Motor(forward=4, backward=14, pwm=True)
# motor_right = Motor(forward=17, backward=27, pwm=True)

# motor_left.stop()
# motor_right.stop()


def move(speed: float):
    """Move the car. Positive speed is forward, negative speed is backward.

    Args:
        speed (float): The speed to move the car at. Must be between -1 and 1.
        Zero stops the car.
    """

    if abs(speed) > 1:
        LOGGER.error("Invalid speed: %s", speed)
        raise ValueError("Speed must be between -1 and 1")

    if speed > 0:
        motor_left.forward(speed)  # type: ignore
        motor_right.forward(speed)  # type: ignore
    else:
        motor_left.backward(-speed)  # type: ignore
        motor_right.backward(-speed)  # type: ignore
