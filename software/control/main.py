#!/usr/bin/env python3
from robot import motor, servo

while True:
    motor.circle()
    motor.back_and_forth()
    servo.circle()
