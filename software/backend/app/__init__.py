"""
The backend application.

It uses FastAPI to provide a REST API for the frontend to use.

Docs: https://fastapi.tiangolo.com/
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

FRONTEND_URL = os.getenv("FRONTEND_URL")
LOGGER = logging.getLogger(__name__)
app_dir = os.path.dirname(os.path.realpath(__file__))
logging_file = os.path.join(os.path.dirname(app_dir), "logs", "backend.log")
debug = os.getenv("DEBUG", "False").lower() == "true"

# logging formats
console_formatter = logging.Formatter(
    r"%(message)s [bright_black]- [italic]%(name)s[/italic] "
    r"\[[underline]%(filename)s:%(lineno)d[/underline]]",
    datefmt=r"%Y-%m-%d %H:%M:%S.%f",
)
file_formatter = logging.Formatter(
    r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
    r"%(message)s - %(name)s [%(filename)s:%(lineno)d]",
    datefmt=r"%Y-%m-%d %H:%M:%S",
)

# setup console logger
console_handler = RichHandler(
    markup=True,
    show_path=False,
    tracebacks_show_locals=debug,
    rich_tracebacks=True,
)
console_handler.setFormatter(console_formatter)

# setup file logger
os.makedirs(os.path.dirname(logging_file), exist_ok=True)
file_handler = RotatingFileHandler(
    logging_file, maxBytes=2**20, backupCount=10
)
file_handler.setFormatter(file_formatter)

# configure logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
root_logger.handlers = [console_handler, file_handler]
logging.captureWarnings(True)
