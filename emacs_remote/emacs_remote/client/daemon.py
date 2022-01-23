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
from emacs_remote.utils.logging import LoggerFactory
from emacs_remote.utils.stcp import SecureTCP
from emacs_remote.utils.stcp_socket import SecureTCPSocket


class ClientDaemon:
    def __init__(
        self,
        emacs_remote_path: str,
        host: str,
        workspace: str,
        num_clients: int = 1,
        logging_level: str = "info",
    ):
        self.host = host
        self.workspace = workspace
        self.workspace_hash = utils.md5((host, workspace))

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        print("Workspace ", self.workspace_path)

        self.num_clients = num_clients

        self.active_requests = AtomicInt()
        self.requests = Queue()

        self.session = None
        self.exceptions = Queue()

        self.terminate_queue = Queue()
        self.finish = Event()
        self.daemon_lock = Lock()

        self.logging_level = logging_level
        self.logging_factory = LoggerFactory(
            logging_level, self.workspace_path.joinpath("client_daemon.log")
        )
        self.logger = self.logging_factory.get_logger("client.daemon")

    def stcp_session(self):
        self.logger.info(f"Establishing ssh connection with {self.host}...")

        def get_cmd(client_ports, server_ports):
            cmd = []
            # Add args
            cmd.append(f'WORKSPACE="{self.workspace}"')
            cmd.append(f'PORTS="{" ".join(server_ports)}"')
            cmd.append(f'LEVEL="{self.logging_level}"')

            script_path = Path(sys.prefix, "emacs_remote_scripts", "server.sh")

            cmd.append("bash -s")
            cmd.append("<")
            cmd.append(str(script_path.resolve()))

            return cmd

        def client_handler(index, socket):
            terminate_event = Event()
            self.terminate_queue.put(terminate_event)

            logger = self.logging_factory.get_logger(f"client.{index}")
            socket.set_logger(logger)

            while not terminate_event.is_set():
                with self.active_requests:
                    try:
                        request = self.requests.get(timeout=1)

                        assert isinstance(request, Request)
                        assert server, "Failed to send. Server has died..."
                        socket.sendall(request)

                        assert server, "Failed to receive. Server has died..."
                        response = socket.recvall()

                        assert isinstance(response, Response)
                        self.logger.info(response)
                    except EmptyQueue as e:
                        pass

        def check_started(process):
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                self.logger.debug(line)

                if line == SERVER_STARTUP_MSG:
                    return True

            return False

        server = SecureTCP(self.host, self.num_clients, self.logger)
        server.start(
            get_cmd,
            check_started,
            client_handler,
        )

        self.logger.info("Client Daemon Initialized!")

        self.finish.wait()

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
            try:
                s.bind("localhost", 0)
                port = s.getsockname()[1]
                self.logger.debug(f"Daemon bound socket to localhost:{port}")

                daemon_port = self.workspace_path.joinpath("daemon.port")
                daemon_port.write_text(str(port))

                s.listen()
                self.logger.debug(f"Listening on port {port}")

                while True:
                    with self.daemon_lock:
                        if self.finish.is_set():
                            break

                    conn, addr = s.accept()
                    self.logger.debug(f"Connection accepted from {addr}")

                    with conn:
                        data = conn.recvall(timeout=5)
                        if not data:
                            continue

                        if not isinstance(data, Request):
                            self.logger.debug(
                                f"Expected type Request. Got: {type(data)}"
                            )

                        conn.sendall(data.run(self))

                self.logger.debug("Finish Client Daemon")
            except KeyboardInterrupt:  # Properly exit on interrupt
                pass
            except Exception as e:
                self.logger.error(str(e))
            finally:
                daemon_port.unlink()

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
