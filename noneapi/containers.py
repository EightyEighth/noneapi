import weakref
from pathlib import Path
from typing import Any, Generic, List, Type, TypeVar, Union

import gevent  # type: ignore
from gevent import monkey  # type: ignore
from gevent.greenlet import Greenlet  # type: ignore
from loguru import logger

from .docs import generate_docs_for_service, get_paths, start_docs_server
from .events import _REGISTERED_EVENT_HANDLERS
from .exceptions import ContainerStopped
from .handlers import BaseRemoteErrorHandler, RemoteErrorHandler
from .protocols import RPCProtocol
from .proxies import ServiceProxy
from .rpc import _REGISTERED_METHODS
from .serializers import ORJSONSerializer
from .servers import ZeroMQRPCServer, ZeroMQSubscribeServer
from .services import ServiceInterface
from .transports import TCP, ProtocolType
from .validations import validate_or_ignore

monkey.patch_all()

T = TypeVar("T")
_SI = TypeVar("_SI", bound=ServiceInterface)

Address = Union[str, Path]


class Container(Generic[_SI]):
    """
    Service container responsible for managing the lifecycle of services.

    :param service_class: Service class implementing the ServiceInterface.
    :type service_class: Type[ServiceInterface]
    """

    def __init__(
        self,
        service_class: Type[_SI],
        error_callback: Type[BaseRemoteErrorHandler] = RemoteErrorHandler,
    ):
        self._service_class = service_class
        self._service: _SI | None = None
        self._error_callback = error_callback
        self._rpc_server: weakref.ref[ZeroMQRPCServer] | None = None
        self._event_servers: list[weakref.ref[ZeroMQSubscribeServer]] = []
        self.modules: list[str | Path] = []

    def run(
        self,
        host: str,
        port: int,
        event_host: str | None = None,
        event_port: int | None = None,
        workers: int = 1,
        protocol: ProtocolType = TCP,
        events_protocol: ProtocolType = TCP,
        is_debug: bool = False,
        through_broker: bool = False,
    ) -> None:
        """
        Initialize and run the service.

        :param host: RPC host.
        :param port: RPC port.
        :param event_host: Event host (optional).
        :param event_port: Event port (optional).
        :param workers: Number of worker threads.
        :param protocol: RPC protocol.
        :param events_protocol: Events protocol.
        :param is_debug: Debug flag.
        :param through_broker: Use broker or not.
        """
        self.init()

        if event_host and event_port:
            self.subscribe(
                event_host,
                event_port,
                events_protocol,
                is_debug=is_debug,
                through_broker=through_broker,
            )

        server = ZeroMQRPCServer(
            host=host,
            port=port,
            workers=workers,
            protocol=protocol,
            callback=self._callback,
            through_broker=through_broker,
        )

        self._rpc_server = weakref.ref(server)

        server.run()

    def init(self) -> ServiceInterface:
        """
        Initialize the protocol.

        :return: Initialized protocol.
        """

        service = self._service_class()
        protocol: RPCProtocol[ORJSONSerializer] | None = getattr(
            service, "protocol", None
        )

        if not protocol:
            protocol = RPCProtocol(ORJSONSerializer())
            setattr(service, "protocol", protocol)

        self._service = service

        return service

    def stop(self) -> None:
        """
        Stop the service.
        """
        if not self._service or not self._rpc_server:
            raise ContainerStopped("Container is not running")

        if self._rpc_server:
            server = self._rpc_server()

            if server:
                server.stop()

        for server_ref in self._event_servers:
            event_server = server_ref()

            if event_server:
                event_server.stop()

    def subscribe(
        self,
        host: str,
        port: int,
        protocol: ProtocolType = TCP,
        workers: int = 1,
        is_debug: bool = False,
        through_broker: bool = False,
    ) -> None:
        """
        Subscribe the service to events.

        :param host: Subscription host.
        :param port: Subscription port.
        :param protocol: Subscription protocol.
        :param workers: Number of worker threads.
        :param is_debug: Debug flag.
        :param through_broker: Use broker or not.
        """
        assert self._service, "Service is not initialized"

        services = [
            service
            for service in self._service.__class__.__dict__.values()
            if isinstance(service, ServiceProxy)
        ]

        service_publishers = {
            service._name: (service._event_host, service._event_port)  # type: ignore  # noqa
            for service in services
            if service._event_host and service._event_port  # type: ignore  # noqa
        }

        for publisher_name in service_publishers.keys():
            topics = [
                ":".join(key)
                for key in _REGISTERED_EVENT_HANDLERS
                if key[0] == publisher_name
            ]

            if not topics:
                continue

            server = ZeroMQSubscribeServer(
                host=host,
                port=port,
                topics=topics,
                workers=workers,
                protocol=protocol,
                callback=self._callback_event,  # type: ignore
                is_debug=is_debug,
                through_broker=through_broker,
            )

            self._event_servers.append(weakref.ref(server))

            Greenlet(server.run).start()

    def _callback(self, data: bytes) -> bytes | None:
        """
        Internal callback for RPC calls.

        :param data: Incoming data.
        :return: Response data.
        """
        if not self._service:
            logger.warning("Service is not initialized")
            return None

        (
            method,
            args,
            kwargs,
        ) = self._service.protocol.parse_call(data)
        full_method_name = f"{self._service.__class__.__name__}.{method}"

        if full_method_name not in _REGISTERED_METHODS:
            return None

        _method = getattr(self._service, method)

        try:
            validate_or_ignore(_method, *args, **kwargs)
            result = _method(*args, **kwargs)
        except Exception as e:
            error_callback = self._error_callback()
            result = error_callback.handle_exception(e)

        return self._service.protocol.build_response(result=result)

    def _callback_event(self, topic: bytes, payload: bytes) -> None:
        """
        Internal callback for event subscription.

        :param topic: Event topic.
        :param payload: Event data.
        """

        if not self._service:
            logger.warning("Service is not initialized")
            return None

        service_name, string_topic = topic.decode().split(":")
        key = (service_name, string_topic)

        msg = self._service.protocol.parse_event(payload)

        if key not in _REGISTERED_EVENT_HANDLERS.keys():
            return None

        _REGISTERED_EVENT_HANDLERS[key](self._service, msg)


