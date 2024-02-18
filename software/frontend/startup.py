#!/usr/bin/env python3
import logging
import os

frontend_dir = os.path.dirname(os.path.realpath(__file__))


def main(debug=False):
    """Starts the frontend server and sets up logging.

    Args:
        debug (bool): Whether to start in debug mode and log debug messages.
    """

    dotnet = (
        f"dotnet {'watch' if debug else ''} run --project {frontend_dir} "
        f"--configuration {'Debug' if debug else 'Release'}"
    )  # the dotnet command to run the frontend server

    try:  # start server
        os.system(dotnet)
    except Exception as e:
        logging.exception(e)
        exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the frontend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
