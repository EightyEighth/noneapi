# NoneAPI (alpha)

This mini-framework (RPC like) allows you to easily build microservices that can communicate with each other like modules in a monolith. This project was inspired by the [nameko framework](https://github.com/nameko/nameko).

## 🎯 Philosophy

> Just call your microservices like you would any other function.

The goal of this framework is to simplify microservice interactions, eliminating the need for middleware. To send parameters like 'user' or anything else, include them in the method arguments. This ensures clarity in the data sent to and received from the service. 


Performance:
~ 35000 requests per second on one worker

---

## 📜 Table of Contents

1. [Philosophy](#philosophy)
2. [Why Not Nameko or Others?](#why-not-nameko-or-others)
3. [Features](#features)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Tutorials](#tutorials)
7. [API Reference](#api-reference)
8. [FAQ](#faq)
9. [Changelog](#changelog)
10. [Contributing](#contributing)
11. [License](#license)

---

## ❓ Why Not Nameko or Others?

We leverage [ZeroMQ](https://zeromq.org/) to eliminate broker intermediaries.

---

## 🌟 Features

- Fast and reliable with ZeroMQ
- Easy integration
- Decoupled architecture
- Event-driven design
- Multi-subscriber support
- No broker needed
- Zero learning curve
- Auto-generated documentation

---

## ⚙️ Installation

Install via pip:

```bash
pip install noneapi
````

## Quick Start
Here's how to get started with MyLibrary:

1. **Install**: 
    ```bash
    pip install noneapi
    ```

2. **Create order service**: 
    ```python
    # services.py
    from noneapi import rpc
    from noneapi import Container, ContainerRunner
    from .db import order_session
    from .models import Order
   
   
    class OrderService:
   
        name = 'order_service'
   
        @rpc
        def get_order(self, order_id: int):
            order = order_session.query(Order).get(order_id)
            if not order:
                return None
   
            return order.to_dict()
   
        @rpc
        def save_order(self, order: dict):
            order = Order(**order)
            order_session.add(order)
            order_session.commit()
            return order.to_dict()
   
    # containers.py
    container = Container(OrderService)
    runner = ContainerRunner(is_document_server=False)
    runner.register("order",container, host="*", port=5555)
   
   
   # app.py
    from .containers import runner
   
    if __name__ == '__main__':
        runner.run()
    ```
3. **Use by client**: 
    ```python
   from noneapi import ClusterProxy
   from exceptions import RemoteError
   from .usecases import OrderUsecase
   config = [
        {
            "name": "order_service",
            "host": "127.0.0.1",
            "port": 5555

        }
   ]
   
   ...  # some other code
   
   with ClusterProxy(config) as cluster:
        order = cluster.order_service.get_order(1)
        order_usecase = OrderUsecase(order)
        updated_order = order_usecase.do_something()
        cluster.order_service.save_order.async_call(updated_order)
   
        ... # A lot of code
        
        try:
            result = cluster.order_service.save_order.result()
        except RemoteError as e:
            print(e)
            # do something
        else:
            # do something
   
        
    ```

---

## Tutorials

1. **Install**: 
    ```bash
    pip install noneapi
    ```

2. **RPC**: 
    ```python
    from noneapi import rpc
   
   
    class OrderService:
        name = 'order_service'
   
        @rpc
        def add_order(self, order: dict):
            # some code
            return order

   ```
    In this scenario, any service using `noneapi` can communicate directly with this service by invoking the `add_order` method.

    - **`name`**: Identifier for the service. This is used for service discovery and is mandatory for each service.

    - **`@rpc`**: A decorator that makes the method available for remote procedure calls. Only methods tagged with this decorator can be remotely invoked.


3. **Event handling**

   ```python
   
   from noneapi import rpc, event_handler, EventDispatcher, ServiceProxy
   
   class OrderService:
        name = 'order_service'
        payment_service = ServiceProxy(event_host="127.0.0.1", event_port=5556)
        
   
        @rpc
        def add_order(self, order: dict):
            # some code
            return order
        
        @event_handler(service_name='payment_service', topic='payment_success')
        def on_payment_success(self, order_id: int):
                # some code
                return order_id
   
   
   
   class PaymentService:
        name = 'payment_service'
        dispatch = EventDispatcher(port=5556, host='*')
        
        @rpc
        def pay(self, order_id: int):
            self.dispatch('payment_success', order_id)
            return order_id
   ```
    In this setup, we add an `event_handler` to `OrderService` and establish `PaymentService` with an `EventDispatcher`. Whenever a 'payment_success' event is dispatched by `PaymentService`, the `on_payment_success` method in `OrderService` will be triggered. Essentially, this mimics the publish/subscribe (pub/sub) pattern where you can subscribe to different topics.

    - **`@event_handler`**: A decorator used for methods that will be invoked when a specific event is dispatched. Only methods with this decorator respond to the event.
    
    - **`EventDispatcher`**: A class responsible for sending out events to all services that are listening via `event_handler`. The parameters `port` and `host` specify where the `EventDispatcher` will be available for dispatching events.
    
    - **`ServiceProxy`**: A class offering access to remote services. The optional parameters `event_host` and `event_port` define where the service listens for events. Because there are no message brokers, it's essential to know the publisher's location for event reception.


4.  **Containers**: 
    ```python
    from noneapi import Container, ContainerRunner
    from .services import OrderService
   
    container = Container(OrderService)
    runner = ContainerRunner(is_document_server=False)
    runner.register(container, host="*", port=5555)
    runner.run()
    ```
    In this case, we create a container with one service and run it.
    
    - **Container**: A class that holds all services that will be available for remote calls.
      
    - **ContainerRunner**: A class responsible for running all registered containers and facilitating service discovery.
    
    - **`register`**: A method to register a container within the runner. It accepts `container`, `host`, and `port` as arguments. Both `host` and `port` are optional. By default, `host` is set to `"*"` and `port` to `5555`.
    
    - **`run`**: A method that starts all the containers and the documentation service if applicable.


5. **ClusterProxy**: 
    ```python
    from noneapi import ClusterProxy
    from exceptions import RemoteError
   
    config = [
        {
            "name": "order_service",
            "host": "127.0.0.1",
            "port": 5555,
        }
   ]
   
   
   def main():
        with ClusterProxy(config) as cluster:
            order = cluster.order_service.add_order({"id": 1})
      
   ```
    In this example, we create a `ClusterProxy` with a configuration that points to the `order_service`. The `ClusterProxy` is a context manager that allows us to access the service via `cluster.order_service`. The `add_order` method is invoked with a dictionary as an argument.

    - **`ClusterProxy`**: A class that allows access to remote services. It accepts a configuration as an argument. The configuration is a list of dictionaries with the following keys: `name`, `host`, and `port`. The `name` is the identifier of the service. The `host` and `port` are the location of the service. Both `host` and `port` are optional. By default, `host` is set to `"

   
6. **Async call**: 
    ```python
    from noneapi import ClusterProxy
    from exceptions import RemoteError
   
    config = [
        {
            "name": "order_service",
            "host": "127.0.0.1",
               "port": 5555,
        }
    ]
   
    def main():
        with ClusterProxy(config) as cluster:
            cluster.order_service.add_order.async_call({"id": 1})
            # a lot of code
            try:
                result = cluster.order_service.result()
            except RemoteError as e:
                print(e)
                # do something
            else:
                # do something
   
    ```
    In this example, we create a `ClusterProxy` with a configuration that points to the `order_service`. The `ClusterProxy` is a context manager that allows us to access the service via `cluster.order_service` like in the previous example but with `async_call` that allow us to call method asynchronously. The `result` method is invoked without arguments and returned result.


7. **Validation with pydantic**
    ```python
    from noneapi import rpc 
    
   class OrderService:
         name = 'order_service'
   
         @rpc
         def add_order(self, order_id: int, name: str):
             # some code
             return order
   
    ```
    In this scenario, we can validate input. NoneAPI will validate input data and return error if data is not valid.
    Only `int`, `float`, `str`, `bool` and `None` types are supported.
    
    If you want validate complex data, you can use `pydantic` models for that:
    ```python
    from noneapi import rpc
    from pydantic import BaseModel
   
    class Order(BaseModel):
        id: int
        name: str
    
    class OrderService:
        name = 'order_service'
    
        @rpc
        def add_order(self, order: Order):
            # some code
            return order
   ```
   In this case NoneAPI will validate input data with `Order` model and return error if data is not valid.


8. **Docs**
    ```python
    from noneapi import Container, ContainerRunner
    from .services import OrderService
   
    container = Container(OrderService)
    runner = ContainerRunner(is_document_server=True)
    runner.register(container, host="*", port=5555)
    runner.run()
    ```
   
    In this case, we create a container with one service and run it with documentation server.
    It will be always available on `http://localhost:8081/`


9.  **Custom serialization**
    ```python
    from noneapi import BaseSerializer
    from noneapi import Protocol
    from msgpack import packb, unpackb
    
    class MsgPackSerializer(BaseSerializer):
        def _serialize(self, data: dict) -> bytes:
            return packb(data)
    
        def _deserialize(self, data: bytes) -> dict:
            return unpackb(data)

    class OrderService:
        name = 'order_service'
        protocol: Protocol[MsgPackSerializer] = Protocol(MsgPackSerializer())
    
        @rpc
        def add_order(self, order: dict):
            # some code
            return order
    ```
    In this case, we're creating a custom serializer for the service, applicable to all its methods. By default, NoneAPI employs a clean JSON serializer, powered by the ultra-fast orjson library. Feel free to use any serializer—just inherit from BaseSerializer and pass it to the Protocol class.
    
    _IMPORTANT_: If you change the serializer, you must change it on all services that will communicate with each other. Otherwise, you will get an error.
---

## Changelog

### Version 0.1.3 (2023-10-29)(alpha)
- Initial release

### Version 0.1.4 (2023-10-29)(alpha)
- Add custom serializer 
- Add custom serializer documentation


---

## Contributing

To contribute, please fork the repository, make your changes, and submit a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.

## If you like this project, please give it a star! 🌟