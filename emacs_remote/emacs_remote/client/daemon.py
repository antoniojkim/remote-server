#!/usr/bin/env python3

import os
import random
import socket
import subprocess
from time import sleep
from pathlib import Path
from threading import Barrier, Event, Thread
from queue import Queue, Empty

import pexpect

from emacs_remote import utils
from emacs_remote.messages.startup import SERVER_STARTUP_MSG


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

        self.num_clients = num_clients

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
        with self.client_path.joinpath("response.txt").open() as f:
            f.write(f"Response: {data.decode('utf-8')}\n")

    def reset_ssh_connection(self):
        print(f"Establishing ssh connection with {self.host}...")

        client_ports = [None for i in range(self.num_clients)]

        def handler(index: int, terminate: Event):
            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #     s.bind(("localhost", 0))
            #     port = str(s.getsockname()[1])

            port = str(random.randint(9130, 40000))
            print(f"Port {index}: {port}")
            client_ports[index] = port

            self.client_barrier.wait()
            self.client_barrier.wait()

            print(f"Connecting to localhost:{port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(("localhost", int(port)))
                print(f"Connected to localhost:{port}")

                # while not terminate.is_set():
                #     try:
                #         request = self.requests.get(timeout=2)
                #         self.handle_request(client, request)
                #     except Empty:
                #         pass

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

        def start_server(timeout):
            server_ports = [str(random.randint(9130, 49151)) for port in client_ports]
            cmd = ["ssh"]
            for client_port, server_port in zip(client_ports, server_ports):
                cmd.extend(["-L", f"{client_port}:localhost:{server_port}"])
            cmd.append(self.host)
            cmd.append(
                "~/.emacs_remote/bin/server.sh "
                f"--workspace {self.workspace} "
                f"--ports {' '.join(server_ports)}"
            )

            print("cmd:", " ".join(cmd))

            self.server = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            for line in self.server.stdout:
                line = line.decode("utf-8").strip()
                print(f">>> {line}")
                if line == SERVER_STARTUP_MSG:
                    break

            if self.server.poll() is None:
                print("ssh connection established!")
                return True

            code = self.server.wait(timeout=timeout)  # wait for server to come up
            print(f"Error {code}.")

            outs, errs = self.server.communicate(timeout=15)
            print(f"{' stdout ':=^50}")
            print(outs.decode("utf-8"))
            print(f"{' stderr ':=^50}")
            print(errs.decode("utf-8"))
            print(f"{'':=^50}")

            return False

        try:
            for i in range(1, 6):
                if start_server(timeout=i * 2 + 1):
                    break

                print(" Retrying ssh connection...")
            else:
                raise RuntimeError("Unable to start server")

        finally:
            self.client_barrier.wait()

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
        for thread, terminate in self.client_threads:
            terminate.set()
            thread.join()

        if self.server:
            self.server.terminate()

            code = self.server.wait()  # wait for server to come up
            print(f"Error {code}.")

            outs, errs = self.server.communicate(timeout=15)
            print(f"{' stdout ':=^50}")
            print(outs.decode("utf-8"))
            print(f"{' stderr ':=^50}")
            print(errs.decode("utf-8"))
            print(f"{'':=^50}")
