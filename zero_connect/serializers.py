import msgpack
from typing import TypeVar, Protocol, runtime_checkable


RPCRequest = TypeVar("RPCRequest", bound=dict)
RPCResponse = TypeVar("RPCResponse", bound=dict)
SerializeProtocol = TypeVar("SerializeProtocol")


@runtime_checkable
class BaseSerializer(Protocol[SerializeProtocol, RPCRequest, RPCResponse]):
    """
    Base class for all serializers. It just serializes and deserializes data.
    """

    def serialize(self, data: RPCRequest) -> bytes:
        return self._serialize(data)

    def deserialize(self, data: bytes) -> RPCResponse:
        return self._deserialize(data)

    def _serialize(self, data: RPCRequest) -> bytes:
        """
        This method should be implemented in subclasses.
        Method convert data type that you choose to bytes before sending.
        """
        ...

    def _deserialize(self, data: bytes) -> RPCResponse:
        """
        This method should be implemented in subclasses.
        Method convert bytes to data type that you choose after receiving.
        """
        ...


class MSGPackSerializer(BaseSerializer[msgpack, RPCRequest, RPCResponse]):

    def __init__(self, serialize_protocol: msgpack = msgpack):
        self._serializer = serialize_protocol

    def _serialize(self, data: RPCRequest) -> bytes:
        return msgpack.packb(data)

    def _deserialize(self, data: bytes) -> RPCResponse:
        return msgpack.unpackb(data)
