import multiprocessing
import os
import socket
from pathlib import Path
from time import sleep

from .. import utils
from ..messages.startup import SERVER_STARTUP_MSG
from ..utils.stcp_socket import SecureTCPSocket


class ServerDaemon:
    def __init__(self, emacs_remote_path, workspace, ports):
        self.workspace = Path(workspace)
        os.chdir(self.workspace.resolve())

        self.ports = ports

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", utils.md5(workspace)
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        self.startup_barrier = multiprocessing.Barrier(len(self.ports) + 1)
        self.processes = []

    @staticmethod
    def listen(startup_barrier, port):
        with SecureTCPSocket() as s:
            s.bind("localhost", int(port))
            startup_barrier.wait()

            s.listen()
            conn, addr = s.accept()
            print(f"Connection accepted from {addr}", flush=True)

            with conn:
                while True:
                    data = conn.recvall()
                    if not data:
                        break

                    print(data)
                    conn.sendall("Received")

    def __enter__(self):
        for port in self.ports:
            p = multiprocessing.Process(
                target=ServerDaemon.listen, args=(self.startup_barrier, port)
            )
            p.start()
            self.processes.append(p)

        self.startup_barrier.wait()
        return self

    def __exit__(self, *args):
        for p in self.processes:
            p.terminate()
            p.join()
