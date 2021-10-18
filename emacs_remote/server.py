#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

from server.daemon import ServerDaemon


def main(args):
    with ServerDaemon(args.emacs_remote_path, args.workspace, args.ports) as daemon:
        daemon.listen()


if __name__ == "__main__":
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
    main(parser.parse_args())
