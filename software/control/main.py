#!/usr/bin/env python3
import threading

from audio import engines as recognition_engines
from audio import transcription
from controller import bluetooth_controller as controller
from robot import motor, servo, speaker


def main():
    controller.start()
    test_motors()
    test_speakers()
    test_transcription()

    try:  # wait for the user to exit
        while True:
            pass
    except KeyboardInterrupt:
        print("\nExiting...")
    exit(0)


def test_motors():
    motor.circle()
    motor.back_and_forth()
    servo.circle()


def test_speakers():
    for sound in speaker.sounds:
        print("Playing sound: " + sound)
        speaker.play(sound)


def test_transcription():
    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize

    def transcribe():  # transcribe audio from a source in real-time
        print("Transcript:")
        for transcript in transcription.transcribe(source, recognizer):
            if transcript == transcription.PHRASE_TERMINATOR:
                print()  # start a new line for a new phrase
            # clear line and print transcription
            print(transcript, end="\r", flush=True)

    # start transcribing in the background
    threading.Thread(target=transcribe, daemon=True).start()


if __name__ == "__main__":
    main()
