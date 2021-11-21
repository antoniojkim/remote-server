import logging
import multiprocessing
import os
import socket
import sys
from pathlib import Path
from queue import Queue, Empty as EmptyQueue
from threading import Barrier, Event, Thread
from time import sleep

from .. import utils
from ..messages.startup import SERVER_STARTUP_MSG
from ..utils.stcp_socket import SecureTCPSocket
from ..utils.logging import get_level


class ServerDaemon:
    def __init__(
        self,
        emacs_remote_path: str,
        workspace: str,
        ports: str,
        logging_level: str = "info",
    ):
        """
        Server daemon process that handles remote computation in the background

        Args:
            emacs_remote_path: Path to the emacs remote directory
            workspace: Path to the workspace to monitor
            ports: Ports to listen on
            logging_level: The logging level
        """
        self.workspace = Path(workspace)
        os.chdir(self.workspace.resolve())

        self.ports = ports
        self.logging_level = get_level(logging_level)

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", utils.md5(workspace)
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        self.startup_barrier = Barrier(len(self.ports) + 1)
        self.threads = []
        self.terminate_events = Queue()

    def listen(self, port):
        terminate = Event()
        self.terminate_events.put(terminate)

        logger = logging.getLogger(f"server.{port}")
        logger.setLevel(self.logging_level)

        with SecureTCPSocket() as s:
            try:
                s.bind("localhost", int(port))
                logger.debug(f"Bound socket to localhost:{port}")

                self.startup_barrier.wait()

                s.listen()
                logger.debug(f"Listening on port {port}")

                conn, addr = s.accept()
                logger.debug(f"Connection accepted from {addr}")

                with conn:
                    while not terminate.is_set():
                        data = conn.recvall(timeout=2)
                        if not data:
                            continue

                        print(data, flush=True)
                        conn.sendall("Received")

            except Exception as e:
                logger.error(str(e))

    def __enter__(self):
        for port in self.ports:
            thread = Thread(target=self.listen, args=(port,))
            thread.start()
            self.threads.append(threa)

        self.startup_barrier.wait()
        return self

    def __exit__(self, *args):
        while not self.terminate_events.empty():
            event = self.terminate_events.get()
            event.set()

        for thread in self.threads:
            thread.join()
