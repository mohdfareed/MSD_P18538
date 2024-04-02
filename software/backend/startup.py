#!/usr/bin/env python3

import logging
import os

import uvicorn
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)
HOST = "localhost"
PORT = 9600


def main(debug=False):
    """Starts the backend server and sets up logging.

    Args:
        debug (bool): Whether to start in debug mode and log debug messages.
    """

    setup_environment(debug)
    try:  # start server
        uvicorn.run(  # TODO: check available uvicorn options
            "app.main:app",
            host=HOST,
            port=PORT,
            reload=debug,
            log_config=None,
        )
    except Exception as e:
        LOGGER.exception(e)
        exit(1)
    finally:
        LOGGER.debug("Backend server stopped.")
        logging.shutdown()


def setup_environment(debug):
    load_dotenv()
    os.environ["DEBUG"] = str(debug)
    os.environ["NOLOG"] = str(1)  # don't log on import
    import app

    os.unsetenv("NOLOG")
    LOGGER.info(f"Logging to files at: {os.path.dirname(app.logging_file)}/")
    LOGGER.debug("Debug mode enabled")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
