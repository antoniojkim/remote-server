#!/usr/bin/env python3

import argparse
import logging
import os
from pathlib import Path

from .daemon import ServerDaemon
from ..messages.startup import SERVER_STARTUP_MSG


def run(args):
    print("Ports: ", args.ports, flush=True)

    with ServerDaemon(
        args.emacs_remote_path, args.workspace, args.ports, args.level
    ) as daemon:
        print(SERVER_STARTUP_MSG, flush=True)


def main():
    parser = argparse.ArgumentParser(
        "emacs-remote-server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--emacs_remote_path",
        default=str(Path.home().joinpath(".emacs_remote")),
        help="Path to the emacs-remote working directory",
    )
    parser.add_argument(
        "-w",
        "--workspace",
        type=str,
        required=True,
        help="Path to the desired workspace",
    )
    parser.add_argument(
        "-p",
        "--ports",
        nargs="+",
        required=True,
        help="Ports to listen on",
    )
    parser.add_argument(
        "-l",
        "--level",
        choices=["info", "debug", "verbose"],
        default="info",
        help="Logger level",
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()
