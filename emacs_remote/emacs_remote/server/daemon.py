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

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", utils.md5(workspace)
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        self.logging_level = get_level(logging_level)
        self.file_handler = logging.FileHandler(
            self.workspace_path.joinpath("server.log"), mode="w"
        )
        self.file_handler.setLevel(self.logging_level)
        logging.basicConfig(
            level=self.logging_level,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
        )

        self.startup_barrier = Barrier(len(self.ports) + 1)
        self.threads = []
        self.terminate_events = Queue()

    def listen(self, port):
        terminate = Event()
        self.terminate_events.put(terminate)

        logger = logging.getLogger(f"server.{port}")
        logger.setLevel(self.logging_level)
        logger.addHandler(self.file_handler)

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
                        logger.debug("Receiving data")
                        data = conn.recvall(timeout=2)
                        if not data:
                            continue

                        logger.debug(f"Received data: {data}")
                        conn.sendall("Received")
                        logger.debug("Sent response")

            except Exception as e:
                logger.error(str(e))

    def wait(self):
        # Wait indefinitely
        event = Event()
        event.wait()

    def __enter__(self):
        for port in self.ports:
            thread = Thread(target=self.listen, args=(port,))
            thread.start()
            self.threads.append(thread)

        self.startup_barrier.wait()
        return self

    def __exit__(self, *args):
        logger = logging.getLogger(f"server.{port}")
        logger.setLevel(self.logging_level)
        logger.addHandler(self.file_handler)

        logger.debug("Terminating events")
        while not self.terminate_events.empty():
            event = self.terminate_events.get()
            event.set()

        logger.debug("Waiting for threads to join")
        for thread in self.threads:
            thread.join()

        logger.debug("Exiting emacs remote server daemon")
