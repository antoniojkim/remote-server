#!/usr/bin/env python3 -u

import argparse
import os
from pathlib import Path
from threading import Thread

from .daemon import ClientDaemon
from .interface import ClientInterface


def run(args):
    if args.command == "daemon":
        with ClientDaemon(
            emacs_remote_path=args.emacs_remote_path,
            host=args.host,
            workspace=args.workspace,
            logging_level=args.level,
        ) as daemon:
            daemon.listen()
    else:
        with ClientInterface(
            emacs_remote_path=args.emacs_remote_path,
            host=args.host,
            workspace=args.workspace,
        ) as client:
            if args.command == "prompt":
                client.prompt()
            else:
                client.execute(args)


def main():
    parser = argparse.ArgumentParser(
        "emacs-remote-client",
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
        "--host",
        type=str,
        required=True,
        help="Remote host to run on. Host must exist in ~/.ssh/config",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        description="valid commands",
        dest="command",
        help="Commands",
    )

    # Parser arguments required to start the daemon
    daemon_parser = subparsers.add_parser("daemon", help="Starts the daemon")
    daemon_parser.add_argument(
        "-l",
        "--level",
        choices=["info", "debug"],
        default="info",
        help="Logger level",
    )

    prompt_parser = subparsers.add_parser(
        "prompt", help="Command to prompt input from stdin"
    )

    ClientInterface.add_subparsers(subparsers)

    # Parse the args and run
    run(parser.parse_args())


if __name__ == "__main__":
    main()
