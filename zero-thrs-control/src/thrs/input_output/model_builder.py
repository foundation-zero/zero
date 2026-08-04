import logging
from abc import ABC, abstractmethod
from asyncio import Future
from typing import Any

from pydantic import TypeAdapter, ValidationError

from thrs.input_output.base import ThrsValues


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
        try:
            self._value = self._cls(**self._values)
        except ValidationError as e:
            logging.debug(
                "Missing fields, keys: %s", list(self._values.keys()), exc_info=e
            )

        return self._value

    async def wait_for_result(self) -> T:
        return await self._complete_model
