import abc


class Response(abc.ABC):
    def run(self, client) -> None:
        pass


class Request(abc.ABC):
    @abc.abstractmethod
    def run(self, daemon) -> Response:
        pass
