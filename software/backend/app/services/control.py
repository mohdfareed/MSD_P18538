"""Robot control module.

This package contains the robot control code. It provides an interface to
control various robot components, such as the motors.

Documentation: https://gpiozero.readthedocs.io/en/latest/index.html
PIN-OUT: https://gpiozero.readthedocs.io/en/latest/recipes.html#pin-numbering
"""

import logging

LOGGER = logging.getLogger(__name__)
"""Control module logger."""


async def forward(activate: bool):
    """Drive the car forward or stop it.

    Args:
        activate (bool): Whether to drive the car forward.
    """

    if activate:
        LOGGER.debug("Driving forward")
    else:
        LOGGER.debug("Stopping")


async def backward(activate: bool):
    """Drive the car backward or stop it.

    Args:
        activate (bool): Whether to drive the car backward.
    """

    if activate:
        LOGGER.debug("Driving backward")
    else:
        LOGGER.debug("Stopping")


async def left(activate: bool):
    """Turn the car left or stop it.

    Args:
        activate (bool): Whether to turn the car left.
    """

    if activate:
        LOGGER.debug("Turning left")
    else:
        LOGGER.debug("Stopping")


async def right(activate: bool):
    """Turn the car right or stop it.

    Args:
        activate (bool): Whether to turn the car right.
    """

    if activate:
        LOGGER.debug("Turning right")
    else:
        LOGGER.debug("Stopping")
