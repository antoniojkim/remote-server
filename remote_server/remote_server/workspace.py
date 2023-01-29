import os
from dataclasses import dataclass
from pathlib import Path

# from emacs_remote.utils.logging import LoggerFactory


@dataclass
class Workspace:
    # The name of the host.
    # Will be the remote server name or IP address for the local client
    # or will be None for the remote server
    host: str
    # The path to the project workspace on the remote server
    workspace: str
    remote_server_path: str = Path.home().joinpath(".remote_server")

    def __post_init__(self):
        self.workspace = Path(self.workspace)
        self.workspace_hash = utils.md5((self.host, str(self.workspace)))

        self.workspace_name = self.workspace.name.replace(" ", "_")
        if self.workspace_name.isidentifier():
            self.workspace_name = f"{self.workspace_name}_{self.workspace_hash}"
        else:
            self.workspace_name = self.workspace_hash

        self.remote_server_path = Path(self.remote_server_path)
        self.remote_server_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.remote_server_path.joinpath(
            "workspaces", self.workspace_name
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        # self.base_path = self.workspace_path.joinpath(self.workspace.name)
        # self.base_path.mkdir(exist_ok=True)

        # self.logging_level = logging_level
        # self.logging_factory = LoggerFactory(
        #     logging_level, self.workspace_path.joinpath("client_interface.log")
        # )

    def __str__(self):
        return str(self.workspace)

    # def logger(self, name):
    #     return self.logging_factory.get_logger(name)
