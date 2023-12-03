#!/usr/bin/env python3

import logging
import os

import uvicorn
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)


def main(debug=False):
    """Starts the backend server and sets up logging.

    Args:
        debug (bool): Whether to log debug messages.
        log (bool): Whether to log to a file in addition to the console.
    """

    load_dotenv()
    os.environ["DEBUG"] = str(debug)
    setup_logging(debug)

    try:  # start server
        uvicorn.run(  # TODO: check other uvicorn options
            "app.main:app",
            host=os.getenv("HOST", ""),
            port=int(os.getenv("PORT") or 0),
            reload=debug,
            log_config=None,
        )
    except Exception as e:
        logging.exception(e)
        exit(1)


def setup_logging(debug):
    import app

    LOGGER.info(f"Logging to files at: {os.path.dirname(app.logging_file)}/")
    LOGGER.debug("Debug mode enabled") if debug else None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
