from zero_connect import ServiceProxy


def client():
    class Service:
        name = "test_service"
        service_a = ServiceProxy(host="127.0.0.1", port=5000)

    service = Service()
    print(f"Sum operation: {service.service_a.sum(1, 2)}")
    print(f"Div operation: {service.service_a.div(1, 2)}")
    print(f"Mul operation: {service.service_a.mul(1, 2)}")


if __name__ == "__main__":
    client()
