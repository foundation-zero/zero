from abc import ABC, abstractmethod
from asyncio import Future, gather
from collections.abc import Mapping
from typing import Any, cast

from pydantic import TypeAdapter

from thrs.input_output.base import CombinedValues, ThrsValues
from thrs.orchestration.module import ModuleClassMap


class ModelBuilder[T](ABC):
    """
    ModelBuilders is used to build instances of a class

    It accepts a class and one or more input calls. If those `input` calls give enough information
    to create a instance of that class, `result` will return an instance.

    Given more `input` calls the class will keep `result` updated.
    """

    @abstractmethod
    def input(self, field: str, json: str | bytes): ...

    @abstractmethod
    def result(self) -> T | None: ...

    @abstractmethod
    async def wait_for_result(self) -> T: ...


class PartialModelBuilder[T: ThrsValues](ModelBuilder[T]):
    """
    ModelBuilder that handles partial input.

    Each input call is expected to set one field in the model.
    """

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


class CombinedModelBuilder[T: CombinedValues](ModelBuilder[T]):
    """
    Model builder that handles multiple modules.

    It builds a ModuleClassMap instead of a single class.
    """

    def __init__(self, clss: ModuleClassMap):
        self._model_builders: Mapping[str, ModelBuilder[ThrsValues]] = {
            name: PartialModelBuilder(module_cls) for name, module_cls in clss.items()
        }

    def input(self, field: str, json: str | bytes):
        module_name, field_name, *rest = field.split("/")
        self._model_builders[module_name].input(field_name, json)

    def result(self) -> T | None:
        values: dict[str, ThrsValues] = {
            name: res
            for name, builder in self._model_builders.items()
            if (res := builder.result())
        }
        if set(values.keys()) == set(self._model_builders.keys()):
            return cast(T, CombinedValues(values=values))
        else:
            return None

    async def wait_for_result(self) -> T:
        results = await gather(
            *(builder.wait_for_result() for builder in self._model_builders.values())
        )
        return cast(T, CombinedValues(dict(zip(self._model_builders.keys(), results))))
