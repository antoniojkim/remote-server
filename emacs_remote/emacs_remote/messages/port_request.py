from dataclasses import dataclass

from .message import Request, Response
from .registry import MessageTypeRegistry


@dataclass
class PortResponse(Response):
    port: str = None


@dataclass
class PortRequest(Request):
    file_path: str
    absolute: bool = False

    def run(self, daemon: "ClientDaemon"):
        return PortResponse(daemon.server.next_client_port())


MessageTypeRegistry.register(PortRequest)
MessageTypeRegistry.register(PortResponse)
