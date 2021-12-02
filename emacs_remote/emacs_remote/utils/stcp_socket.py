import select
import socket
import zlib
import logging
from dataclasses import astuple, is_dataclass

import msgpack

from ..messages.registry import MessageTypeRegistry


class SecureTCPSocket:
    def __init__(self, s=None, logger=None):
        if s is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket = s

        if logger is None:
            logger = logging.getLogger("SecureTCPSocket")

        self.logger = logger

    def __enter__(self):
        self.socket.__enter__()
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.socket.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, 1)
        return self

    def __exit__(self, *args):
        self.socket.__exit__(*args)

    def set_logger(self, logger):
        self.logger = logger

    def bind(self, host, port):
        return self.socket.bind((host, port))

    def getsockname(self):
        return self.socket.getsockname()

    def listen(self):
        return self.socket.listen()

    def accept(self):
        conn, addr = self.socket.accept()
        return SecureTCPSocket(conn, self.logger), addr

    def connect(self, host, port):
        return self.socket.connect((host, port))

    def sendall(self, data):
        self.logger.debug(f"Sending data: {data}")

        message_type = MessageTypeRegistry.get_index(type(data))
        self.logger.debug(f"    message_type: {message_type}")

        if isinstance(data, str):
            data = (data,)
        elif is_dataclass(data):
            data = astuple(data)
        elif not isinstance(data, (list, tuple, dict)):
            raise TypeError(
                f"Expected data to be one of [str, list, tuple, dict, dataclass]. Got {type(data)}"
            )

        packed = msgpack.packb(data)
        compressed = zlib.compress(packed)
        self.logger.debug(f"    message_size: {len(compressed)}")

        size_message = bytearray()
        size_message.extend(msgpack.packb((message_type, len(compressed))))
        assert len(size_message) <= 16, "Expected size message to be less than 16 bytes"
        if len(size_message) < 16:
            size_message.extend(bytes(16 - len(size_message)))

        self.logger.debug(f"    sending size message...")

        self.socket.sendall(size_message)
        self.logger.debug(f"    sending payload...")

        self.socket.sendall(compressed)
        self.logger.debug(f"    Send Complete!")

    def recvall(self, timeout: float = None):
        """
        Receive all bytes in a message

        Will recv all for 2 messages. First one denoting size and type of actual message.
        Second one being the actual payload.

        Args:
            timeout: positive floating value representing seconds after which to return None
                timeout only applies to waiting for first message. Not second.
        """
        self.logger.debug("Receiving data")

        if timeout is not None:
            assert isinstance(timeout, (int, float)) and timeout > 0
            self.logger.debug(f"    Timeout: {timeout}")

            self.socket.setblocking(0)
            ready = select.select([self.socket], [], [], timeout)
            if not ready[0]:
                self.logger.debug(f"    timed out")
                raise TimeoutError()

        self.logger.debug(f"    receiving message size...")
        data = bytearray()
        while len(data) < 16:
            d = self.socket.recv(16)
            if len(d) == 0:
                self.logger.debug(f"        Received no data")
                return None
            data.extend(d)
            self.logger.debug(f"        received {len(d)} bytes (total: {len(data)})")

        data = data.strip(b"\x00")
        message_type, message_size = msgpack.unpackb(data)
        self.logger.debug(f"    message_type: {message_type}")
        self.logger.debug(f"    message_size: {message_size}")

        self.logger.debug(f"    receiving payload...")
        data = bytearray()
        while len(data) < message_size:
            d = self.socket.recv(1024)
            if len(d) == 0:
                return None
            data.extend(d)
            self.logger.debug(f"        received {len(d)} bytes (total: {len(data)})")

        self.logger.debug(f"    Received payload!")

        data = zlib.decompress(data)
        data = msgpack.unpackb(data)
        self.logger.debug(f"    Unpacked payload!")

        data = MessageTypeRegistry.get_type(message_type, data)
        self.logger.debug(f"    Got message!")

        return data
