#!/usr/bin/env python3

import os

frontend = os.path.dirname(os.path.realpath(__file__))


def main():
    """Starts the frontend server and sets up logging."""

    cmd = f"dotnet watch run --project {frontend} --configuration Debug"
    os.system(cmd)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Start the frontend server in debug mode."
    )
    args = parser.parse_args()
    main()
