#!/usr/bin/env python3

import os
import socket
import random
import subprocess
from time import sleep
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

        self.threads = []

        self.client_tcps = []
        self.num_client_tcps = 1

    def run_ssh_connection(self, client_ports):
        terminate_event = Event()

        def target():
            retries = 0

            while not terminate_event.is_set() and self.exceptions.empty():
                server_ports = [
                    str(random.randint(9130, 65535)) for port in client_ports
                ]
                cmd = ["ssh"]
                for client_port, server_port in zip(client_ports, server_ports):
                    cmd.extend(["-L", f"{client_port}:localhost:{server_port}"])
                cmd.append(self.host)
                cmd.append(
                    "~/.emacs_remote/bin/server.sh "
                    f"--workspace {self.workspace} "
                    f"--ports {' '.join(server_ports)}"
                )

                server = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                while True:
                    sleep(2)
                    code = server.poll()
                    if code is None:
                        if terminate_event.is_set():
                            return
                        retries = 0
                    elif code != 0:
                        if retries >= 5:
                            return
                        retries += 1
                        break

        thread = Thread(target=target)
        thread.start()

        self.threads.append((thread, terminate_event))

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            port = s.getsockname()[1]

            daemon_port = self.client_path.joinpath("daemon.port")
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
        ports = []
        for i in range(self.num_client_tcps):
            client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_tcp.__enter__()
            client_tcp.bind(("localhost", 0))
            ports.append(str(client_tcp.getsockname()[1]))
            self.client_tcps.append(client_tcp)

        self.run_ssh_connection(ports)

        return self

    def __exit__(self, *args):
        for client_tcp in self.client_tcps:
            client_tcp.__exit__(*args)

        for thread, terminate_event in self.threads:
            terminate_event.set()
            thread.join()
