import speech_recognition as sr

from ...models.microphone import MicrophoneConfig
from ..events import Event
from . import LOGGER
from .engines import RecognitionEngine
from .sources import ByteStreamSource

RECORD_TIMEOUT = 0.5
"""The maximum audio recording chunk size (seconds)."""
ENERGY_THRESHOLD = 1000
"""The energy threshold for recording audio."""
DYNAMIC_ENERGY_THRESHOLD = False
"""Whether to dynamically adjust the energy threshold for recording audio."""


async def start_recorder(
    engine: RecognitionEngine, mic_config: MicrophoneConfig, mic_event: Event
):
    """Start recording audio from a microphone using a speech recognition
    engine.

    Args:
        engine (RecognitionEngine): The speech recognition engine.
        mic_config (MicrophoneConfig): The microphone configuration.
        mic_event (Event): The audio event triggered on new microphone data.

    Returns:
        Tuple[Event[sr.AudioData], CancellationToken]: The recording event and
            the cancellation token.
    """

    # configure the engine's recognizer
    engine.recognizer.energy_threshold = ENERGY_THRESHOLD
    engine.recognizer.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

    source = ByteStreamSource(mic_event, mic_config)
    with source:  # adjust for ambient noise
        LOGGER.error("Adjusting recognizer for ambient noise")
        engine.recognizer.adjust_for_ambient_noise(source)

    # starting recording in the background
    recording_event = Event[sr.AudioData]()
    stopper = engine.recognizer.listen_in_background(
        source,
        recording_event.trigger,
        phrase_time_limit=RECORD_TIMEOUT,
    )
    cancellation_event = Event()
    await cancellation_event.subscribe(stopper)
    return recording_event, cancellation_event
