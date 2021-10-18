#!/usr/bin/env python3

import argparse
import os
from pathlib import Path

from client.daemon import ClientDaemon


def main(args):
    if args.daemon:
        with ClientDaemon(args.emacs_remote_path, args.host, args.workspace) as daemon:
            daemon.listen()
    else:
        pass


if __name__ == "__main__":
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
    main(parser.parse_args())
