import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from ..services.transcription import LOGGER
from ..services.transcription import core as transcription
from ..services.transcription import engines as recognition_engines

router = APIRouter()
_running = False  # whether transcription is running
# TODO: review whether a single transcription instance is enough


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
    try:  # start transcription
        async for transcript in transcription.transcribe(source, recognizer):
            yield transcript
            if not _running:
                break
    except asyncio.CancelledError or GeneratorExit or KeyboardInterrupt:
        LOGGER.info("Transcription interrupted")
    finally:  # cleanup
        LOGGER.debug("Transcription stopped")
        _running = False
