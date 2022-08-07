import argparse
import os
import shlex
from pathlib import Path
from time import sleep

from emacs_remote import utils
from emacs_remote.client.daemon import ClientDaemon
from emacs_remote.client.utils import add_client_subparsers
from emacs_remote.messages import (GetFileRequest, PortRequest, Request,
                                   Response, ServerTerminateRequest,
                                   ShellRequest)
from emacs_remote.utils.logging import LoggerFactory
from emacs_remote.utils.stcp_socket import SecureTCPSocket


class ClientInterface:
    def __init__(
        self, emacs_remote_path: str, host: str, workspace: str, logging_level: str
    ):
        self.workspace = Workspace(host, emacs_remote_path, workspace)

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

        self.logger = self.workspace.logger("client.daemon")

    def __enter__(self):
        self.socket.__enter__()
        self.socket.connect("localhost", self.port)
        return self

    def __exit__(self, *args):
        self.socket.__exit__(*args)

    def send_request(self, request):
        self.socket.sendall(PortRequest())
        response = self.socket.recvall()

        if not isinstance(response, PortResponse):
            self.logger.debug(f"Expected response PortResponse. Got: {type(response)}")
        else:
            port = response.port
            with SecureTCPSocket() as s:
                s.connect("localhost", port)
                s.sendall(request)
                return s.recvall(timeout=300)  # wait up to 5 mins for response

    def execute(self, args):
        if args.command == "exit":
            self.socket.sendall(TerminateRequest())
            response = self.socket.recvall()
            self.logger.info("Client Daemon Succesfully Terminated!")
        elif args.command == "get":
            self.socket.sendall(GetFileRequest(args.filename, args.absolute))
            response = self.socket.recvall()
            if response:
                if isinstance(response, Response):
                    raise TypeError(f"Expected response type. Got: {type(response)}")

                response.run(self)

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
