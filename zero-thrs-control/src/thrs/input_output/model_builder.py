import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any

from pydantic import TypeAdapter, ValidationError

from thrs.input_output.base import ThrsValues
from thrs.input_output.definitions.wire_context import WireContext

logger = logging.getLogger(__name__)


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


class PartialModelBuilder[T: ThrsValues](ModelBuilder[T]):
    """
    ModelBuilder that handles partial input.

    Each input call is expected to set one field in the model. Given an `initial`
    model, the builder starts from it, and each input call overrides one of its
    fields.
    """

    def __init__(
        self,
        cls: type[T],
        validation_context: WireContext | None = None,
        initial: T | None = None,
    ):
        self._cls = cls
        self._validation_context = validation_context
        self._value: T | None = initial
        self._values: dict[str, Any] = {} if initial is None else dict(initial)
        self._fields: dict[str, TypeAdapter] = {
            field_name: TypeAdapter(field.annotation)
            for field_name, field in cls.model_fields.items()
            if field.annotation is not None
        }

    def input(self, field: str, json: str | bytes):
        value = self._fields[field].validate_json(
            json, context=self._validation_context
        )

        self._values[field] = value

        # Just try to create the object, we can't compare key sets because of optional values
        with suppress(ValidationError):
            self._value = self._cls(**self._values)

    def result(self) -> T | None:
        if logger.isEnabledFor(logging.DEBUG):
            try:
                self._cls(**self._values)
            except ValidationError as e:
                logger.debug(
                    "Failed creating model",
                    exc_info=e,
                )

        return self._value
