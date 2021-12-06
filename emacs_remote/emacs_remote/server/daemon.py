import logging
import multiprocessing
import os
import signal
import socket
import sys
from pathlib import Path
from queue import Queue, Empty as EmptyQueue
from threading import Barrier, Event, Thread
from time import sleep

from .. import utils
from ..messages import Request, ShellResponse
from ..messages.startup import SERVER_STARTUP_MSG
from ..utils.stcp_socket import SecureTCPSocket
from ..utils.logging import LoggerFactory


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

        self.logging_factory = LoggerFactory(
            logging_level, self.workspace_path.joinpath("server.log")
        )
        self.logger = self.logging_factory.get_logger("server.daemon")

        self.startup_barrier = Barrier(len(self.ports) + 1)
        self.threads = []
        self.terminate_events = Queue()
        self.finish = Event()

    def listen(self, port):
        terminate = Event()
        self.terminate_events.put(terminate)

        logger = self.logging_factory.get_logger(f"server.{port}")

        with SecureTCPSocket(logger=logger) as s:
            try:
                s.bind("localhost", int(port))

                self.startup_barrier.wait()

                s.listen()
                conn, addr = s.accept()

                with conn:
                    while not terminate.is_set():
                        try:
                            request = conn.recvall(timeout=2)
                            if not request:
                                break

                            logger.debug(f"Got request with type: {type(request)}")
                            if not isinstance(request, Request):
                                raise TypeError(
                                    f"Expected type Request. Got: {type(request)}"
                                )

                            conn.sendall(request.run(self))
                            logger.debug("Sent response")
                        except TimeoutError:
                            pass

            except Exception as e:
                logger.error(str(e))

    def wait(self):
        while not self.finish.is_set():
            sleep(1)

    def __enter__(self):
        self.logger.info("Starting server threads...")

        for port in self.ports:
            thread = Thread(target=self.listen, args=(port,))
            thread.start()
            self.threads.append(thread)

        self.startup_barrier.wait()
        return self

    def __exit__(self, *args):
        self.logger.debug("Terminating events")
        while not self.terminate_events.empty():
            event = self.terminate_events.get()
            event.set()

        self.logger.debug("Waiting for threads to join")
        for thread in self.threads:
            thread.join()

        self.logger.info("Exiting emacs remote server daemon")
