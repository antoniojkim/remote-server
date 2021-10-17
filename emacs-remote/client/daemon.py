#!/usr/bin/env python3

import os
import socket
from pathlib import Path
from threading import Event, Thread
from queue import Queue


class ClientDaemon:
    def __init__(self, emacs_remote_path: str, host: str, workspace: str):
        self.host = host
        self.workspace = workspace

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.client_path = self.emacs_remote_path.joinpath("client")
        self.client_path.mkdir(parents=True, exist_ok=True)

        self.exceptions = Queue()

        self.ssh_thread = None
        self.ssh_terminate = Event()

        self.client_tcps = []
        self.num_client_tcps = 1

    def run_ssh_connection(self, ports):
        while not self.ssh_terminate.is_set() and self.exceptions.empty():
            break

    def listen(self):
        assert self.client_tcp is not None, "Client TCP session is uninitialized"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind("localhost", 0)
            port = s.getsockname()[1]

            self.client_path.joinpath("daemon.port").write_text(str(port))

            try:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)
                pass
            finally:
                self.client_path.joinpath("daemon.port").unlink()

    def __enter__(self):
        ports = []
        for i in range(self.num_client_tcps):
            client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_tcp.__enter__()
            client_tcp.bind(("localhost", 0))
            ports.append(client_tcp.getsockname()[1])
            self.client_tcps.append(client_tcp)

        self.ssh_thread = Thread(target=self.run_ssh_connection, args=(ports))
        self.ssh_thread.start()

    def __exit__(self, *args):
        for client_tcp in self.client_tcps:
            client_tcp.__exit__(*args)

        if self.ssh_thread and isinstance(self.ssh_thread, Thread):
            self.ssh_terminate.set()
            self.ssh_thread.join()
