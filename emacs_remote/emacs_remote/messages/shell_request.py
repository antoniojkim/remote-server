#!/usr/bin/env python3

import subprocess
from dataclasses import dataclass
from typing import List

from .message import Request, Response
from .registry import MessageTypeRegistry


@dataclass
class ShellRequest(Request):
    cmd: List[str]

    def run(self):
        p = subprocess.run(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return ShellResponse(
            p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")
        )


@dataclass
class ShellResponse(Response):
    returncode: int
    stdout: str
    stderr: str


MessageTypeRegistry.register(ShellRequest)
MessageTypeRegistry.register(ShellResponse)
