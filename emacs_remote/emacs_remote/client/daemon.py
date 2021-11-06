#!/usr/bin/env python3

import os
import random
import signal
import socket
import subprocess
from time import sleep
from pathlib import Path
from threading import Event
from queue import Queue, Empty

import pexpect

from .. import utils
from ..messages.startup import SERVER_STARTUP_MSG
from ..utils.stcp import SecureTCP


class ClientDaemon:
    def __init__(
        self, emacs_remote_path: str, host: str, workspace: str, num_clients: int = 1
    ):
        self.host = host
        self.workspace = workspace
        self.workspace_hash = utils.md5(workspace)

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        self.num_clients = num_clients

        self.requests = Queue()
        self.requests.put("ls")

        self.server = None
        self.exceptions = Queue()

    def handle_request(self, session, request):
        print("Request:", request)

        session.send(request.encode("utf-8"))
        data = session.recv(1024)
        with self.client_path.joinpath("response.txt").open() as f:
            f.write(f"Response: {data.decode('utf-8')}\n")

    def reset_ssh_connection(self):
        print(f"Establishing ssh connection with {self.host}...")

        def get_cmd(client_ports, server_ports):
            return [
                "~/.emacs_remote/bin/server.sh ",
                f"--workspace {self.workspace} ",
                f"--ports {' '.join(server_ports)}",
            ]

        def client_handler(socker):
            pass

        def check_started(process):
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                if line == SERVER_STARTUP_MSG:
                    return True

            return False

        self.server = SecureTCP(self.host, self.num_clients)
        self.server.start(
            get_cmd,
            check_started,
            client_handler,
        )

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            port = s.getsockname()[1]

            daemon_port = self.workspace_path.joinpath("daemon.port")
            daemon_port.write_text(str(port))

            try:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)
            finally:
                daemon_port.unlink()

    def __enter__(self):
        self.reset_ssh_connection()

        print("Client Daemon Initialized!")
        return self

    def __exit__(self, *args):
        if self.server:
            self.server.stop()
