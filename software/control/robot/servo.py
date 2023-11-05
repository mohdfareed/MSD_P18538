from time import sleep

from gpiozero import AngularServo

servo = AngularServo(17, min_angle=-90, max_angle=90)


def circle():
    servo.angle = -90
    sleep(1)
    servo.angle = -45
    sleep(1)
    servo.angle = 0
    sleep(1)
    servo.angle = 45
    sleep(1)
    servo.angle = 90
    sleep(1)
