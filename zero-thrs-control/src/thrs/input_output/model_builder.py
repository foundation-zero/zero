from abc import ABC, abstractmethod
from asyncio import Future, gather
from typing import Any

from pydantic import TypeAdapter
from thrs.input_output.base import ThrsModel, NestedValues
from thrs.utils.string import dash_to_snake


class ModelBuilder[T](ABC):
    @abstractmethod
    def input(self, topic: str, json: str | bytes): ...

    @abstractmethod
    def result(self) -> T | None: ...

    @abstractmethod
    async def wait_for_result(self) -> T: ...


class PartialModelBuilder[T: ThrsModel](ModelBuilder[T]):
    def __init__(self, cls: type[T]):
        self._cls = cls
        self._value: T | None = None
        self._values: dict[str, Any] = {}
        self._fields: dict[str, TypeAdapter] = {
            field_name: TypeAdapter(field.annotation)
            for field_name, field in cls.model_fields.items()
        }
        self._complete_model = Future()

    def input(self, topic: str, json: str | bytes):
        field = dash_to_snake(topic)
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


class NestedModelBuilder(ModelBuilder[NestedValues]):
    def __init__(self, clss: dict[str, type[ThrsModel]]):
        self._model_builders: dict[str, ModelBuilder[ThrsModel]] = {
            name: PartialModelBuilder(cls) for name, cls in clss.items()
        }

    def input(self, topic: str, json: str | bytes):
        module_name, field, *rest = topic.split("/")
        self._model_builders[module_name].input(field, json)

    def result(self) -> NestedValues | None:
        values: dict[str, ThrsModel] = {
            name: res
            for name, builder in self._model_builders.items()
            if (res := builder.result())
        }
        if set(values.keys()) == set(self._model_builders.keys()):
            return NestedValues(values=values)
        else:
            return None

    async def wait_for_result(self) -> NestedValues:
        results = await gather(
            *(builder.wait_for_result() for builder in self._model_builders.values())
        )
        return NestedValues(dict(zip(self._model_builders.keys(), results)))
