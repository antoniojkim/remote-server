#!/usr/bin/env python3

import logging
import os
import random
import signal
import socket
import subprocess
import sys
from time import sleep
from pathlib import Path
from threading import Event, Lock
from queue import Queue, Empty as EmptyQueue

import pexpect

from .. import utils
from ..messages import Request, Response, ShellRequest, TerminateRequest
from ..messages.startup import SERVER_STARTUP_MSG
from ..utils.atomic import AtomicInt
from ..utils.stcp import SecureTCP
from ..utils.stcp_socket import SecureTCPSocket
from ..utils.logging import get_level, LoggerFactory


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
        self.workspace_hash = utils.md5(workspace)

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        self.num_clients = num_clients

        self.active_requests = AtomicInt()
        self.requests = Queue()
        self.requests.put(ShellRequest(["ls"]))
        self.requests.put(ShellRequest(["git", "status"]))
        # self.requests.put(TerminateRequest())

        self.server = None
        self.exceptions = Queue()

        self.terminate_queue = Queue()
        self.finish = Event()
        self.daemon_lock = Lock()

        self.logging_level = logging_level
        self.logging_factory = LoggerFactory(
            logging_level, self.workspace_path.joinpath("client.log")
        )
        self.logger = self.logging_factory.get_logger("client.daemon")

    def handle_request(self, request, socket):
        assert isinstance(request, Request)
        socket.sendall(request)
        data = socket.recvall()

        assert isinstance(data, Response)
        print(data)

    def reset_ssh_connection(self):
        if self.server:
            self.server.stop()

        print(f"Establishing ssh connection with {self.host}...")

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
                try:
                    with self.active_requests:
                        request = self.requests.get(timeout=1)
                        self.handle_request(request, socket)
                except EmptyQueue as e:
                    pass

        def check_started(process):
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                # print(line)
                if line == SERVER_STARTUP_MSG:
                    return True

            return False

        self.server = SecureTCP(self.host, self.num_clients, self.logger)
        self.server.start(
            get_cmd,
            check_started,
            client_handler,
        )

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
            except Exception as e:
                self.logger.error(str(e))
            finally:
                daemon_port.unlink()

    def __enter__(self):
        self.reset_ssh_connection()

        print("Client Daemon Initialized!")
        return self

    def __exit__(self, *args):
        self.logger.info("Shutting down Client Daemon")

        with self.daemon_lock:
            self.finish.set()
        self.requests.put(TerminateRequest())

        self.logger.debug("    Waiting for request queue to be flushed")
        while not self.requests.empty() or self.active_requests:
            sleep(1)

        self.logger.debug("    Terminating Client Handlers")
        while not self.terminate_queue.empty():
            terminate_event = self.terminate_queue.get()
            terminate_event.set()

        self.logger.debug("    Stopping server")
        if self.server:
            self.server.stop()

        self.logger.info("Successfully shutdown Client Daemon")
