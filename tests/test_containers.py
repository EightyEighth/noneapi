import pytest
import requests
from gevent import Greenlet
from threading import Thread

from noneapi.rpc import rpc
from noneapi.containers import Container, ContainerRunner
from noneapi.proxies import ServiceProxy
from noneapi.exceptions import RemoteError


def test_container_call_methods():
    class ServiceMath:
        name = "test_service"

        @rpc
        def sum(self, a: int, b: int) -> int:
            return a + b

        @rpc
        def div(self, a: int, b: int) -> int:
            return a // b

        @rpc
        def mul(self, a: int, b: int) -> int:
            return a * b

    class Service:
        math_service = ServiceProxy(host="127.0.0.1", port=8000)

    container = Container(ServiceMath)

    thread = Greenlet(
        run=container.run,
        **dict(host="127.0.0.1", port=8000)
    )
    thread.start()

    service = Service()
    assert service.math_service.sum(1, 2) == 3
    assert service.math_service.div(10, 2) == 5
    assert service.math_service.mul(2, 2) == 4

    with pytest.raises(RemoteError):
        service.math_service.div(1, 0, 2)

    thread.kill()


def test_container_runner():
    class ServiceMath:
        name = "test_service"

        @rpc
        def sum(self, a: int, b: int) -> int:
            return a + b

    container = Container(ServiceMath)

    runner = ContainerRunner()
    runner.register("container", container, host="127.0.0.1", port=6543)
    thread = Thread(target=runner.start)
    thread.daemon = True
    thread.start()

    response = requests.get("http://127.0.0.1:8081", timeout=1)

    assert response.status_code == 200
    assert "html" in response.text
