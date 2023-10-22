import pytest
from zero_connect.protocols import RPCProtocol
from zero_connect.transports import ZeroMQTransport
from zero_connect.serializers import MSGPackSerializer


def test_create_without_transport():
    with pytest.raises(AssertionError):
        RPCProtocol(transport=None, serializer=None)


def test_create_without_serializer():
    with pytest.raises(AssertionError):
        RPCProtocol(transport=1, serializer=None)


def test_create_with_transport_and_serializer():
    with pytest.raises(ValueError):
        RPCProtocol(transport=1, serializer=1)


def test_create_correct_protocol(echo_server):
    protocol = RPCProtocol(
        transport=ZeroMQTransport(),
        serializer=MSGPackSerializer()
    )

    result = protocol.call(
        host="127.0.0.1", port=5555, method="test",
        args=[], kwargs={}, headers={}
    )

    assert result == {
        'method': 'test',
        'args': [],
        'kwargs': {},
        'meta': {'headers': {}}
    }

