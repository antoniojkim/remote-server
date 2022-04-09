import socket
from queue import Empty as EmptyQueue
from queue import Queue
from threading import Thread

client_udp_port = 9130
server_udp_port = 9131


def client():
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
        s.bind(("localhost", client_udp_port))
        print("Client bound to power ", client_udp_port)

        for msg in (
            "test1",
            "test2",
            "test5",
        ):
            s.sendto(msg.encode("utf-8"), ("localhost", server_udp_port))


def server():
    queue = Queue()

    def udp_recv():
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
            s.bind(("localhost", server_udp_port))
            print("Server bound to power ", server_udp_port)

            for i in range(3):
                message, address = s.recvfrom(256)
                queue.put((message, address))

    udp_recv_thread = Thread(target=udp_recv)
    udp_recv_thread.start()

    def process_queue():
        while True:
            try:
                message, address = queue.get(timeout=2)
                print(
                    "Server: ", message.decode("utf-8"), len(message), "from", address
                )
            except EmptyQueue:
                break

    process_queue()


server_thread = Thread(target=server)
server_thread.start()

client_thread = Thread(target=client)
client_thread.start()

client_thread.join()
server_thread.join()
