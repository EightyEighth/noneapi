import json
from abc import ABC, abstractmethod

import orjson


class BaseSerializer(ABC):
    def serialize(self, data: dict) -> bytes:
        return self._serialize(data)

    def deserialize(self, data: bytes) -> dict:
        return self._deserialize(data)

    @abstractmethod
    def _serialize(self, data: dict) -> bytes:
        ...

    @abstractmethod
    def _deserialize(self, data: bytes) -> dict:
        ...


class JSONSerializer(BaseSerializer):
    def _serialize(self, data: dict) -> bytes:
        return json.dumps(data).encode()

    def _deserialize(self, data: bytes) -> dict:
        return json.loads(data.decode())


class ORJSONSerializer(BaseSerializer):
    def _serialize(self, data: dict) -> bytes:
        return orjson.dumps(data)

    def _deserialize(self, data: bytes) -> dict:
        return orjson.loads(data)
