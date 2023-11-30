#!/usr/bin/env python3
import os
import threading

from audio import engines as recognition_engines
from audio import transcription
from controller import bluetooth_controller as controller
from robot import motor, servo, speaker


def main():
    # controller.start()
    test_transcription()
    # test_motors()
    # test_speakers()

    # wait for the user to exit
    input("Press anything to exit.\n")
    exit(0)


def test_motors():
    motor.circle()
    motor.back_and_forth()
    servo.circle()


def test_speakers():
    for sound in speaker.sounds:
        speaker.play(sound)


def test_transcription():
    # source = transcription.sr.Microphone(sample_rate=16000)
    source = transcription.sr.AudioFile("demo.wav")
    recognizer = recognition_engines.whisper_recognize

    # function to display transcriptions
    def print_transcription(transcription: str):
        # clear line and print transcription
        print(" " * os.get_terminal_size().columns, end="\r", flush=True)
        print(transcription, end="\r", flush=True)

    def transcribe():  # transcribe audio from a source in real-time
        print("Listening...")
        for transcript in transcription.transcribe(source, recognizer):
            if transcript == transcription.PHRASE_TERMINATOR:
                continue
            print_transcription(transcript)

    # start transcribing in the background
    threading.Thread(target=transcribe, daemon=True).start()


if __name__ == "__main__":
    main()
