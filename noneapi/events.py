from typing import Any, Callable

_REGISTERED_EVENT_HANDLERS: dict[tuple[str, str], Callable] = {}


def event_handler(service_name: str, topic: str) -> Callable:
    """
    Decorator to register a function as an event handler.

    :param service_name: Name of the service the event belongs to.
    :type service_name: str

    :param topic: Topic of the event.
    :type topic: str

    :return: The original function with the event handler registered.
    :rtype: Callable
    """

    def decorator(func: Callable) -> Callable:
        key = (service_name, topic)
        if key not in _REGISTERED_EVENT_HANDLERS:
            _REGISTERED_EVENT_HANDLERS[key] = func
        return func

    return decorator


class EventDispatcher:
    """
    Dispatches events to the relevant services.

    :param host: Host where the event should be dispatched to.
    :type host: str

    :param port: Port where the event should be dispatched to.
    :type port: int
    """

    def __init__(
            self, host: str, port: int, through_broker: bool = False
    ) -> None:
        self._host = host
        self._port = port
        self._through_broker = through_broker

    def __set_name__(self, owner: Any, name: str) -> None:
        """
        Called when an owner class is created, typically used to set the
        attribute name.

        :param owner: The owning class where the descriptor is defined.
        :type owner: Any

        :param name: The name of the descriptor in the owner class.
        :type name: str
        """
        self._name = name

    def __get__(self, instance: Any, owner: Any) -> "Callable":
        """
        Retrieve the descriptor value from an instance of the owner.

        :param instance: Instance of the owning class.
        :type instance: Any

        :param owner: The owning class where the descriptor is defined.
        :type owner: Any

        :return: Callable object to dispatch the event.
        :rtype: Callable
        """
        assert instance.name, "Service name is not defined"
        self._service = instance
        return self

    def __call__(self, topic: str, payload: Any) -> None:
        """
        Dispatch the event to the relevant service.

        :param topic: Topic of the event.
        :type topic: str

        :param payload: Data payload of the event.
        :type payload: Any
        """
        key = "{}:{}".format(self._service.name, topic)
        self._service.protocol.dispatch(
            self._host, self._port, key, payload,
            through_broker=self._through_broker
        )
