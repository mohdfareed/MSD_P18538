import asyncio

from fastapi import APIRouter, HTTPException, status

from ..services.transcription import core as transcription
from ..services.transcription import engines as recognition_engines

router = APIRouter()

_transcriber = None  # the transcription generator


@router.post("/transcription/", status_code=status.HTTP_200_OK)
async def transcribe():
    global _transcriber

    if not _transcriber:
        _transcriber = asyncio.create_task(_start_transcription())
        return {"message": "Transcription started"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcription already running",
        )


@router.delete("/transcription/", status_code=status.HTTP_200_OK)
async def stop():
    global _transcriber

    if _transcriber:
        _transcriber.cancel()
        return {"message": "Transcription stopped"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcription not running",
        )


async def _start_transcription():
    global _transcriber

    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize

    try:
        async for transcript in transcription.transcribe(source, recognizer):
            if transcript == transcription.PHRASE_TERMINATOR:
                print()  # start a new line for a new phrase
            # clear line and print transcription
            print(transcript, end="\r", flush=True)
    except asyncio.CancelledError:
        print("\nTranscription stopped")
    finally:
        _transcriber = None
