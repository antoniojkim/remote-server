# import multiprocessing
import socket
from pathlib import Path
from time import sleep

from emacs_remote import utils
from emacs_remote.messages.startup import SERVER_STARTUP_MSG


class ServerDaemon:
    def __init__(self, emacs_remote_path, workspace, ports):
        self.workspace = workspace
        self.workspace_hash = utils.md5(workspace)
        self.ports = ports

        self.server_tcps = []

        self.emacs_remote_path = Path(emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        self.startup_barrier = None  # multiprocessing.Barrier(len(self.ports) + 1)
        self.processes = []

    @staticmethod
    def listen(startup_barrier, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", int(port)))
            print(SERVER_STARTUP_MSG, flush=True)
            # startup_barrier.wait()

            s.listen()
            conn, addr = s.accept()
            print(f"Connection accepted from {addr}")
            # with conn:
            #     while True:
            #         data = conn.recv(1024)
            #         if not data:
            #             break

            #         print(data.decode("utf-8"))
            #         conn.send("Received".encore("utf-8"))
            #

    def __enter__(self):
        port = self.ports[0]
        print("Starting listen", flush=True)
        ServerDaemon.listen(self.startup_barrier, port)
        print("Exiting...")
        # for port in self.ports:
        #     p = multiprocessing.Process(
        #         target=ServerDaemon.listen,
        #         args=(self.startup_barrier, port)
        #     )
        #     print("Starting process")
        #     p.start()
        #     print("Started process")
        #     self.processes.append(p)

        # print("Waiting at barrier")
        # self.startup_barrier.wait()
        # print("Barrier crossed")
        return self

    def __exit__(self, *args):
        for p in self.processes:
            # p.terminate()
            p.join()
