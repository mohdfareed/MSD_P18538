"""
Configurator service. This service is responsible for configuring the
application. It uses a simple JSON file to store the configuration. The
configuration file is loaded when the application starts and saved whenever
the configuration changes. The configuration file is located in the backend
directory and is called `config.json`.
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict
from typing import Callable

from .. import data_dir
from ..models.config import Config

LOGGER = logging.getLogger(__name__)
"""Configurator logger."""

config: Config
"""The configuration settings."""
config_file = os.path.join(data_dir, "config.json")
"""The configuration file path."""
validators: list[Callable[[Config], None]] = []
"""The configuration validators. Called when a setting is changed."""

_config_lock = asyncio.Lock()  # lock for accessing the configuration


async def set_config(new_config: Config) -> dict:
    """Update the active configuration.

    Args:
        new_config (Config): The new configuration.

    Returns:
        dict: The updated configuration settings.
    """
    global config

    prev_config = config  # backup the previous configuration
    LOGGER.debug(f"Updating config from {prev_config} to {new_config}")

    # validate the new configuration
    async with _config_lock:
        config = new_config  # update the configuration
        for validator in validators:
            try:  # run all validators
                validator(new_config)
            except Exception as e:
                LOGGER.exception(f"Error validating config: {e}")
                config = prev_config  # restore the previous configuration
                raise ValidationError from e  # raise the error

        return asdict(_store_config(config))


async def get_config() -> dict:
    """Get the active configuration.

    Returns:
        dict: The configuration settings.
    """
    global config

    # wait for the lock (therefore config) to be available
    async with _config_lock:
        return asdict(config)


def register_validator(validator: Callable[[Config], None]):
    """Register a configuration validator that is called when any setting is
    changed.

    Args:
        validator (Callable): The validator function.
    """

    validator(config)  # run the validator on the active configuration
    validators.append(validator)


def _load_config(config_file: str) -> Config:
    config = Config()
    try:
        with open(config_file, "r") as file:
            config = Config(**json.load(file))
    except FileNotFoundError:
        LOGGER.warning("Configuration file not found. Creating new file")
        _store_config(config)
    except Exception as e:
        LOGGER.exception(f"Error loading configuration: {e}")
        LOGGER.warning("Using default configuration")
    finally:
        LOGGER.debug(f"Configuration loaded: {config}")
        return config


def _store_config(config: Config) -> Config:
    try:
        with open(config_file, "w") as file:
            json.dump(asdict(config), file, indent=4)
        return config
    except Exception as e:
        LOGGER.exception(f"Error storing configuration: {e}")
        return config
    finally:
        LOGGER.debug(f"Configuration changed: {config}")


class ValidationError(Exception):
    """A configuration validation error."""

    ...


LOGGER.debug(f"Configuration file: {config_file}")
config = _load_config(config_file)
