#!/usr/bin/env python3

import logging
import os
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from rich.logging import RichHandler

LOGGER = logging.getLogger(__name__)

backend = os.path.dirname(os.path.realpath(__file__))
logging_dir = os.path.join(backend, "logs")

# logging format
console_formatter = logging.Formatter(
    r"%(message)s [bright_black]- [italic]%(name)s[/italic] "
    r"\[[underline]%(filename)s:%(lineno)d[/underline]]",
    datefmt=r"%Y-%m-%d %H:%M:%S.%3f",
)
file_formatter = logging.Formatter(
    r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
    r"%(message)s - %(name)s [%(filename)s:%(lineno)d]",
    datefmt=r"%Y-%m-%d %H:%M:%S",
)


def main(debug=False):
    """Starts the backend server and sets up logging.

    Args:
        debug (bool): Whether to log debug messages.
        log (bool): Whether to log to a file in addition to the console.
    """
    load_dotenv()
    setup_logging(debug)

    try:  # start server
        uvicorn.run(
            "app.main:app",
            host=os.getenv("HOSTNAME", ""),
            port=int(os.getenv("PORT") or 0),
            reload=debug,
            log_config=None,
        )
    except Exception as e:
        logging.exception(e)
        exit(1)


def setup_logging(debug: bool):
    # configure logging
    logging.captureWarnings(True)
    root_logger = logging.getLogger()
    root_logger.level = logging.DEBUG if debug else logging.INFO

    # setup console logger
    console_handler = RichHandler(
        markup=True,
        show_path=False,
        log_time_format=console_formatter.datefmt,  # type: ignore
        tracebacks_word_wrap=False,
        tracebacks_show_locals=debug,
        rich_tracebacks=True,
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # setup file logger
    os.makedirs(logging_dir, exist_ok=True)
    filename = f"{datetime.now():%y%m%d_%H%M%S}.log"
    file_handler = logging.FileHandler(os.path.join(logging_dir, filename))
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    LOGGER.info(f"Logging to file: {filename}")
    LOGGER.debug("Debug mode enabled") if debug else None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
