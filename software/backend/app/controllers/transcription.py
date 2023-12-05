import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from ..services.transcription import LOGGER
from ..services.transcription import core as transcription
from ..services.transcription import engines as recognition_engines

router = APIRouter()
_transcriber = None  # active transcription generator
_cancellation_token = asyncio.Event()


@router.get("/transcription/", status_code=status.HTTP_200_OK)
async def start_transcription():
    global _transcriber
    if _transcriber is not None:
        raise HTTPException(
            status_code=400, detail="Transcription already running"
        )

    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize
    _transcriber = transcription.transcribe(source, recognizer)
    _cancellation_token.clear()

    async def _transcription():
        global _transcriber
        try:
            async for transcript in _transcriber:  # type: ignore
                yield transcript
                if _cancellation_token.is_set():
                    break
        except asyncio.CancelledError or GeneratorExit or KeyboardInterrupt:
            LOGGER.debug("Transcription interrupted")
        finally:
            LOGGER.debug("Transcription stopped")
            _transcriber = None

    return StreamingResponse(_transcription())


@router.delete("/transcription/", status_code=status.HTTP_200_OK)
async def stop_transcription():
    global _transcriber
    if _transcriber is None:
        raise HTTPException(
            status_code=400, detail="Transcription not running"
        )
    _cancellation_token.set()
