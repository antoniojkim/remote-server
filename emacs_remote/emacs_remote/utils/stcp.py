import random
import signal
import socket
import subprocess
import time
from queue import Queue
from threading import Barrier, Event, Thread
from typing import Callable

from .stcp_socket import SecureTCPSocket


class SecureTCP:
    """
    Handles creating secure TCP connections with the host

    Args:
        host: the host to connect to
            Note, the host must be able to used verbatim as `ssh {host}`
        num_clients: the number of TCP connections to establish
    """

    def __init__(self, host: str, num_clients: int = 1, logger=None):
        self.host = host
        self.num_clients = num_clients

        self.client_threads = []
        self.barrier = Barrier(self.num_clients + 1)

        self.process = None
        self.process_started = Event()

        self.exception_queue = Queue()

        self.logger = logger

    def start(
        self, cmd_closure: Callable, start_closure: Callable, client_handler: Callable
    ):
        client_ports = [None for i in range(self.num_clients)]

        def client(index: int):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("localhost", 0))
                port = str(s.getsockname()[1])

                client_ports[index] = port

            self.barrier.wait()
            self.barrier.wait()

            if not self.process_started.is_set():
                # failed to establish connection
                return

            time.sleep(1)

            self.logger.debug(f"Connecting to localhost:{port}...")
            with SecureTCPSocket() as s:
                s.connect("localhost", int(port))
                self.logger.debug(f"Connected to localhost:{port}")

                client_handler(index, s)

        for thread in self.client_threads:
            thread.join()

        self.client_threads.clear()
        for i in range(self.num_clients):
            thread = Thread(target=client, args=(i,))
            thread.daemon = True
            thread.start()
            self.client_threads.append(thread)

        self.barrier.wait()
        assert all(port is not None for port in client_ports)

        def start_server(timeout):
            server_ports = []
            while len(server_ports) < len(client_ports):
                port = str(random.randint(9130, 49151))
                if port not in client_ports:
                    server_ports.append(port)

            cmd = ["ssh"]
            for client_port, server_port in zip(client_ports, server_ports):
                cmd.extend(["-L", f"{client_port}:localhost:{server_port}"])
            cmd.append(self.host)
            cmd.extend(cmd_closure(client_ports, server_ports))

            self.logger.info(f"cmd: {' '.join(cmd)}")

            self.process_started.clear()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if not start_closure(self.process):
                code = self.process.wait(timeout=timeout)  # wait for server to come up
                self.logger.info(f"Error {code}.")

                outs, errs = self.process.communicate(timeout=15)
                self.logger.debug(f"{' stdout ':=^50}")
                self.logger.debug(outs.decode("utf-8"))
                self.logger.debug(f"{' stderr ':=^50}")
                self.logger.debug(errs.decode("utf-8"))
                self.logger.debug(f"{'':=^50}")

                return False

            self.process_started.set()
            return True

        try:
            for i in range(1, 6):
                if start_server(timeout=i * 2 + 1):
                    self.logger.info("ssh connection established!")
                    break

                self.logger.info(" Retrying ssh connection...")
            else:
                raise RuntimeError("Unable to start server")

        finally:
            self.barrier.wait()

    def stop(self):
        for thread in self.client_threads:
            thread.join()

        if self.process:
            self.process.send_signal(signal.SIGINT)
            # self.process.terminate()
            code = self.process.wait(timeout=10)

            if code != 0:
                self.logger.info(f"Failed to stop server. Error code {code}")

                outs, errs = self.process.communicate(timeout=15)
                self.logger.debug(f"{' stdout ':=^50}")
                self.logger.debug(outs.decode("utf-8"))
                self.logger.debug(f"{' stderr ':=^50}")
                self.logger.debug(errs.decode("utf-8"))
                self.logger.debug(f"{'':=^50}")
            else:
                self.logger.info("Successfully cleaned up server process!")

    def __bool__(self):
        return self.process and self.process.poll() is None

    def run(self, cmd: list, expect_msg: str = None, timeout: int = None):
        assert (
            expect_msg is not None or timeout is not None
        ), "Expected one of expect_msg or timeout to not be None"

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
