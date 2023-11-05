#!/usr/bin/env python3
from controller import bluetooth_controller as controller
from robot import motor, servo, speaker

i = 0
while True:
    motor.circle()
    motor.back_and_forth()
    servo.circle()
    controller.start()
    speaker.play(speaker.sounds[i])
    i = (i + 1) % len(speaker.sounds)
