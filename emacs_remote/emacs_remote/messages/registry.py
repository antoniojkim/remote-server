#!/usr/bin/env python3
from collections import OrderedDict
from dataclasses import is_dataclass


class MessageTypeRegistry:
    registered_types = []
    type_dict = {}

    @staticmethod
    def register(type):
        if type not in MessageTypeRegistry.type_dict:
            if not is_dataclass(type) and type not in (str, list, tuple, dict):
                raise TypeError(
                    "Expected data to be one of [str, list, tuple, dict, dataclass]. "
                    f"Got {type(data)}"
                )

            MessageTypeRegistry.type_dict[type] = len(
                MessageTypeRegistry.registered_types
            )
            MessageTypeRegistry.registered_types.append(type)

    @staticmethod
    def get_type(index: int, data=None):
        assert isinstance(index, int) and (
            0 <= index < len(MessageTypeRegistry.registered_types)
        )
        _type = MessageTypeRegistry.registered_types[index]

        if data is None:
            return _type
        elif isinstance(data, (list, tuple)):
            return _type(*data)
        elif isinstance(data, dict):
            return _type(**data)
        else:
            return TypeError(
                "Expected list, tuple or dict for data. " f"Got: {type(data)}"
            )

    @staticmethod
    def get_index(type):
        return MessageTypeRegistry.type_dict[type]


MessageTypeRegistry.register(str)
MessageTypeRegistry.register(list)
MessageTypeRegistry.register(dict)
MessageTypeRegistry.register(list)
