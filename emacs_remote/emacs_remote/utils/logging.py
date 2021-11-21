#!/usr/bin/env python3

import logging
from enum import Enum


class LoggingLevel(Enum):
    info = 0
    debug = 1
    verbose = 2


_LOGGING_LEVELS = (logging.INFO, logging.DEBUG, logging.VERBOSE)


def get_level(enum_name: str):
    return _LOGGING_LEVELS[LoggingLevel[enum_name]]
