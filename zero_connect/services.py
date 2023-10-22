from typing import Protocol, runtime_checkable, TypeVar

from .protocols import RPCProtocol
from .transports import BaseTransport

from .serializers import BaseSerializer


_T = TypeVar("_T")


@runtime_checkable
class ServiceInterface(Protocol[_T]):
    """
     Protocol defining the service interface.

     :var name: Name of the service.
     :type name: str
    """
    name: str
