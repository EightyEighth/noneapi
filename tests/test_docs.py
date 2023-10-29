from noneapi.containers import Container, ContainerRunner
from noneapi.events import EventDispatcher
from noneapi.rpc import rpc
from gevent.threading import Thread
from unittest import mock


class MathService:
    name = "math_service"
    dispatch = EventDispatcher(host="127.0.0.1", port=6551)

    @rpc
    def sum(self, a, b):
        _result = a + b
        self.dispatch("sum", _result)
        return _result


@mock.patch("pdoc.Path.write_bytes", return_value=mock.MagicMock())
@mock.patch("pdoc.Path.mkdir", return_value=mock.MagicMock())
def test_generate_docs(_, __):
    with mock.patch(
            "pdoc.render.html_index",
            return_value=b""
    ) as html_index:
        with mock.patch(
                "pdoc.render.search_index",
                return_value=b""
        ) as search_index:
            math_container = Container(MathService)
            runner = ContainerRunner()
            runner.register(
                "math_service",
                math_container,
                host="127.0.0.1",
                port=8111
            )
            thread = Thread(target=runner.start)
            thread.daemon = True
            thread.start()
            thread.join(2)

            assert html_index.called
            assert search_index.called
