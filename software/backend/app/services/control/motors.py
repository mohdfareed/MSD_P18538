from gpiozero import Motor, Servo

from ...models.movement import Movement
from . import LOGGER

# These pins could be a good choice for this purpose
# GPIO  -> PIN
# 0 -> 27 note: might be reserved
# 5 -> 29
# 6 -> 31
# 13 -> 33, also PWM1
# 19 -> 35, also PWM1
# 26 -> 37 


# For now we are going to test without PWM, not sure for now the switching speed for the ICs 
MOTOR_SPEED = 6 # High is fast, and low is slow. Not sure if this matters for for reverse..
MOTOR_FORWARD = 13
MOTOR_REVERSE = 19 
STEERING_MOTOR = 18 # Should be noted that this not a servo, but rather just another 

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
