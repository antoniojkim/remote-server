#!/usr/bin/env python3

import select
import socket
from time import sleep
from threading import Barrier, Event, Thread


def main():
    port = None
    barrier = Barrier(2)

    def server():
        nonlocal port

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            port = str(s.getsockname()[1])
            barrier.wait()

            s.listen()
            conn, addr = s.accept()

            i = 0
            with conn:
                while True:
                    conn.setblocking(0)
                    ready = select.select([conn], [], [], 2)
                    if not ready[0]:
                        print("Timed out")
                        continue

                    data = conn.recv(1024)
                    if not data:
                        break

                    data = data.decode("utf-8")
                    print(f"Data: {data}")

                    i += 1
                    conn.sendall(f"Received {i}".encode("utf-8"))

    def client():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", int(port)))

            for wait, message in (
                (0, "Test"),
                (0, "Test2"),
                (5, "Test Wait"),
            ):
                sleep(wait)
                s.sendall(message.encode("utf-8"))

                data = s.recv(1024)
                if data:
                    print(data.decode("utf-8"))

    server_thread = Thread(target=server)
    server_thread.start()
    barrier.wait()

    client_thread = Thread(target=client)
    client_thread.start()
    # barrier.wait()

    client_thread.join()
    server_thread.join()


if __name__ == "__main__":
    main()
