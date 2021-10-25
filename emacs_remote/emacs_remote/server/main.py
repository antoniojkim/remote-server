#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

from .daemon import ServerDaemon


def run(args):
    with ServerDaemon(args.emacs_remote_path, args.workspace, args.ports) as daemon:
        pass


def main():
    parser = argparse.ArgumentParser(
        "emacs-remote-server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--emacs_remote_path",
        default=os.path.join(Path.home(), ".emacs_remote"),
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
    run(parser.parse_args())


if __name__ == "__main__":
    main()
