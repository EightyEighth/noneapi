from zero_connect import rpc, Container, ContainerRunner
from pydantic import BaseModel


__all__ = ["ServiceMath", "Calculate"]


class Calculate(BaseModel):
    a: int
    b: int
    method: str


class ServiceMath:
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


if __name__ == "__main__":
    container = Container(ServiceMath)
    zero = ContainerRunner()
    zero.register(
        "math_container", container, host="*", port=5000,

    )
    zero.run()
