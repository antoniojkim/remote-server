#!/usr/bin/env python3

import select
import socket
from time import sleep
from threading import Barrier, Event, Thread
from queue import Queue, Empty as EmptyQueue

from emacs_remote.utils.stcp_socket import SecureTCPSocket


def main():
    port = None
    barrier = Barrier(2)

    requests = Queue()
    finish = Event()

    for i in range(100):
        requests.put("Test")

    def server():
        nonlocal port

        with SecureTCPSocket() as s:
            s.bind("localhost", 0)
            port = str(s.getsockname()[1])
            barrier.wait()

            s.listen()
            conn, addr = s.accept()

            i = 0
            with conn:
                while True:
                    try:
                        data = conn.recvall(timeout=2)
                        if not data:
                            break

                        print(f"Data: {data}")

                        i += 1
                        conn.sendall(f"Received {i}")

                        if data == "exit":
                            break
                    except TimeoutError:
                        pass

        print("Exiting server")

    def client():
        with SecureTCPSocket() as s:
            s.connect("localhost", int(port))

            while not finish.is_set():
                try:
                    request = requests.get(timeout=1)

                    s.sendall(request)
                    response = s.recvall()
                    if response:
                        print(response)
                except EmptyQueue as e:
                    pass

        print("Exiting client")

    server_thread = Thread(target=server)
    server_thread.start()
    barrier.wait()

    client_thread = Thread(target=client)
    client_thread.start()

    try:
        while True:
            message = input(">>> ")
            requests.put(message)
    except KeyboardInterrupt:
        pass

    requests.put("exit")
    finish.set()
    client_thread.join()
    server_thread.join()


if __name__ == "__main__":
    main()
