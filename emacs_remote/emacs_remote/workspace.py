import os
from dataclasses import dataclass
from pathlib import Path

from emacs_remote.utils.logging import LoggerFactory


@dataclass
class Workspace:
    host: str
    emacs_remote_path: str
    workspace: str
    logging_level: str = "info"

    def __post_init__(self):
        self.workspace = Path(self.workspace)
        self.workspace_hash = utils.md5((self.host, str(self.workspace)))

        self.emacs_remote_path = Path(self.emacs_remote_path)
        self.emacs_remote_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path = self.emacs_remote_path.joinpath(
            "workspaces", self.workspace_hash
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.workspace_path.resolve())

        self.base_path = self.workspace_path.joinpath(self.workspace.name)
        self.base_path.mkdir(exist_ok=True)

        self.logging_level = logging_level
        self.logging_factory = LoggerFactory(
            logging_level, self.workspace_path.joinpath("client_interface.log")
        )

    def __str__(self):
        return str(self.workspace)

    def logger(self, name):
        return self.logging_factory.get_logger(name)
