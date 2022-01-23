from dataclasses import dataclass

from .message import Request, Response
from .registry import MessageTypeRegistry


@dataclass
class GetFileResponse(Response):
    file_path: str = None
    absolute: bool = False
    file_contents: bytes = None

    def run(self, client):
        if file_contents:
            file_path = client.base_path.joinpath(self.file_path)
            file_path.write_bytes(self.file_contents)


@dataclass
class GetFileRequest(Request):
    file_path: str
    absolute: bool = False

    def run(self, daemon):
        daemon.logger.debug(f"Getting file {file_name}")

        if self.absolute:
            pass
        else:
            file_path = daemon.workspace.joinpath(self.file_path)
            if not file_path.exists():
                return GetFileResponse()

            return GetFileResponse(self.file_path, self.absolute, file_path.read_bytes)


@dataclass
class SendFileResponse(Response):
    success: bool


@dataclass
class SendFileRequest(Request):
    def run(self, daemon):
        # daemon.logger.debug("Running Terminate Request")
        # daemon.finish.set()
        return ClientTerminateResponse(True)


MessageTypeRegistry.register(GetFileRequest)
MessageTypeRegistry.register(GetFileResponse)
MessageTypeRegistry.register(SendFileRequest)
MessageTypeRegistry.register(SendFileResponse)
