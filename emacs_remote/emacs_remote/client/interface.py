import argparse
import os
import shlex
from pathlib import Path
from time import sleep

from emacs_remote import utils
from emacs_remote.client.daemon import ClientDaemon
from emacs_remote.client.utils import add_client_subparsers
from emacs_remote.messages import (Request, Response, ServerTerminateRequest,
                                   ShellRequest)
from emacs_remote.utils.logging import LoggerFactory
from emacs_remote.utils.stcp_socket import SecureTCPSocket


class ClientInterface:
    def __init__(
        self, emacs_remote_path: str, host: str, workspace: str, logging_level: str
    ):
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
            ClientDaemon.start_new_session(
                emacs_remote_path, host, workspace, logging_level
            )

            for i in range(20):
                if port_file.exists():
                    break
                sleep(0.5)
            else:
                raise FileNotFoundError(
                    "Daemon port file not found. Make sure the client daemon is running.\n\n\t"
                    f"emacs-remote-client --host {host} --workspace {workspace} daemon"
                )

        self.port = int(port_file.read_text().strip())
        self.socket = SecureTCPSocket()

        self.logging_level = logging_level
        self.logging_factory = LoggerFactory(
            logging_level, self.workspace_path.joinpath("client_interface.log")
        )
        self.logger = self.logging_factory.get_logger("client.daemon")

    def __enter__(self):
        self.socket.__enter__()
        self.socket.connect("localhost", self.port)
        return self

    def __exit__(self, *args):
        self.socket.__exit__(*args)

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
        add_client_subparsers(subparsers)
        try:
            while True:
                cmd = input(">>> ")
                args = parser.parse_args(shlex.split(cmd))
                self.execute(args)
        except EOFError:
            pass
        except KeyboardInterrupt:
            pass
