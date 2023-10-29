import pytest

from noneapi.proxies import ServiceProxy, ClusterProxy
from noneapi.exceptions import ServiceNotFound, AsyncCallError


def test_remote_service_call(echo_server):
    class Service:
        name = "test_service"
        service_a = ServiceProxy(host="127.0.0.1", port=5555)

    service = Service()

    result = service.service_a.test(1, 2, 3, test=1, test2=2)

    assert result == {
        'method': 'test',
        'args': [1, 2, 3],
        'kwargs': {"test": 1, "test2": 2},
        'meta': {'headers': {}}
    }


def test_remote_service_async_call(echo_server):
    class Service:
        name = "test_service"
        service_a = ServiceProxy(host="127.0.0.1", port=5555)

    service = Service()

    with service.service_a as service_a:
        service_a.test.async_call(1, 2, 3, test=1, test2=2)
        service_a.test2.async_call(1, 2, 3)

        result_sync = service_a.test(1, 2, 3, test=1, test2=2)

        result_async2 = service_a.test2.result()
        result_async = service_a.test.result()

        assert result_sync == {
            'method': 'test',
            'args': [1, 2, 3],
            'kwargs': {"test": 1, "test2": 2},
            'meta': {'headers': {}}
        }

        assert result_async == result_sync

        assert result_async2 == {
            'method': 'test2',
            'args': [1, 2, 3],
            'kwargs': {},
            'meta': {'headers': {}}
        }

        service_a.test.async_call(1, 2, 3, test=1, test2=2)
        result_async = service_a.test.result()

        assert result_async == result_sync


def test_remote_service_try_call_without_async_context(echo_server):
    class Service:
        name = "test_service"
        service_a = ServiceProxy(host="127.0.0.1", port=5555)

    with pytest.raises(AsyncCallError):
        service = Service()
        service.service_a.test.async_call(1, 2, 3, test=1, test2=2)


def test_remote_service_through_cluster(echo_server):
    config = [
        {
            "name": "test_service_1",
            "host": "127.0.0.1",
            "port": 5555
        }
    ]

    with ClusterProxy(config) as cluster:
        result = cluster.test_service_1.test(1, 2, 3, test=1, test2=2)

        assert result == {
            'method': 'test',
            'args': [1, 2, 3],
            'kwargs': {"test": 1, "test2": 2},
            'meta': {'headers': {}}
        }


def test_async_remote_service_through_cluster(echo_server):
    config = [
        {
            "name": "test_service_1",
            "host": "127.0.0.1",
            "port": 5555
        },
        {
            "name": "test_service_2",
            "host": "127.0.0.1",
            "port": 5555
        }
    ]

    with ClusterProxy(config) as cluster:
        cluster.test_service_1.test.call_async(
            1, 2, 3, test=1, test2=2
        )
        assert cluster.test_service_1.test.result() == {
            'method': 'test',
            'args': [1, 2, 3],
            'kwargs': {"test": 1, "test2": 2},
            'meta': {'headers': {}}
        }

        cluster.test_service_2.test.call_async(
            1, 2, 3, test=1, test2=2
        )
        assert cluster.test_service_2.test.result() == {
            'method': 'test',
            'args': [1, 2, 3],
            'kwargs': {"test": 1, "test2": 2},
            'meta': {'headers': {}}
        }


def test_async_remote_service_through_cluster_with_exception(echo_server):
    config = [
        {
            "name": "test_service_1",
            "host": "127.0.0.1",
            "port": 5555

        }
    ]

    with ClusterProxy(config) as cluster:
        with pytest.raises(ServiceNotFound):
            cluster.test_service_2.test(1, 2, 3, test=1, test2=2)
