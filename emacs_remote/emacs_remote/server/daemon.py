#!/usr/bin/env python3

from pathlib import Path
from time import sleep


class ServerDaemon:
    def __init__(self, emacs_remote_path, workspace, ports):
        self.workspace = workspace
        self.ports = ports

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.server_path = self.emacs_remote_path.joinpath("server")
        self.server_path.mkdir(parents=True, exist_ok=True)

    def listen(self):
        sleep(100)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
