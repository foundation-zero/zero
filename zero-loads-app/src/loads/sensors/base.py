from typing import Any, ClassVar, Dict

import generator.gen as gen
from generator import Generator, GeneratorConfig, create_generator
from pydantic import AliasGenerator, BaseModel, ConfigDict

from .util import hyphenize


class LoadsModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        ),
        extra="ignore",
    )

    TOPIC: ClassVar[str]

    @classmethod
    def gen_config(cls, interval: int = 10) -> GeneratorConfig:
        """Generate configuration for data generation."""

        return GeneratorConfig(
            topic=cls.TOPIC,
            interval=interval,
            values={
                str(
                    field_info.validation_alias
                    if field_info.validation_alias
                    else field
                ): cls._create_generator(field_info.annotation, field_info.metadata)
                for field, field_info in cls.model_fields.items()
            },
        )

    @classmethod
    def _create_generator(cls, base_type: Any, meta: list[Any]) -> Generator:
        """Create a data generator based on the type and constraints."""
        constraints = cls._extract_constraints(meta)

        lower = constraints.get("ge", constraints.get("gt", 0))
        upper = constraints.get("le", constraints.get("lt", 100))

        type = gen.validate_type(cls._type_name(base_type))
        if type in ("int", "float"):
            return create_generator(type, lt=lower, gt=upper)
        else:
            return create_generator(type)

    @staticmethod
    def _extract_constraints(meta: list[Any]) -> Dict[str, Any]:
        return {
            attr: getattr(m, attr)
            for m in meta
            for attr in ("gt", "ge", "lt", "le")
            if hasattr(m, attr)
        }

    @staticmethod
    def _type_name(tp: Any) -> str:
        try:
            return tp.__name__
        except AttributeError:
            return str(tp)
