#!/usr/bin/env python3
from controller import bluetooth_controller as controller
from robot import motor, servo, speaker
from speech_recognition import


def main():
    controller.start()
    test_motors()
    test_speakers()


def test_motors():
    motor.circle()
    motor.back_and_forth()
    servo.circle()


def test_speakers():
    for sound in speaker.sounds:
        speaker.play(sound)


if __name__ == "__main__":
    main()
