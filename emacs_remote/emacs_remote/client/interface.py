import argparse
import os
from pathlib import Path

from .. import utils
from ..messages import Request, Response, ShellRequest, ServerTerminateRequest
from ..utils.logging import LoggerFactory
from ..utils.stcp_socket import SecureTCPSocket


class ClientInterface:
    def __init__(self, emacs_remote_path: str, host: str, workspace: str):
        self.host = host
        self.workspace = workspace
        self.workspace_hash = utils.md5((host, workspace))

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        print("Workspace ", self.workspace_path)

        port_file = self.workspace_path.joinpath("daemon.port")
        if not port_file.exists():
            raise FileNotFoundError(
                "Daemon port file not found. Make sure the client daemon is running.\n\n\t"
                f"emacs-remote-client --host {host} --workspace {workspace} daemon"
            )

        self.port = int(port_file.read_text().strip())
        self.socket = SecureTCPSocket()

    def __enter__(self):
        self.socket.__enter__()
        self.socket.connect("localhost", self.port)
        return self

    def __exit__(self, *args):
        self.socket.__exit__(*args)

    @staticmethod
    def add_subparsers(subparsers):
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

    def execute(self, args):
        if args.command == "exit":
            self.socket.sendall(ServerTerminateRequest())
            response = self.socket.recvall()
            raise EOFError("Daemon has been terminated")
        elif args.command == "get":
            self.get(args.filename, args.absolute)

    def prompt(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(
            title="commands",
            description="valid commands",
            dest="command",
            help="Commands",
        )
        ClientInterface.add_subparsers(subparsers)
        try:
            while True:
                cmd = input(">>> ")
                args = parser.parse_args(cmd.split())
                self.execute(args)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
