from dataclasses import dataclass, asdict
from typing import TypeVar, Generic, Any
from zero_connect.transports import BaseTransport, PROTOCOLS, TCP
from zero_connect.serializers import BaseSerializer


T = TypeVar("T")
_Transport = TypeVar("_Transport")
_Serializer = TypeVar("_Serializer")


@dataclass(frozen=True)
class _BaseConvertor:
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "_BaseConvertor":
        return cls(**data)


@dataclass(frozen=True)
class Meta(_BaseConvertor):
    """
    Meta information about RPC request.
    """
    headers: dict


@dataclass(frozen=True)
class RPCRequest(_BaseConvertor):
    """
    RPC request body.
    """
    method: str
    args: tuple
    kwargs: dict
    meta: Meta


@dataclass(frozen=True)
class RPCResponse(_BaseConvertor):
    """
    RPC response body.
    """
    result: dict
    request: RPCRequest


class RPCProtocol(Generic[_Transport, _Serializer]):
    """
    Base class for all RPC protocols. This class is responsible for
    convert data to RPC request and RPC response for communication between
    services.
    """
    def __init__(self, transport: _Transport, serializer: _Serializer):

        assert transport, "Transport is not defined"
        assert serializer, "Serializer is not defined"

        if not isinstance(transport, BaseTransport):
            raise ValueError("Transport should be instance of BaseTransport")

        if not isinstance(serializer, BaseSerializer):
            raise ValueError("Serializer should be instance of BaseSerializer")

        self._transport = transport
        self._serializer = serializer

    @staticmethod
    def _build_request(
            method: str, args: Any, kwargs: Any, headers: dict = None
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
            host: str | None = None,
            port: int | None = None,
            headers: dict[Any, Any] = None,
            protocol: PROTOCOLS = TCP
    ) -> Any:
        """
        Call remote method.
        """
        request = self._build_request(method, args, kwargs, headers)
        data = self._serializer.serialize(request.to_dict())
        result = self._transport.request(host, port, data, protocol)

        result = self._serializer.deserialize(result)
        return result

    def send(
        self,
        method: str,
        args: list[Any] | tuple[Any],
        kwargs: dict[Any, Any],
        host: str | None = None,
        port: int | None = None,
        socket: Any = None,
        headers: dict[Any, Any] = None,
        protocol: PROTOCOLS = TCP
    ) -> Any:
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
        :return: Any
        """
        request = self._build_request(method, args, kwargs, headers)
        data = self._serializer.serialize(request.to_dict())

        result = self._transport.send(
            data, protocol, host=host, port=port, socket=socket
        )

        return result

    def receive(self, socket: Any) -> Any:
        """
        Receive data from the remote endpoint. Low level method.
        Uses by server for receiving requests.
        """

        bytes_result = self._transport.receive(socket)
        result = self._serializer.deserialize(bytes_result)

        return result

    def dispatch(
            self, host: str, port: int,  topic: str, payload: dict,
            protocol: PROTOCOLS = TCP, through_broker: bool = False
    ) -> None:
        """
        Publish event to subscribers.
        """
        data = self._serializer.serialize(payload)
        self._transport.dispatch(
            host, port, topic, data, protocol, through_broker
        )

    def parse_call(self, data: bytes) -> tuple[str, list[Any], dict[Any, Any]]:
        """
        Parse incoming data to method name, args and kwargs.
        :param data: bytes
        :return: tuple[str, list[Any], dict[Any, Any]]
        """
        data = self._serializer.deserialize(data)

        return data["method"], data["args"], data["kwargs"]

    def parse_event(self, data: bytes) -> dict:
        """
        Parse incoming data to topic and payload.
        :param data: bytes
        :return: dict
        """
        data = self._serializer.deserialize(data)

        return data

    def build_response(self, result: dict) -> bytes:
        """
        Build response from result and request.
        :param result: dict
        :return: bytes
        """

        return self._serializer.serialize(result)
