from time import sleep

from gpiozero import Motor, PWMOutputDevice, Robot

_motor1 = Motor(forward=4, backward=14)
_motor2 = Motor(forward=17, backward=27)

robot = Robot(left=_motor1, right=_motor2)


def circle():
    robot.right()
    sleep(2.5)
    robot.left()
    sleep(2.5)
    robot.stop()


def back_and_forth():
    robot.forward()
    sleep(2.5)
    robot.backward()
    sleep(2.5)
    robot.stop()


# PWM example
pin = PWMOutputDevice(2)
pin.value = 0.25  # 25% duty cycle
pin.frequency = 1000  # 1kHz
