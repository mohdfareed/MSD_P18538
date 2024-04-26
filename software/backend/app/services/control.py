"""Robot control module.

This package contains the robot control code. It provides an interface to
control various robot components, such as the motors.

Documentation: https://gpiozero.readthedocs.io/en/latest/index.html
PIN-OUT: https://gpiozero.readthedocs.io/en/latest/recipes.html#pin-numbering
"""

import logging
import platform

LOGGER = logging.getLogger(__name__)
"""Control module logger."""

FORWARD_PIN = 9
"""Forward pin number."""
BACKWARD_PIN = 10
"""Backward pin number."""
LEFT_PIN = 13
"""Left pin number."""
RIGHT_PIN = 19
"""Right pin number."""
SIREN_PIN = 11

forward_motor = None
"""Forward motor."""
backward_motor = None
"""Backward motor."""
left_motor = None
"""Left motor."""
right_motor = None
"""Right motor."""
siren = None
"""Siren"""



if platform.system() == "Linux":
    import gpiozero  # type: ignore

    forward_motor = gpiozero.OutputDevice(FORWARD_PIN)  # type: ignore
    backward_motor = gpiozero.OutputDevice(BACKWARD_PIN)  # type: ignore
    left_motor = gpiozero.OutputDevice(LEFT_PIN)  # type: ignore
    right_motor = gpiozero.OutputDevice(RIGHT_PIN)  # type: ignore
    siren = gpiozero.OutputDevice(SIREN_PIN) # type: ignore


async def forward(activate: bool):
    """Drive the car forward or stop it.

    Args:
        activate (bool): Whether to drive the car forward.
    """

    if activate:
        if forward_motor:
            forward_motor.on()
        LOGGER.debug("Driving forward")
    else:
        if forward_motor:
            forward_motor.off()
        LOGGER.debug("Stopping")


async def backward(activate: bool):
    """Drive the car backward or stop it.

    Args:
        activate (bool): Whether to drive the car backward.
    """

    if activate:
        if backward_motor:
            backward_motor.on()
        LOGGER.debug("Driving backward")
    else:
        if backward_motor:
            backward_motor.off()
        LOGGER.debug("Stopping")


async def left(activate: bool):
    """Turn the car left or stop it.

    Args:
        activate (bool): Whether to turn the car left.
    """

    if activate:
        if left_motor:
            left_motor.on()
        LOGGER.debug("Turning left")
    else:
        if left_motor:
            left_motor.off()
        LOGGER.debug("Stopping")


async def right(activate: bool):
    """Turn the car right or stop it.

    Args:
        activate (bool): Whether to turn the car right.
    """

    if activate:
        if right_motor:
            right_motor.on()
        LOGGER.debug("Turning right")
    else:
        if right_motor:
            right_motor.off()
        LOGGER.debug("Stopping")
        
async def siren (active: bool):
    """Turn on the siren or stop it 
    
    Args:
        activate (bool): Whether to turn the siren on.
    """
    
    if active: 
        if siren:
            siren.on()
        LOGGER.debug("Turning on Siren")
    else:
        if siren:
            siren.off()
        LOGGER.debug("Turning off Siren")
