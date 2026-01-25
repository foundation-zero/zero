from typing import Any, Callable, ClassVar, get_type_hints

import generator.gen as gen
from generator import Generator, GeneratorConfig, create_generator
from generator.base import JSONGenerator
from pydantic import AliasGenerator, BaseModel, ConfigDict

from loads.sensors.units import ScalingMeta, VariableMeta

from .util import hyphenize


class LoadsModel(BaseModel):
    """
    Pydantic model that supports generation of mock data
    and customization of the underlaying transport format of that mocked data.

    Suggestion: move both capabilities to zero-generator for better SOLID adherence.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        ),
        extra="ignore",
    )

    TOPIC: ClassVar[str]

    @classmethod
    def make_generator(cls):
        return JSONGenerator(
            {
                str(
                    field_info.validation_alias
                    if field_info.validation_alias
                    else field
                ): cls._create_generator(field_info.annotation, field_info.metadata)
                for field, field_info in cls.model_fields.items()
            },
        )

    @classmethod
    def gen_config(cls, interval: int = 10) -> GeneratorConfig:
        """Generate configuration for data generation."""
        return GeneratorConfig(
            topic=cls.TOPIC,
            interval=interval,
            generator=cls.make_generator(),
        )

    @classmethod
    def _create_generator(cls, base_type: Any, meta: list[Any]) -> Generator:
        """Create a data generator based on the type and constraints."""

        minimum = cls.extract_minimum(meta)
        maximum = cls.extract_maximum(meta)

        if inverse_conversion := cls._extract_inverse_scaling_conversion(meta):
            type = gen.validate_type(
                cls._type_name(get_type_hints(inverse_conversion).get("return"))
            )
            lt = inverse_conversion(minimum) if minimum else 0
            gt = inverse_conversion(maximum) if maximum else 100
        else:
            type = gen.validate_type(cls._type_name(base_type))
            lt = minimum if minimum else 0
            gt = maximum if maximum else 100

        if type in ("int", "float"):
            return create_generator(type, lt=lt, gt=gt)
        else:
            return create_generator(type)

    @staticmethod
    def extract_minimum(meta: list[Any]) -> float | None:
        return next(
            (
                getattr(m, attr)
                for m in meta
                for attr in ("ge", "gt")
                if hasattr(m, attr)
            ),
            None,
        )

    @staticmethod
    def extract_maximum(meta: list[Any]) -> float | None:
        return next(
            (
                getattr(m, attr)
                for m in meta
                for attr in ("lt", "le")
                if hasattr(m, attr)
            ),
            None,
        )

    @staticmethod
    def _extract_inverse_scaling_conversion(meta: list[Any]) -> Callable | None:
        for m in meta:
            if isinstance(m, ScalingMeta):
                return m.inverse_conversion
        return None

    @staticmethod
    def extract_variable_meta(meta: list[Any]) -> VariableMeta | None:
        for m in meta:
            if isinstance(m, VariableMeta):
                return m
        return None

    @staticmethod
    def extract_scaling_conversion(meta: list[Any]) -> Callable | None:
        for m in meta:
            if isinstance(m, ScalingMeta):
                return m.conversion
        return None

    @staticmethod
    def _type_name(tp: Any) -> str:
        try:
            return tp.__name__
        except AttributeError:
            return str(tp)

    @classmethod
    def parse_message_payload(cls, payload: str | bytes):
        return cls.model_validate_json(payload)


class LoadsBytesModel(LoadsModel):
    """
    Subclass that expects single value encoded as string in the transport format.
    The value will be exposed as `value` attribute of the instance.
    """

    @classmethod
    def make_generator(cls):
        field_info = cls.model_fields["value"]  # Only one field is expected
        return cls._create_generator(field_info.annotation, field_info.metadata)

    @classmethod
    def parse_message_payload(cls, payload: str | bytes):
        cast = cls.model_fields["value"].annotation
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        # This is not expected to work with all types e.g. `datetime.date` will break
        return cls.model_validate(
            {"value": cast(payload) if cast is not None else payload}
        )
