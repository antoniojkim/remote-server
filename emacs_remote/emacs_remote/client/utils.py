import argparse
import os
from pathlib import Path


def get_client_parser():
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
    parser.add_argument(
        "-l",
        "--level",
        choices=["info", "debug"],
        default="info",
        help="Logger level",
    )
    return parser


def add_client_subparsers(subparsers):
    exit_parser = subparsers.add_parser(
        "exit", help="Command to stop daemon and server"
    )

    get_parser = subparsers.add_parser(
        "get", help="Command to get a something from the server"
    )
    get_parser.add_argument("filename", help="Name of the file to get")
    get_parser.add_argument(
        "-a",
        "--absolute",
        action="store_true",
        help="If provided, assume file name is an absolute path, not a relative one",
    )
