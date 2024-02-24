"""
Network module.

Network module manages the network that will be used to control the application.
This will manage the devices configuration in the Adhoc network and internet
router bridge modes. Peer wifi offers net sharing with automatic IP and is intended
to be used in lieu of hosting through another network.
"""

import os

from ... import app_dir

ADHOC_PATH = f"{app_dir}/services/network/adhoc-interface "
ROUTER_PATH = f"{app_dir}/services/network/wifi-interface"


def update_interface(path, verbose=False):
    update_interface = "sudo cp %s /etc/network/interfaces" % path
    status = os.system(update_interface)
    if verbose:
        if not status:
            print("Success, reboot to change the network interface.")
        else:
            print("Interface change has failed, error code:", status)
    return status


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Control Network interface.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-a",
        "--adhoc",
        action="store_true",
        help="Initialize the adhoc hosted network",
    )
    mode_group.add_argument(
        "-r",
        "--router",
        action="store_true",
        help="Initialize the router hosted network",
    )
    args = parser.parse_args()

    if args.adhoc:
        status = update_interface(ADHOC_PATH)
    elif args.router:
        status = update_interface(ROUTER_PATH)
