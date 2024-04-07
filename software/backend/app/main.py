from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import LOGGER
from .controllers import audio, configurator, control, transcription

app = FastAPI()
app.include_router(control.router)
app.include_router(transcription.router)
app.include_router(configurator.router)
app.include_router(audio.router)

# setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/health")
async def root():
    LOGGER.info("Health check passed.")
    return {"message": "Backend server running"}
