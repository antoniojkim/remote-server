import enum
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, is_dataclass, make_dataclass, astuple, field

import msgpack


class_re = re.compile("<class '(?P<name>[^']+)'>")

request_registry = {}
request_enum = None

def request(cls):
    """
    Decorator that registers the class as a Request

    Assigns the class a request type whose value corresponds
    """
    global request_enum

    # Check that the class implements __call__
    assert callable(getattr(cls, "__call__"))

    if not is_dataclass(cls):
        cls = dataclass(cls)

    cls_name = cls.__name__
    request_type = cls_name.split(".")[-1].upper()

    if request_type in request_registry:
        raise ValueError("Duplicate registering of request class")

    request_types = list(request_registry.keys())
    request_types.append(request_type)

    request_enum = enum.Enum('RequestEnum', sorted(request_types))

    cls = make_dataclass(cls_name, fields=[("request_type", int, field(default_factory=lambda: request_enum[request_type].value))], bases=(cls,))

    request_registry[request_type] = cls

    def encode(self):
        return msgpack.packb(astuple(self))

    cls.encode = encode

    return cls

def is_request(cls):
    return hasattr(cls, "request_type")

def decode_request(data):
    args = msgpack.unpackb(data)
    request_type = args[-1]
    cls = request_registry[request_enum._value2member_map_[request_type].name]
    return cls(*args)


response_registry = {}
response_enum = None

def register_response_enum(name, cls):
    global response_enum

    response_registry[name] = cls

    response_enum = enum.Enum('ResponseEnum', sorted(response_registry.keys()))
    for key, val in response_registry.items():
        val.response_type = response_enum[key]


def response(cls):
    if not is_dataclass(cls):
        cls = dataclass(cls)

    cls_name = cls.__name__
    response_type = cls_name.split(".")[-1].upper()

    if response_type in response_registry:
        raise ValueError("Duplicate registering of response class")

    response_types = list(response_registry.keys())
    response_types.append(response_type)

    response_enum = enum.Enum('ResponseEnum', sorted(response_types))

    cls = make_dataclass(cls_name, fields=[("response_type", int, field(default_factory=lambda: response_enum[response_type].value))], bases=(cls,))

    response_registry[response_type] = cls

    def encode(self):
        return msgpack.packb(astuple(self))

    cls.encode = encode

    return cls

def is_response(cls):
    return hasattr(cls, "response_type")

def decode_response(data):
    args = msgpack.unpackb(data)
    response_type = args[-1]
    cls = response_registry[response_enum._value2member_map_[response_type].value]
    return cls(*args)
