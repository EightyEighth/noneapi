import inspect
from importlib import import_module
from typing import Any, TypedDict


class RemoteErrorData(TypedDict):
    exc_type: str
    exc_path: str
    exc_args: list[str]
    value: str


def get_module_path(exc_type):
    module = inspect.getmodule(exc_type)
    return f"{module.__name__}.{exc_type.__name__}"


class BaseError(Exception):
    pass


class RemoteError(BaseError):
    """Raised when a remote error occurs."""

    def __init__(self, original_exc: Exception, message: str) -> None:
        self._original_exc = original_exc
        self._message = message
        super().__init__(
            f"{self._original_exc.__class__.__name__}: {self._message}"
        )

    def to_dict(self) -> RemoteErrorData:
        return {
            "exc_type": type(self._original_exc).__name__,
            "exc_path": get_module_path(self._original_exc.__class__),
            "exc_args": list(self._original_exc.args),
            "value": str(self._original_exc),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RemoteError":
        module_path, class_name = data["exc_path"].rsplit(".", 1)
        module = import_module(module_path)
        exc_cls = getattr(module, class_name)
        original_exc = exc_cls(*data["exc_args"])

        return cls(original_exc, data["value"])

    @staticmethod
    def is_remote_error(data: Any) -> bool:
        return isinstance(data, dict) and "exc_type" in data


class ContainerStopped(BaseError):
    """Raised when the container is stopped."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Container {name} is stopped")


class ServiceNotFound(BaseError):
    """Raised when the service is not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Service {name} is not found")


class AsyncCallError(BaseError):
    """Raised when the async call is out of context."""

    pass
