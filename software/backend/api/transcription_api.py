import asyncio
import json

from flask import Blueprint
from flask_executor import Executor
from transcription import core as transcription
from transcription import engines as recognition_engines

api = Blueprint("transcription_api", __name__)
executor: Executor = None  # type: ignore

_cancel_event = asyncio.Event()  # event to cancel transcription
_cancel_event.set()  # transcription is not running


@api.route("", methods=["POST"])
async def transcribe():
    global _cancel_event

    if _cancel_event.is_set():
        _cancel_event.clear()
        executor.submit(_start_transcription)
        return json.dumps({"message": "Transcription started"}), 200
    else:
        return json.dumps({"message": "Transcription already running"}), 400


@api.route("", methods=["DELETE"])
def stop():
    global _cancel_event

    if not _cancel_event.is_set():
        _cancel_event.set()
        return json.dumps({"message": "Transcription stopped"}), 200
    else:
        return json.dumps({"message": "Transcription not running"}), 400


async def _start_transcription():
    global _cancel_event

    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize
    print("Transcript:")

    try:
        async for transcript in transcription.transcribe(
            source, recognizer, _cancel_event
        ):
            if transcript == transcription.PHRASE_TERMINATOR:
                print()  # start a new line for a new phrase
            # clear line and print transcription
            print(transcript, end="\r", flush=True)
    except GeneratorExit:
        print("\nTranscription stopped")
    except asyncio.CancelledError:
        print("\nTranscription stopped")
    finally:
        _cancel_event.set()
