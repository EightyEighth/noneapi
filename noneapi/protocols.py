from dataclasses import asdict, dataclass
from typing import Any, Generic, TypeVar

import zmq.green as zmq

from .serializers import BaseSerializer
from .transports import TCP, ProtocolType, ZeroMQTransport

T = TypeVar("T")
_Serializer = TypeVar("_Serializer", bound=BaseSerializer)


@dataclass(frozen=True)
class Meta:
    """
    Meta information about RPC request.
    """

    headers: dict


@dataclass(frozen=True)
class RPCRequest:
    """
    RPC request body.
    """

    method: str
    args: tuple
    kwargs: dict
    meta: Meta


@dataclass(frozen=True)
class RPCResponse:
    """
    RPC response body.
    """

    result: dict
    request: RPCRequest


class RPCProtocol(Generic[_Serializer]):
    """
    Base class for all RPC protocols. This class is responsible for
    convert data to RPC request and RPC response for communication between
    services.
    """

    def __init__(self, serializer: _Serializer):
        self._transport = ZeroMQTransport()
        self._serializer = serializer

    @staticmethod
    def _build_request(
        method: str, args: Any, kwargs: Any, headers: dict | None = None
    ) -> RPCRequest:
        return RPCRequest(
            method=method,
            args=args,
            kwargs=kwargs,
            meta=Meta(headers=headers or {}),
        )

    def call(
        self,
        method: str,
        args: list[Any] | tuple[Any],
        kwargs: dict[Any, Any],
        host: str,
        port: int,
        headers: dict[Any, Any] | None = None,
        protocol: ProtocolType = TCP,
    ) -> dict | list:
        """
        Call remote method.
        """
        request: RPCRequest = self._build_request(
            method, args, kwargs, headers
        )

        data: bytes = self._serializer.serialize(asdict(request))
        bytes_result: bytes = self._transport.request(
            host, port, data, protocol
        )

        result: dict | list = self._serializer.deserialize(bytes_result)

        return result

    def send(
        self,
        method: str,
        args: list[Any] | tuple[Any],
        kwargs: dict[Any, Any],
        host: str,
        port: int,
        socket: Any = None,
        headers: dict[Any, Any] | None = None,
        protocol: ProtocolType = TCP,
    ) -> zmq.Socket:
        """
        Send data to the remote endpoint. Low level method.
        Uses by server for sending responses.

        :arg host: host to send
        :arg port: port to send
        :arg protocol: protocol to use
        :arg headers: headers to send
        :arg method: method to send
        :arg args: args to send
        :arg kwargs: kwargs to send
        :arg socket: socket to use
        :return: zmq.Socket
        """
        request: RPCRequest = self._build_request(
            method, args, kwargs, headers
        )
        data: bytes = self._serializer.serialize(asdict(request))

        connection: zmq.Socket = self._transport.send(
            data, protocol, host=host, port=port, socket=socket
        )

        return connection

    def receive(self, socket: zmq.Socket) -> dict | list:
        """
        Receive data from the remote endpoint. Low level method.
        Uses by server for receiving requests.
        """

        bytes_result: bytes = self._transport.receive(socket)
        result: dict | list = self._serializer.deserialize(bytes_result)

        return result

    def dispatch(
        self,
        host: str,
        port: int,
        topic: str,
        payload: dict,
        protocol: ProtocolType = TCP,
        through_broker: bool = False,
    ) -> None:
        """
        Publish event to subscribers.
        """
        data: bytes = self._serializer.serialize(payload)
        self._transport.dispatch(
            host, port, topic, data, protocol, through_broker
        )

    def parse_call(
            self, data: bytes
    ) -> tuple[str, tuple[Any, ...], dict[Any, Any]]:
        """
        Parse incoming data to method name, args and kwargs.
        :param data: bytes
        :return: tuple[str, list[Any], dict[Any, Any]]
        """
        result: dict = self._serializer.deserialize(data)
        request = RPCRequest(**result)

        return request.method, request.args, request.kwargs

    def parse_event(self, data: bytes) -> dict:
        """
        Parse incoming data to topic and payload.
        :param data: bytes
        :return: dict
        """
        return self._serializer.deserialize(data)

    def build_response(self, result: dict) -> bytes:
        """
        Build response from result and request.
        :param result: dict
        :return: bytes
        """

        return self._serializer.serialize(result)
