import socket
import zlib
from dataclasses import astuple, is_dataclass

import msgpack


class SecureTCPSocket:
    def __init__(self, s=None):
        if s is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket = s

    def __enter__(self):
        self.socket.__enter__()
        return self

    def __exit__(self, *args):
        self.socket.__exit__(*args)

    def bind(self, host, port):
        return self.socket.bind((host, port))

    def listen(self):
        return self.socket.listen()

    def accept(self):
        conn, addr = self.socket.accept()
        return SecureTCPSocket(conn), addr

    def connect(self, host, port):
        return self.socket.connect((host, port))

    def sendall(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        elif is_dataclass(data):
            data = astuple(data)
        elif not isinstance(data, (list, tuple, dict)):
            raise TypeError(
                f"Expected data to be one of [str, list, tuple, dict, dataclass]. Got {type(data)}"
            )

        packed = msgpack.packb(data)
        compressed = zlib.compress(packed)

        self.socket.sendall(compressed)
        # writer = self.socket.makefile("bw")
        # writer.write(compressed)
        # writer.flush()

    def recvall(self, size=None, cls=None):
        data = self.socket.recv(1024)

        decompressed = zlib.decompress(data)
        data = msgpack.unpackb(decompressed)

        if isinstance(data, (tuple, list)) and cls:
            return cls(*data)

        return data
