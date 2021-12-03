import logging
from enum import Enum


class LoggingLevel(Enum):
    info = 0
    debug = 1


_LOGGING_LEVELS = (logging.INFO, logging.DEBUG)


class LoggerFactory:
    def __init__(self, level, filepath=None):
        self.level = Logger.get_level(level)

        logging.basicConfig(
            level=self.level,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
        )

        self.file_handler = None
        if filepath is not None:
            self.file_handler = logging.FileHandler(filepath, mode="w")
            self.file_handler.setLevel(self.level)

        self.loggers = {}

    def get_logger(self, name):
        logger = self.loggers.get(name)
        if logger:
            return logger

        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        if self.file_handler:
            logger.addHandler(self.file_handler)

        self.loggers[name] = logger

        return logger

    @staticmethod
    def get_level(enum_name: str):
        return _LOGGING_LEVELS[LoggingLevel[enum_name].value]
