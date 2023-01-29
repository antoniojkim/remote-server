import subprocess

from request import request, response

@response
class ConnectionResponse:
    def __call__(self) -> int:

@request
class ConnectionRequest:
    def __call__(self) -> ConnectionResponse:
        pass


@response
class ExitResponse:
    exitcode: int

    def __call__(self) -> int:
        return self.exitcode


@request
class ExitRequest:
    exitcode: int

    def __call__(self) -> ExitResponse:
        return ExitResponse(self.exitcode)



@response
class ShellResponse:
    stdout: str
    stderr: str
    returncode: int

    def __call__(self) -> int:
        print(self.stdout)
        return self.returncode


@request
class ShellRequest:
    cmd: List[str]

    def __call__(self) -> ShellResponse:
        s = subprocess.run(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return ShellResponse(
            s.stdout,
            s.stderr,
            s.returncode,
        )
