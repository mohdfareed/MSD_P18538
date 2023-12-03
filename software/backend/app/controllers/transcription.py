import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from ..services.transcription import LOGGER
from ..services.transcription import core as transcription
from ..services.transcription import engines as recognition_engines

router = APIRouter()
_running = False  # whether transcription is running
# REVIEW: should there only be a single transcription instance?


@router.get("/transcription/", status_code=status.HTTP_200_OK)
async def get_transcription():
    global _running

    if not _running:
        _running = True
        return StreamingResponse(_transcription())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcription already running",
        )


@router.delete("/transcription/", status_code=status.HTTP_200_OK)
async def stop_transcription():
    global _running

    if _running:
        _running = False
        return {"detail": "Transcription stopped"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcription not running",
        )


async def _transcription():
    global _running

    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize

    try:
        async for transcript in transcription.transcribe(source, recognizer):
            if not _running:
                break
            yield transcript
    except asyncio.CancelledError or GeneratorExit or KeyboardInterrupt:
        LOGGER.warning("Transcription interrupted")
    finally:
        LOGGER.info("Transcription stopped")
        _running = False
