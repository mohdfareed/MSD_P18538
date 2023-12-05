from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import FRONTEND_URL, LOGGER
from .controllers import control, transcription

app = FastAPI()
app.include_router(control.router)
app.include_router(transcription.router)

# setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL or "*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
async def root():
    LOGGER.warning("Running")
    LOGGER.error("Running")
    return {"message": "Running"}
