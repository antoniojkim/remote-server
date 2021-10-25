#!/usr/bin/env python3
import multiprocessing
import socket
from pathlib import Path
from time import sleep


class ServerDaemon:
    def __init__(self, emacs_remote_path, workspace, ports):
        self.workspace = workspace
        self.ports = ports

        self.server_tcps = []

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.server_path = self.emacs_remote_path.joinpath("server")
        self.server_path.mkdir(parents=True, exist_ok=True)

        self.threads = []

    @staticmethod
    def listen(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", int(port)))

            s.listen()
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break

                    print(data.decode("utf-8"))
                    conn.send("Received".encore("utf-8"))

    def __enter__(self):
        with multiprocessing.Pool(len(self.ports)) as p:
            list(p.starmap(ServerDaemon.listen, ((port,) for port in self.ports)))

        return self

    def __exit__(self, *args):
        for server_tcp in self.server_tcps:
            server_tcp.__exit__(*args)
