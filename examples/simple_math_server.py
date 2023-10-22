from zero_connect.services import ServiceInterface
from zero_connect.rpc import rpc
from pydantic import BaseModel

__all__ = ["ServiceMath", "Calculate"]


class Calculate(BaseModel):
    a: int
    b: int
    method: str


class ServiceMath(ServiceInterface):
    name = "math_service"

    @rpc
    def sum(self, a: int, b: int) -> int:
        return a + b

    @rpc
    def div(self, a: int, b: int) -> int:
        return a // b

    @rpc
    def mul(self, a: int, b: int) -> int:
        return a * b

    @rpc
    def calculate(self, c: Calculate) -> int:
        method = getattr(self, c.method)
        return method(c.a, c.b)
