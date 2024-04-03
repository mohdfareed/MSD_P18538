#!/usr/bin/env python3

import logging
import os
import platform
import subprocess

import uvicorn
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)
HOST = "0.0.0.0"
PORT = 9600
CERTIFICATE_NAME = "MSD_P18538"

backend = os.path.dirname(os.path.realpath(__file__))
cert_path = os.path.join(backend, "data", "cert.pem")
key_path = os.path.join(backend, "data", "key.pem")


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
        LOGGER.debug("Backend server stopped")
        logging.shutdown()


def setup_environment(debug):
    load_dotenv()
    os.environ["DEBUG"] = str(debug)
    os.environ["NOLOG"] = str(1)  # don't log on import
    import app

    os.unsetenv("NOLOG")
    LOGGER.info(f"Logging to files at: {os.path.dirname(app.logging_file)}/")
    LOGGER.debug("Debug mode enabled")


def setup_https():
    """Set up HTTPS certificates for the server."""
    need_generate = False

    # check if certificates exist
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        LOGGER.warning("No HTTPS certificates found. Generating new ones")
        need_generate = True
    else:  # check if certificates are expired
        result = subprocess.run(
            ["openssl", "x509", "-checkend", "0", "-noout", "-in", cert_path],
            capture_output=True,
        )
        if result.returncode != 0:  # certificate expired
            LOGGER.warning("HTTPS certificates expired. Generating new ones")
            need_generate = True
    if not need_generate:
        return

    # remove old trusted certificates by common name
    if platform.system() == "Darwin":  # macOS
        # find the certificate by its Common Name and get its SHA-1 hash
        find_cert_cmd = [
            "security",
            "find-certificate",
            "-c",
            CERTIFICATE_NAME,
            "-a",
            "-Z",
        ]
        result = subprocess.run(
            find_cert_cmd, capture_output=True, text=True, check=True
        )
        # extract SHA-1 hashes from the command output
        hashes = [
            line.split(": ")[1]
            for line in result.stdout.split("\n")
            if line.startswith("SHA-1 hash")
        ]
        # delete certificates by their SHA-1 hash
        for hash_value in hashes:
            delete_cert_cmd = [
                "sudo",
                "security",
                "delete-certificate",
                "-Z",
                hash_value,
            ]
            subprocess.run(delete_cert_cmd, capture_output=True, check=True)
            LOGGER.info(
                f"Successfully deleted certificate with SHA-1 hash: {hash_value}"
            )
    elif platform.system() == "Linux":  # Linux
        # remove all certificates from the trusted store
        remove_cert_cmd = [
            "sudo",
            "rm",
            "-f",
            "/usr/local/share/ca-certificates/*",
        ]
        subprocess.run(remove_cert_cmd, capture_output=True, check=True)
    LOGGER.info("Removed old trusted certificates")

    # generate new certificates
    cmd = [
        "openssl",
        "req",
        "-new",
        "-x509",
        "-keyout",
        key_path,
        "-out",
        cert_path,
        "-days",
        "365",
        "-nodes",
        "-subj",
        f"/C=US/ST=NY/L=Rochester/O=RIT/CN={CERTIFICATE_NAME}",
    ]
    result = subprocess.run(cmd, capture_output=True, check=True)
    LOGGER.info("Generated new HTTPS certificates")

    # trust the certificates
    if platform.system() == "Darwin":  # macOS
        trust_cmd = ["sudo", "security", "add-trusted-cert", cert_path]
        subprocess.run(trust_cmd, capture_output=True, check=True)
        LOGGER.info("Certificate trusted successfully")
    elif platform.system() == "Linux":  # Linux
        trust_cmd = [
            "sudo",
            "cp",
            cert_path,
            "/usr/local/share/ca-certificates/",
        ]
        subprocess.run(trust_cmd, capture_output=True, check=True)
        subprocess.run(
            ["sudo", "update-ca-certificates"], capture_output=True, check=True
        )
        LOGGER.info("Certificate trusted successfully")
    else:
        LOGGER.warning("Cannot trust certificate automatically on this system")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the backend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
