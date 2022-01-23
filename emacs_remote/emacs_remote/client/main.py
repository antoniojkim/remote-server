#!/usr/bin/env python3 -u

import os
from pathlib import Path
from threading import Thread

from emacs_remote.client.daemon import ClientDaemon
from emacs_remote.client.interface import ClientInterface
from emacs_remote.client.utils import add_client_subparsers, get_client_parser


def run(args):
    with ClientInterface(
        emacs_remote_path=args.emacs_remote_path,
        host=args.host,
        workspace=args.workspace,
        logging_level=args.level,
    ) as client:
        if args.command == "prompt":
            client.prompt()
        else:
            client.execute(args)


def main():
    parser = get_client_parser()

    subparsers = parser.add_subparsers(
        title="commands",
        description="valid commands",
        dest="command",
        help="Commands",
    )

    prompt_parser = subparsers.add_parser(
        "prompt", help="Command to prompt input from stdin"
    )

    add_client_subparsers(subparsers)

    # Parse the args and run
    run(parser.parse_args())


if __name__ == "__main__":
    main()
