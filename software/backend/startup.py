#!/usr/bin/env python3

import logging
import os
import sys
from datetime import datetime

import uvicorn
from dotenv import load_dotenv
from rich import print
from rich.logging import RichHandler

HOST = "localhost"
PORT = 8000

DEBUG_LEVEL = logging.DEBUG
LOGGING_LEVEL = logging.INFO
DEFAULT_LEVEL = logging.WARNING

BACKEND = os.path.dirname(os.path.realpath(__file__))
LOGGING_MODULES = ["backend"]
LOGGING_PATH = os.path.join(BACKEND, "logs")
LOGGER = logging.getLogger(__name__)


def main(debug=False):
    """Starts the backend server and sets up logging.

    Args:
        debug (bool): Whether to log debug messages.
        log (bool): Whether to log to a file in addition to the console.
    """
    setup_env()
    setup_logging(debug)

    try:  # import backend and start server
        print("[bold green]Starting backend...[/]")
        uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=debug)
    except Exception as e:
        logging.exception(e)
        exit(1)
    print("\n[bold green]backend stopped[/]")


def setup_env():
    load_dotenv()  # load environment variables from .env file
    os.chdir(os.path.dirname(BACKEND))
    sys.path.append(os.getcwd())
    import backend


def setup_logging(debug: bool):
    # configure logging
    logging.captureWarnings(True)
    root_logger = logging.getLogger()
    root_logger.level = DEFAULT_LEVEL  # default level of all loggers

    # set up logging level for logging modules
    level = DEBUG_LEVEL if debug else LOGGING_LEVEL
    for module in LOGGING_MODULES:
        logging.getLogger(module).setLevel(level)
    LOGGER.setLevel(level)  # set up logging level for this module

    # setup console and file loggers
    configure_console_logging(root_logger, debug)
    configure_file_logging(root_logger)
    LOGGER.debug("Debug mode enabled") if debug else None


def configure_console_logging(logger: logging.Logger, debug: bool):
    format = (
        r"%(message)s [bright_black]- [italic]%(name)s[/italic] "
        r"\[[underline]%(filename)s:%(lineno)d[/underline]]"
    )

    # create console handler
    console_handler = RichHandler(
        markup=True,
        show_path=False,  # use custom path
        log_time_format="[%Y-%m-%d %H:%M:%S]",
        rich_tracebacks=True,
        # show locals only in debug mode
        tracebacks_show_locals=debug,
    )
    formatter = logging.Formatter(format)

    # setup handler
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def configure_file_logging(logger: logging.Logger):
    format = (
        "[%(asctime)s] %(levelname)-8s "
        "%(message)s - %(name)s [%(filename)s:%(lineno)d]"
    )

    # create file handler
    logging_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "logs"
    )
    os.makedirs(logging_dir, exist_ok=True)
    filename = f"{datetime.now():%y%m%d_%H%M%S}.log"
    file = os.path.join(logging_dir, filename)
    file_handler = logging.FileHandler(file)
    formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S")

    # setup handler
    logger.addHandler(file_handler)
    file_handler.setFormatter(formatter)
    logger.info(f"Logging to file: {file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
