from dataclasses import dataclass

from .message import Request, Response
from .registry import MessageTypeRegistry


@dataclass
class TerminateResponse(Response):
    success: bool


@dataclass
class TerminateRequest(Request):
    def run(self, daemon):
        daemon.logger.debug("Running Terminate Request")
        daemon.finish.set()
        return TerminateResponse(True)


MessageTypeRegistry.register(TerminateRequest)
MessageTypeRegistry.register(TerminateResponse)
