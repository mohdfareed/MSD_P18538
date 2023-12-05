import pygame

from . import LOGGER

# initialize Pygame Mixer
pygame.mixer.init()
# list of sound files
sounds = []


def play(sound: str):
    """Plays a sound file.

    Args:
        sound (str): The filepath.
    """

    try:
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
    except pygame.error:
        LOGGER.error("Could not play sound file: %s", sound)
