from zero_connect.protocols import RPCProtocol
from zero_connect.serializers import JSONSerializer


def test_create_correct_protocol(echo_server):
    protocol = RPCProtocol(
        serializer=JSONSerializer()
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

