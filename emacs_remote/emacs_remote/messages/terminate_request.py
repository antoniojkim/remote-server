from dataclasses import dataclass

from .message import Request, Response
from .registry import MessageTypeRegistry


@dataclass
class ServerTerminateResponse(Response):
    success: bool


@dataclass
class ServerTerminateRequest(Request):
    def run(self, daemon):
        daemon.logger.debug("Running Terminate Request")
        daemon.finish.set()
        return ServerTerminateResponse(True)


@dataclass
class ClientTerminateResponse(Response):
    success: bool


@dataclass
class ClientTerminateRequest(Request):
    def run(self, daemon):
        # daemon.logger.debug("Running Terminate Request")
        # daemon.finish.set()
        return ClientTerminateResponse(True)


MessageTypeRegistry.register(ServerTerminateRequest)
MessageTypeRegistry.register(ServerTerminateResponse)
MessageTypeRegistry.register(ClientTerminateRequest)
MessageTypeRegistry.register(ClientTerminateResponse)