class SingletonMeta(type, Generic[T]):
    _instances: dict[Type[T], T] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ContainerRunner(Greenlet, metaclass=SingletonMeta):
    """
    Container runner for running the containers
    """

    LOOP_WAIT_TIME = 1
    DELAY_BEFORE_START = 1

    def __init__(
        self,
        is_document_server: bool = True,
        host: str = "127.0.0.1",
        port: int = 8081,
        output_dir: str = ".docs",
    ) -> None:
        Greenlet.__init__(self)
        self._is_document_server = is_document_server
        self._host = host
        self._port = port
        self._output_dir = output_dir
        self._containers: dict[str, dict[str, Any]] = {}
        self._workers: list[Greenlet] = []

    def register(
        self, name: str, container: Container, *args: List[Any], **kwargs: Any
    ) -> None:
        """
        Register container
        """
        self._containers[name] = {
            "container": container,
            "args": args,
            "kwargs": kwargs,
        }

    def _run(self) -> None:
        """
        Run all registered containers
        """

        docs_paths: list[str | Path] = []

        for name, container in self._containers.items():
            worker = Greenlet(
                run=container["container"].run,
                *container["args"],
                **container["kwargs"],
            )
            worker.start()
            self._workers.append(worker)

            if self._is_document_server:
                docs_paths.extend(
                    get_paths(
                        container["container"]._service_class.__name__
                    )
                )

        if self._is_document_server:
            thread = Greenlet(
                generate_docs_for_service, docs_paths,
                output_dir=self._output_dir
            )
            thread.start()

            doc_server = Greenlet(
                run=start_docs_server,
                **dict(modules=docs_paths, host=self._host, port=self._port),
            )
            logger.info(f"Starting docs server on {self._host}:{self._port}")
            doc_server.start()

        while True:
            gevent.sleep(self.LOOP_WAIT_TIME)
            for worker in self._workers:
                if worker.dead and not worker.successful():
                    self._clear_worker(worker)
                    self._restart_worker(worker)

            if not self._workers:
                break

    def start(self) -> None:
        """
        Start the containers
        """
        self._run()

    def _clear_worker(self, worker: Greenlet) -> None:
        """
        Clear the worker
        """
        worker.kill()
        self._workers.remove(worker)
        logger.info(f"Worker {worker} is dead")

    def _restart_worker(self, worker: Greenlet) -> None:
        """
        Restart the worker
        """
        worker = Greenlet(run=worker.run, *worker.args, **worker.kwargs)
        worker.start()
        self._workers.append(worker)
        logger.info(f"Worker {worker} is restarted")
