"""
Audio service.

This service is responsible for audio capture and playback. It also contains
any audio processing logic.

Usage: The desired audio source is initialized by creating the appropriate
microphone service. The microphone is then passed to the audio player service,
which starts listening to the microphone and broadcasting the audio data to
subscribed speakers.
"""

import logging

import pyaudio

LOGGER = logging.getLogger(__name__)
"""Audio service logger."""
