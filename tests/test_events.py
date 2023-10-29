from gevent.greenlet import Greenlet

from unittest import mock
from noneapi import events
from noneapi import containers
from noneapi import proxies
from noneapi import rpc


@mock.patch("noneapi.events._REGISTERED_EVENT_HANDLERS", {})
def test_register_events_handler():
    class Service:
        name = "test_service"

        @events.event_handler(service_name="test_service_2", topic="topic")
        def test(self, payload):
            return "ping"

    assert events._REGISTERED_EVENT_HANDLERS == {
        ("test_service_2", "topic"): Service.test
    }


def test_event_dispatcher():
    callback = mock.MagicMock()

    class MathService:
        name = "math_service"
        dispatch = events.EventDispatcher(host="127.0.0.1", port=6551)

        @rpc
        def sum(self, a, b):
            _result = a + b
            self.dispatch("sum", _result)
            return _result

    class SubscriberMath:
        name = "subscriber_math"
        math_service = proxies.ServiceProxy(
            host="127.0.0.1", port=5550,
            event_host="127.0.0.1", event_port=6551
        )

        @events.event_handler(service_name="math_service", topic="sum")
        def sum_dispatcher(self, payload):
            callback(payload)

        def sum(self, a, b):
            return self.math_service.sum(a, b)

    math_container = containers.Container(MathService)

    thread1 = Greenlet(
        run=math_container.run,
        **dict(
            host="127.0.0.1",
            port=5550,
            event_host="127.0.0.1",
            event_port=6551
        )
    )
    thread1.start()

    sub_math_container = containers.Container(SubscriberMath)
    sub_math_service = sub_math_container.init()

    thread2 = Greenlet(
        run=sub_math_container.subscribe,
        **dict(host="127.0.0.1", port=6551)
    )
    thread2.start()

    result = sub_math_service.sum(1, 2)

    assert result == 3

    thread1.kill()
    thread2.kill()
