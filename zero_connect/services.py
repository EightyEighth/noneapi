from typing import Protocol, runtime_checkable, TypeVar


_T = TypeVar("_T", covariant=True)


@runtime_checkable
class ServiceInterface(Protocol[_T]):
    """
     Protocol defining the service interface.

     :var name: Name of the service.
     :type name: str
    """
    name: str
