import abc


class Response(abc.ABC):
    pass


class Request(abc.ABC):
    @abc.abstractmethod
    def run(self) -> Response:
        pass
