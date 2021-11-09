#!/usr/bin/env python3

import os
import random
import signal
import socket
import subprocess
import sys
from time import sleep
from pathlib import Path
from threading import Event
from queue import Queue, Empty as EmptyQueue

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

        self.terminate_queue = Queue()

    def handle_request(self, request, socket):
        print("Request:", request)

        socket.sendall(request)
        data = socket.recvall()
        print(f"Response: {data}")

    def reset_ssh_connection(self):
        if self.server:
            self.server.stop()

        print(f"Establishing ssh connection with {self.host}...")

        def get_cmd(client_ports, server_ports):
            cmd = []
            # Add args
            cmd.append(f'WORKSPACE="{self.workspace}"')
            cmd.append(f'PORTS="{" ".join(server_ports)}"')

            script_path = Path(sys.prefix, "emacs_remote_scripts", "server.sh")

            cmd.append("bash -s")
            cmd.append("<")
            cmd.append(str(script_path.resolve()))

            return cmd

        def client_handler(socket):
            terminate_event = Event()
            self.terminate_queue.put(terminate_event)

            while not terminate_event.is_set():
                try:
                    request = self.requests.get(timeout=1)
                    self.handle_request(request, socket)
                except EmptyQueue as e:
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
        while not self.terminate_queue.empty():
            terminate_event = self.terminate_queue.get()
            terminate_event.set()

        if self.server:
            self.server.stop()
