import logging
import select
import socket
import zlib
from dataclasses import astuple, is_dataclass

import msgpack

from ..messages.registry import MessageTypeRegistry
from ..utils.logging import LoggerFactory


class SecureTCPSocket:
    def __init__(self, s=None, logger=None):
        if s is None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket = s
        self.host = None
        self.port = None

        if logger is None:
            logger = LoggerFactory().get_logger("SecureTCPSocket")

        self.logger = logger

        self.recv_buffer = bytearray()

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
        self.host = host
        self.port = port
        out = self.socket.bind((host, port))
        self.logger.debug(f"Bound socket to {host}:{port}")
        return out

    def getsockname(self):
        return self.socket.getsockname()

    def listen(self):
        self.logger.debug(f"Listening on port {self.port}")
        return self.socket.listen()

    def accept(self):
        conn, addr = self.socket.accept()
        self.logger.debug(f"Connection accepted from {addr}")
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

        size_message = msgpack.packb((message_type, len(compressed)))
        assert len(size_message) <= 16, "Expected size message to be less than 16 bytes"

        payload = bytearray()
        payload.extend(size_message)
        if len(size_message) < 16:
            payload.extend(bytes(16 - len(size_message)))

        payload.extend(compressed)

        try:
            self.logger.debug(f"    sending payload ({len(payload)})...")
            self.socket.sendall(payload)
        except:
            self.logger.error("Failed to send payload")
            raise

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

            try:
                self.socket.setblocking(False)
                ready = select.select([self.socket], [], [], timeout)
                if not ready[0]:
                    self.logger.debug(f"    timed out")
                    raise TimeoutError()
            finally:
                self.socket.setblocking(True)

        self.logger.debug(f"    receiving payload...")
        while len(self.recv_buffer) < 16:
            data = self.socket.recv(1024)
            if not data:
                self.logger.debug(
                    f"        Received no data (total: {len(self.recv_buffer)})"
                )
                return None

            self.recv_buffer.extend(data)
            self.logger.debug(
                f"        received {len(data)} bytes (total: {len(self.recv_buffer)})"
            )

        assert len(self.recv_buffer) >= 16

        size_message = self.recv_buffer[:16].strip(b"\x00")

        message_type, message_size = msgpack.unpackb(size_message)
        self.logger.debug(f"    message_type: {message_type}")
        self.logger.debug(f"    message_size: {message_size}")

        self.recv_buffer = self.recv_buffer[16:]
        while len(self.recv_buffer) < message_size:
            data = self.socket.recv(4096)
            if len(data) == 0:
                return None

            self.recv_buffer.extend(data)
            self.logger.debug(
                f"        received {len(data)} bytes (total: {len(self.recv_buffer)})"
            )

        self.logger.debug(f"    Received payload!")

        payload = self.recv_buffer[:message_size]
        self.recv_buffer = self.recv_buffer[message_size:]

        data = zlib.decompress(payload)
        data = msgpack.unpackb(data)
        self.logger.debug(f"    Unpacked data!")

        message = MessageTypeRegistry.get_type(message_type, data)
        self.logger.debug(f"    Got message!")

        return message
