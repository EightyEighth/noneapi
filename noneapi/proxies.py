from typing import Any, TypedDict

import zmq.green as zmq

from .exceptions import AsyncCallError, ServiceNotFound
from .handlers import RemoteErrorHandler
from .protocols import RPCProtocol
from .serializers import ORJSONSerializer


class ClusterServiceProxy(TypedDict):
    name: str
    host: str
    port: int


class RPCProxy:
    """Base class for proxy classes."""

    async_methods = ["async_call", "result"]

    def __init__(
        self,
        current_service: Any,
        host: str | None = None,
        port: int | None = None,
        event_host: str | None = None,
        event_port: int | None = None,
    ) -> None:
        self._current_service = current_service
        self._host = host
        self._port = port
        self._event_host = event_host
        self._event_port = event_port
        self._method_name: str = ""
        self._active_async_calls: dict[str, zmq.Socket] = {}
        self._is_async_context: bool = False
        self._protocol: RPCProtocol | None = None

    def __getattr__(self, name: str) -> "Any":
        self._method_name = name
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call(*args, **kwargs)

    def __enter__(self) -> "Any":
        self._is_async_context = True
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._is_async_context = False
        for connection in self._active_async_calls.values():
            connection.close()

        self._active_async_calls = {}

    def async_call(self, *args: Any, **kwargs: Any) -> None:
        """
        Call remote method asynchronously.
        :param args: args for remote method.
        :param kwargs: kwargs for remote method.
        :return: None
        """
        if not self._is_async_context:
            raise AsyncCallError("Async call should be in async context")

        protocol = self._get_protocol()

        connection = self._active_async_calls.get(self._method_name)

        connection_new = protocol.send(
            host=self._host,
            port=self._port,
            method=self._method_name,
            args=args,
            kwargs=kwargs,
            headers={},
            socket=connection,
        )

        if not connection:
            self._active_async_calls[self._method_name] = connection_new

    def call_async(self, *args: Any, **kwargs: Any) -> None:
        self.async_call(*args, **kwargs)

    def result(self) -> Any:
        """
        Get result of async call.
        :return: Any
        """
        if not self._is_async_context:
            raise AsyncCallError("Async call should be in async context")

        protocol = self._get_protocol()

        if self._method_name not in self._active_async_calls:
            raise AsyncCallError(
                f"Async call for method {self._method_name} was never called"
            )

        response = protocol.receive(
            socket=self._active_async_calls[self._method_name]
        )

        handler = RemoteErrorHandler()

        if handler.is_validate_error(response):
            handler.raise_remote_error(response)

        return response

    def _call(self, *args: Any, **kwargs: Any) -> dict:
        protocol = self._get_protocol()

        response = protocol.call(
            host=self._host,
            port=self._port,
            method=self._method_name,
            args=args,
            kwargs=kwargs,
            headers={},
        )

        handler = RemoteErrorHandler()

        if handler.is_validate_error(response):
            handler.raise_remote_error(response)

        return response

    def _get_protocol(self) -> Any:
        """
        Get protocol from current service if it exists else return default.
        :return: RPCProtocol - protocol for communication between services.
        """
        if not self._protocol:
            self._protocol = RPCProtocol(ORJSONSerializer())

        return self._protocol


class ServiceProxy:
    """
    Proxy class for remote service calls.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        event_host: str | None = None,
        event_port: int | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._event_host = event_host
        self._event_port = event_port

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance: Any, owner: Any) -> "RPCProxy":
        """
        Get RPCProxy instance. Delegate all calls to RPCProxy.
        :return: Proxy instance.
        """
        return instance.__dict__.setdefault(
            self._name,
            RPCProxy(
                instance, self._host, self._port, self._event_host,
                self._event_port
            ),
        )

    def __set__(self, instance: Any, value: Any) -> None:
        raise AttributeError("Can't set attribute")


class ClusterProxy:
    """
    Proxy class for remote cluster calls.
    """

    def __init__(self, config: list[ClusterServiceProxy]) -> None:
        self._config = config
        self._services: dict[str, RPCProxy] = {}

        self._init()

    def __getattr__(self, name: str) -> "RPCProxy":
        try:
            return self._services[name]
        except KeyError as e:
            raise ServiceNotFound(name) from e

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        for _service in self._services.values():
            del _service

    def _init(self):
        for service in self._config:
            proxy = RPCProxy(self, host=service["host"], port=service["port"])
            proxy._is_async_context = True
            self._services[service["name"]] = proxy
