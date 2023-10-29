from typing import Callable

_REGISTERED_METHODS: dict[str, Callable] = {}


def rpc(method: Callable) -> Callable:
    global _REGISTERED_METHODS

    method_name = method.__name__
    method_class = method.__qualname__.split(".")[-2]

    if method_name not in _REGISTERED_METHODS:
        _REGISTERED_METHODS[f"{method_class}.{method_name}"] = method

    return method
