from typing import Any, Protocol

from .exceptions import RemoteError, RemoteErrorData


class BaseRemoteErrorHandler(Protocol):
    def handle_exception(self, error: Exception) -> RemoteErrorData:
        ...

    def raise_remote_error(self, data: dict):
        ...

    def is_validate_error(self, error: dict) -> bool:
        ...


class RemoteErrorHandler(BaseRemoteErrorHandler):
    def handle_exception(self, error: Exception) -> RemoteErrorData:
        return RemoteError(original_exc=error, message=str(error)).to_dict()

    def raise_remote_error(self, data: dict):
        raise RemoteError.from_dict(data)

    def is_validate_error(self, data: Any) -> bool:
        return RemoteError.is_remote_error(data)
