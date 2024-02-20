from gpiozero import PhaseEnabledMotor, DigitalOutputDevice

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

# For now very this is a digital signal until we know that pwm can work
motor_speed = DigitalOutputDevice(MOTOR_SPEED, True, False)
motor_forward = DigitalOutputDevice(MOTOR_FORWARD, True, False)
motor_reverse = DigitalOutputDevice(MOTOR_REVERSE, True, False)

def drive(movement: Movement):
    """Drive the car.

    Args:
        movement (Movement): The movement to drive the car with.
    """

    if movement.speed > 0: 
        motor_speed.on()
    else:
        motor_speed.off()

    if movement.direction > 0:
        motor_forward.on()
        motor_reverse.off()
    else:
        motor_forward.off()
        motor_reverse.on()
