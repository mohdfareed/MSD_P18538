import logging

from fastapi import FastAPI

from .routers import control, transcription

LOGGER = logging.getLogger(__name__)

app = FastAPI()
app.include_router(control.router)
app.include_router(transcription.router)


@app.get("/")
async def root():
    return {"message": "Running"}
