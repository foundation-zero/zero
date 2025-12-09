from asyncio import Future
from typing import Any

from pydantic import TypeAdapter
from thrs.input_output.base import ThrsModel


class ModelBuilder[T: ThrsModel]:
    def __init__(self, cls: type[T]):
        self._cls = cls
        self._value: T | None = None
        self._values: dict[str, Any] = {}
        self._fields: dict[str, TypeAdapter] = {
            field_name: TypeAdapter(field.annotation)
            for field_name, field in cls.model_fields.items()
        }
        self._complete_model = Future()

    def input(self, field: str, json: str | bytes):
        value = self._fields[field].validate_json(json)
        if self._value is not None:
            setattr(self._value, field, value)
        else:
            self._values[field] = value
            if set(self._values.keys()) == set(self._cls.model_fields.keys()):
                self._value = self._cls(**self._values)
                self._complete_model.set_result(self._value)

    def result(self) -> T | None:
        return self._value

    async def wait_for_result(self) -> T:
        return await self._complete_model
