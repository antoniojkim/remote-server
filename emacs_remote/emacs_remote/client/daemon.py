#!/usr/bin/env python3

import os
import socket
import random
import subprocess
from time import sleep
from pathlib import Path
from threading import Barrier, Event, Thread
from queue import Queue, Empty


class ClientDaemon:
    def __init__(self, emacs_remote_path: str, host: str, workspace: str):
        self.host = host
        self.workspace = workspace

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.client_path = self.emacs_remote_path.joinpath("client")
        self.client_path.mkdir(parents=True, exist_ok=True)

        self.num_clients = 1

        self.client_barrier = Barrier(self.num_clients + 1)
        self.client_threads = []
        self.requests = Queue()

        self.requests.put("ls")

        self.server = None

        self.exceptions = Queue()

    def handle_request(self, session, request):
        print("Request:", request)

        session.send(request.encode("utf-8"))
        data = session.recv(1024)
        print("Response:", data.decode("utf-8"))

    def reset_ssh_connection(self):
        print(f"Establishing ssh connection with {self.host}...")

        client_ports = [None for i in range(self.num_clients)]

        def handler(index: int, terminate: Event):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", 0))
                port = str(s.getsockname()[1])

                print(f"Port {i}: {port}")
                client_ports[index] = port
                self.client_barrier.wait()
                self.client_barrier.wait()

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.connect(("localhost", int(port)))

                    while not terminate.is_set():
                        try:
                            request = self.requests.get(timeout=2)
                            self.handle_request(client, request)
                        except Empty:
                            pass

        for thread, terminate in self.client_threads:
            terminate.set()
            thread.join()

        self.client_threads.clear()
        for i in range(self.num_clients):
            terminate = Event()
            thread = Thread(target=handler, args=(i, terminate))
            thread.start()
            self.client_threads.append((thread, terminate))

        self.client_barrier.wait()
        assert all(port is not None for port in client_ports)

        if self.server:
            self.server.terminate()

        try:
            for i in range(1, 6):
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

                self.server = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                try:
                    code = self.server.wait(timeout=i + 1)  # wait for server to come up

                    outs, errs = self.server.communicate(timeout=15)
                    print(outs.decode("utf-8"))
                    print(errs.decode("utf-8"))
                    print(f"Error {code}. Retrying ssh connection...")
                    if i < 5:
                        sleep(5 * i)

                except subprocess.TimeoutExpired:  # means server started up
                    print("ssh connection established!")
                    break
            else:
                raise RuntimeError("Unable to start server")

        finally:
            self.client_barrier.wait()

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
        self.reset_ssh_connection()

        print("Client Daemon Initialized!")
        return self

    def __exit__(self, *args):
        for thread, terminate in self.client_threads:
            terminate.set()
            thread.join()

        if self.server:
            self.server.terminate()
