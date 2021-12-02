#!/usr/bin/env python3 -u

import argparse
import os
from pathlib import Path

from .daemon import ClientDaemon


def run(args):
    if args.daemon:
        with ClientDaemon(
            args.emacs_remote_path, args.host, args.workspace, logging_level=args.level
        ) as daemon:
            daemon.listen()
    else:
        pass


def main():
    parser = argparse.ArgumentParser(
        "emacs-remote-client",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d", "--daemon", action="store_true", help="Enables daemon mode"
    )
    parser.add_argument(
        "-r",
        "--emacs_remote_path",
        default=os.path.join(Path.home(), ".emacs_remote"),
        help="Path to the emacs-remote working directory",
    )
    parser.add_argument(
        "--host",
        type=str,
        required=True,
        help="Remote host to run on. Host must exist in ~/.ssh/config",
    )
    parser.add_argument(
        "-w",
        "--workspace",
        type=str,
        required=True,
        help="Path to the desired workspace",
    )
    parser.add_argument(
        "-l",
        "--level",
        choices=["info", "debug"],
        default="info",
        help="Logger level",
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()
