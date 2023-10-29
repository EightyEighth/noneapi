from typing import Callable

import zmq.green as zmq
from loguru import logger

from .transports import TCP, ProtocolType


class ZeroMQRPCServer:
    """
    A ZeroMQ based RPC server with multithreading support.

    :param host: The host to bind the server.
    :type host: str

    :param port: The port to bind the server.
    :type port: int

    :param callback: The function to process the incoming messages.
    :type callback: Callable[[bytes], bytes]

    :param protocol: The communication protocol. Defaults to TCP.
    :type protocol: PROTOCOLS, optional

    :param workers: The number of worker threads. Defaults to 1.
    :type workers: int, optional
    """

    def __init__(
        self,
        host: str,
        port: int,
        callback: Callable[[bytes], bytes | None],
        protocol: ProtocolType = TCP,
        workers: int = 1,
        through_broker: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._callback = callback
        self._protocol = protocol
        self._workers = workers
        self._through_broker = through_broker
        self._is_active = False

    def run(self) -> None:
        """
        Start the RPC server and listen for incoming requests.
        """
        url_client = f"{self._protocol}://{self._host}:{self._port}"

        logger.info(
            f"Starting ZeroMQ RPC server on "
            f"{self._protocol}://{self._host}:{self._port}"
        )

        self._start_worker(url_client, self._callback)

    def stop(self) -> None:
        """
        Stop the RPC server.
        """
        self._is_active = False

    def _start_worker(self, url_worker: str, callback: Callable) -> None:
        """
        Worker function to process incoming messages.

        :param url_worker: The worker URL.
        :type url_worker: str

        :param callback: The function to process the messages.
        :type callback: Callable
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(url_worker)

        self._is_active = True

        while self._is_active:
            message = socket.recv()
            result: bytes | None = callback(message)
            if result:
                socket.send(result)

        socket.close()
        context.term()


class ZeroMQSubscribeServer:
    """
    A ZeroMQ based Subscription server with multithreading support.

    :param host: The host to connect to.
    :type host: str

    :param port: The port to connect to.
    :type port: int

    :param callback: The function to process the incoming topic and messages.
    :type callback: Callable[[bytes, bytes], bytes]

    :param topics: A list of topics to subscribe to.
    :type topics: list[str]

    :param protocol: The communication protocol. Defaults to TCP.
    :type protocol: PROTOCOLS, optional

    :param workers: The number of worker threads. Defaults to 1.
    :type workers: int, optional

    :param is_debug: Debug flag.
    :type is_debug: bool, optional

    :param through_broker: Use broker or not.
    :type through_broker: bool, optional
    """

    def __init__(
        self,
        host: str,
        port: int,
        callback: Callable[[bytes, bytes], bytes],
        topics: list[str],
        protocol: ProtocolType = TCP,
        workers: int = 1,
        is_debug: bool = False,
        through_broker: bool = False,
    ) -> None:
        self._host = host
        self._port = port
        self._callback = callback
        self._protocol = protocol
        self._workers = workers
        self._topics = topics
        self._through_broker = through_broker
        self._is_active = False

    def run(self) -> None:
        """
        Start the subscription server and listen for incoming topics and
        messages.
        """

        context = zmq.Context.instance()
        socket = context.socket(zmq.SUB)

        for topic in self._topics:
            socket.setsockopt(zmq.SUBSCRIBE, topic.encode())

        socket.connect(f"{self._protocol}://{self._host}:{self._port}")

        self._is_active = True

        while self._is_active:
            _topic, message = socket.recv_multipart()
            result: bytes | None = self._callback(_topic, message)
            if result:
                socket.send(result)

    def stop(self) -> None:
        """
        Stop the subscription server.
        """
        self._is_active = False
