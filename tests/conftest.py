import pytest
from pydantic import BaseModel
from gevent.greenlet import Greenlet
from noneapi.servers import ZeroMQRPCServer
from noneapi.containers import Container, ServiceInterface


def start_server(host, port, callback):
    server = ZeroMQRPCServer(
        host=host, port=port, callback=callback
    )

    thread = Greenlet(run=server.run)
    thread.start()

    return server


@pytest.fixture(scope="session")
def echo_server():
    callback = lambda msg: msg
    server = start_server(host="127.0.0.1", port=5555, callback=callback)

    yield server

    server.stop()


@pytest.fixture(scope="function")
def math_server():
    class Calculate(BaseModel):
        a: int
        b: int
        method: str

    class MathService(ServiceInterface):
        def sum(self, a: int, b: int) -> int:
            return a + b

        def div(self, a: int, b: int) -> int:
            return a // b

        def mul(self, a: int, b: int) -> int:
            return a * b

        def calculate(self, c: Calculate) -> int:
            method = getattr(self, c.method)
            return method(c.a, c.b)

    container = Container(MathService)
    thread = Greenlet(
        target=container.run,
        **dict(host="127.0.0.1", port=3001)
    )
    thread.start()

    yield thread

    thread.kill()
