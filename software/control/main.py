#!/usr/bin/env python3
import os

from audio.core import record as record_audio
from audio.transcription import PHRASE_TERMINATOR, transcribe

# from controller import bluetooth_controller as controller
# from robot import motor, servo, speaker


def main():
    # controller.start()
    # test_motors()
    # test_speakers()

    record_audio()
    transcriptions = [""]
    for transcript in transcribe():
        if transcript == PHRASE_TERMINATOR:
            transcriptions.append("")  # start new phrase
            continue
        transcriptions[-1] = transcript
        print_transcription(transcriptions)


# def test_motors():
#     motor.circle()
#     motor.back_and_forth()
#     servo.circle()


# def test_speakers():
#     for sound in speaker.sounds:
#         speaker.play(sound)


def print_transcription(transcription: list[str]):
    os.system("cls" if os.name == "nt" else "clear")
    print("Transcription:")
    for line in transcription:
        print(line)
    print("", end="", flush=True)


if __name__ == "__main__":
    main()
