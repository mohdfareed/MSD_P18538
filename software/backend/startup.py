#!../../.venv/bin/python3

import logging
import os
import subprocess
import threading
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

LOGGER = logging.getLogger(__name__)
HOST = "0.0.0.0"
PORT = 443
CERTIFICATE_PORT = 9600
ROOT_CA_DIR = (  # root CA path
    subprocess.check_output("mkcert -CAROOT", shell=True).decode().strip()
)

# project paths
backend = os.path.dirname(os.path.realpath(__file__))
frontend = os.path.join(os.path.dirname(backend), "frontend")

# certificate paths
cert_path = os.path.join(backend, "data", "certificate.pem")
key_path = os.path.join(backend, "data", "private.key")
root_ca = os.path.join(ROOT_CA_DIR, "rootCA.pem")


def main(debug=False):
    """Starts the backend server and sets up logging.

    Args:
        debug (bool): Whether to start in debug mode and log debug messages.
    """
    setup_environment(debug)

    # build frontend
    subprocess.run(
        f"dotnet publish -c Release {frontend}",
        shell=True,
        check=True,
        capture_output=True,
    )
    LOGGER.info("Frontend built")

    # start certificate server
    cert_thread = threading.Thread(target=start_cert_server)
    cert_thread.start()

    try:  # start server
        uvicorn.run(
            "app.main:app",
            host=HOST,
            port=PORT,
            ssl_certfile=cert_path,
            ssl_keyfile=key_path,
            reload=debug,
            log_config=None,
        )
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception(e)
        os._exit(1)
    finally:
        print()
        LOGGER.debug("Backend server stopped")
        logging.shutdown()
        os._exit(0)


def setup_environment(debug):
    """Set up the environment and logging."""

    frontend_build = os.path.join(
        frontend, "bin", "Release", "net6.0", "publish", "wwwroot"
    )

    load_dotenv()
    os.environ["FRONTEND"] = frontend_build
    os.environ["DEBUG"] = str(debug)
    os.environ["NOLOG"] = str(1)  # don't log on import
    import app  # pylint: disable=import-outside-toplevel

    os.unsetenv("NOLOG")
    LOGGER.info("Logging to files at: %s/", os.path.dirname(app.logging_file))
    LOGGER.debug("Debug mode enabled")


def start_cert_server():
    """Start the certificate server."""

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        LOGGER.info("Certificate server started")
        yield
        LOGGER.debug("Certificate server stopped")

    cert_app = FastAPI(lifespan=lifespan)
    cert_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    @cert_app.get("/")
    async def root():
        LOGGER.info("Serving certificate")
        return FileResponse(
            root_ca,
            media_type="application/x-pem-file",
            filename="root_ca.pem",
        )

    @cert_app.get("/health")
    async def health():
        LOGGER.info("Health check passed.")
        return {"message": "Certificate server running"}

    try:
        uvicorn.run(  # start server
            cert_app, host=HOST, port=CERTIFICATE_PORT, log_config=None
        )
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception(e)
        LOGGER.error("Certificate server failed to start")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
