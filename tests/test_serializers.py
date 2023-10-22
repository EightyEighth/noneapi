from zero_connect.serializers import MSGPackSerializer


def test_serialize():
    serializer = MSGPackSerializer()
    data = {"test": "test"}
    result = serializer.serialize(data)

    assert result == b"\x81\xa4test\xa4test"


def test_deserialize():
    serializer = MSGPackSerializer()
    data = b"\x81\xa4test\xa4test"
    result = serializer.deserialize(data)

    assert result == {"test": "test"}
