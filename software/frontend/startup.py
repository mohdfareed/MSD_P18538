#!/usr/bin/env python3

import os

frontend = os.path.dirname(os.path.realpath(__file__))


def main(debug=False):
    """Starts the frontend server and sets up logging.

    Args:
        debug (bool): Whether to start in debug mode and log debug messages.
    """

    os.system(
        (
            f"dotnet {'watch' if debug else ''} run --project {frontend} "
            f"--configuration {'Debug' if debug else 'Release'}"
        )
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start the frontend server.")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="start in debug mode"
    )

    args = parser.parse_args()
    main(args.debug)
