from gpiozero import Motor, Servo

from ...models.movement import Movement
from . import LOGGER

MOTOR_LEFT_FORWARD = 17
MOTOR_LEFT_BACKWARD = 27
MOTOR_RIGHT_FORWARD = 4
MOTOR_RIGHT_BACKWARD = 14
SERVO = 18

# servo = Servo(SERVO)
# motor_left = Motor(
#     forward=MOTOR_LEFT_FORWARD, backward=MOTOR_LEFT_BACKWARD, pwm=True
# )
# motor_right = Motor(
#     forward=MOTOR_RIGHT_FORWARD, backward=MOTOR_RIGHT_BACKWARD, pwm=True
# )

# servo.mid()
# motor_left.stop()
# motor_right.stop()


def drive(movement: Movement):
    """Drive the car.

    Args:
        movement (Movement): The movement to drive the car with.
    """

    # servo.value = movement.angle
    if movement.speed > 0:
        motor_left.forward(movement.speed)  # type: ignore
        motor_right.forward(movement.speed)  # type: ignore
    else:
        motor_left.backward(-movement.speed)  # type: ignore
        motor_right.backward(-movement.speed)  # type: ignore
