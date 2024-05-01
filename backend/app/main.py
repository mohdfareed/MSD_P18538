import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import FRONTEND
from .controllers import audio, configurator, control, transcription

api_app = FastAPI(title="backend")
api_app.include_router(control.router)
api_app.include_router(transcription.router)
api_app.include_router(configurator.router)
api_app.include_router(audio.router)

app = FastAPI()
app.mount("/api", api_app, name="api")
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")


@app.exception_handler(404)
async def custom_404_handler(_, __):
    return FileResponse(os.path.join(FRONTEND, "index.html"))


# setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
