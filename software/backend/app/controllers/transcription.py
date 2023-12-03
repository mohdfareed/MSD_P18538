import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from ..services.transcription import LOGGER
from ..services.transcription import core as transcription
from ..services.transcription import engines as recognition_engines

router = APIRouter()


@router.get("/transcription/", status_code=status.HTTP_200_OK)
async def get_transcription():
    source = transcription.sr.Microphone(sample_rate=16000)
    recognizer = recognition_engines.whisper_recognize

    async def _transcription():
        try:
            async for text in transcription.transcribe(source, recognizer):
                yield text
        except asyncio.CancelledError or GeneratorExit or KeyboardInterrupt:
            LOGGER.debug("Transcription interrupted")

    return StreamingResponse(_transcription())
