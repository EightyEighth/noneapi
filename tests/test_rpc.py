from unittest import mock
from zero_connect import rpc


@mock.patch("zero_connect.rpc._REGISTERED_METHODS", {})
def test_register_rpc_methods():

    class Service:
        name = "test_service"

        @rpc.rpc
        def test(self, arg1: int, arg2: str, bar: str = "baz"):
            return None

    assert rpc._REGISTERED_METHODS == {
        "Service.test": Service.test
    }
