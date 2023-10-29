from typing import Protocol, runtime_checkable

from .protocols import RPCProtocol


@runtime_checkable
class ServiceInterface(Protocol):
    """
    Protocol defining the service interface.

    :var name: Name of the service.
    :type name: str
    """

    name: str
    protocol: RPCProtocol
