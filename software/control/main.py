#!/usr/bin/env python3
import os

from audio import core as audio

# from controller import bluetooth_controller as controller
# from robot import motor, servo, speaker


def main():
    # controller.start()
    # test_motors()
    # test_speakers()

    audio.startup()
    audio.record()

    transcriptions = [""]
    phrase_complete = False
    for transcript in audio.transcribe(audio.recordings):
        if transcript == "":
            continue
        if transcript == "\n":
            phrase_complete = True
            continue

        if phrase_complete:
            transcriptions.append(transcript)
            phrase_complete = False
        else:
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
