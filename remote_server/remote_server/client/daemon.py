import argparse
import logging
import os
import random
import signal
import socket
import subprocess
import sys
from pathlib import Path
from queue import Empty as EmptyQueue
from queue import Queue
from threading import Event, Lock, Thread
from time import sleep

from emacs_remote import utils
from emacs_remote.client.utils import get_client_parser
from emacs_remote.messages import (Request, Response, ServerTerminateRequest,
                                   ShellRequest)
from emacs_remote.messages.startup import SERVER_STARTUP_MSG
from emacs_remote.utils.atomic import AtomicInt
from emacs_remote.utils.stcp import SecureTCP
from emacs_remote.utils.stcp_socket import SecureTCPSocket
from emacs_remote.workspace import Workspace


class ClientDaemon:
    def __init__(
        self,
        emacs_remote_path: str,
        host: str,
        workspace: str,
        num_clients: int = 1,
        logging_level: str = "info",
    ):
        self.workspace = Workspace(host, emacs_remote_path, workspace, logging_level)

        self.session = None
        self.server = None

        self.finished = Event()
        self.daemon_lock = Lock()

        self.logger = self.workspace.logger("client.daemon")

    def stcp_session(self):
        while True:
            self.logger.info(f"Establishing ssh connection with {self.host}...")

        def get_cmd(session):
            cmd = []
            # Add args
            cmd.append(f'WORKSPACE="{self.workspace}"')
            cmd.append(f'PORTS="{" ".join(session.server_ports)}"')
            cmd.append(f'LEVEL="{self.workspace, logging_level}"')

            script_path = Path(sys.prefix, "emacs_remote_scripts", "server.sh")

            cmd.append("bash -s")
            cmd.append("<")
            cmd.append(str(script_path.resolve()))

            return cmd

        def check_started(session):
            port = session.next_client_port()
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                self.logger.debug(line)

                if line == SERVER_STARTUP_MSG:
                    return True

            return False

        self.server = SecureTCP(self.workspace, self.num_clients)
        self.server.start(get_cmd, check_started)

        self.logger.info("Client Daemon Initialized!")

        self.finished.wait()

        self.logger.info("Shutting down Client Daemon")

        self.requests.put(ServerTerminateRequest())

        self.logger.debug("    Waiting for request queue to be flushed")
        while not self.requests.empty():
            self.logger.debug("    Request queue is not empty")
            sleep(1)

        self.logger.debug("    Terminating Client Handlers")
        while not self.terminate_queue.empty():
            terminate_event = self.terminate_queue.get()
            terminate_event.set()

        while self.active_requests:
            self.logger.debug("    Number of active requests is > 0")
            sleep(1)

        self.logger.debug("    Stopping server")
        if server:
            server.stop()

        self.logger.info("Successfully shutdown Client Daemon")

    def start(self):
        self.session = Thread(target=self.stcp_session)
        self.session.daemon = True
        self.session.start()

    def stop(self):
        with self.daemon_lock:
            self.finish.set()

        if self.session:
            self.session.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def listen(self):
        with SecureTCPSocket(logger=self.logger) as s:
            s.bind("localhost", 0)
            port = s.getsockname()[1]
            self.logger.debug(f"Daemon bound socket to localhost:{port}")

            daemon_port = self.workspace_path.joinpath("daemon.port")
            daemon_port.write_text(str(port))

            s.listen()
            self.logger.debug(f"Listening on port {port}")

            while not self.finished.is_set():
                try:
                    conn, addr = s.accept()
                    self.logger.debug(f"Connection accepted from {addr}")

                    with conn:
                        request = conn.recvall(timeout=5)
                        if not request:
                            continue

                        if not isinstance(request, Request):
                            self.logger.debug(
                                f"Expected type Request. Got: {type(request)}"
                            )

                        response = request.run(self)

                        if not isinstance(response, Response):
                            self.logger.debug(
                                f"Expected type Response. Got: {type(response)}"
                            )

                        conn.sendall(response)
                finally:
                    daemon_port.unlink()

            self.logger.debug("Finish Client Daemon")

    @staticmethod
    def start_new_session(emacs_remote_path, host, workspace, logging_level):
        daemon_script = Path(__file__).resolve()
        p = subprocess.Popen(
            [
                sys.executable,
                daemon_script,
                "--emacs_remote_path",
                emacs_remote_path,
                "--host",
                host,
                "--workspace",
                workspace,
                "--level",
                logging_level,
            ],
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


def main(args):
    with ClientDaemon(
        emacs_remote_path=args.emacs_remote_path,
        host=args.host,
        workspace=args.workspace,
        logging_level=args.level,
    ) as daemon:
        daemon.listen()


if __name__ == "__main__":
    main(get_client_parser().parse_args())
