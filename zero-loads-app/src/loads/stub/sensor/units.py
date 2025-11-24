from dataclasses import dataclass
from typing import Annotated, Any, Dict, TypeAlias, get_args, get_origin

import generator.gen as gen
from generator import Generator, GeneratorConfig, create_generator
from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic.fields import FieldInfo

from .util import hyphenize

TOPIC_PREFIX: str = "sail-systems"


# Unit definition
@dataclass(frozen=True)
class Unit:
    unit: str


# Unit definition
Position: TypeAlias = Annotated[float, Field(ge=0, lt=1), Unit(unit="mm")]
RelativePosition: TypeAlias = Annotated[float, Field(ge=0, lt=1), Unit(unit="%")]
Load: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="ton")]
Torque: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="Nm")]
RotationalSpeed: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="rpm")]
Temperature: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="°C")]


# Component metadata
class ComponentMeta(BaseModel):
    topic: str


def component_meta(*args, **kwargs):
    return Field(json_schema_extra=ComponentMeta(*args, **kwargs).model_dump())


class LoadsModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )

    @classmethod
    def gen_config(cls, interval: int = 10) -> list[GeneratorConfig]:
        """Generate configuration for data generation."""
        config = []

        for component, field_info in cls.model_fields.items():
            base_type = field_info.annotation
            topic = f"{TOPIC_PREFIX}/{cls._extract_topic(field_info) or component}"

            if isinstance(base_type, type) and issubclass(base_type, LoadsModel):
                values = {}
                for sub_field_name, sub_field_info in base_type.model_fields.items():
                    values[sub_field_name] = cls._create_generator(sub_field_info.annotation, sub_field_info.metadata)

                config.append(GeneratorConfig(topic=topic, interval=interval, values=values))
            else:
                config.append(
                    GeneratorConfig(
                        topic=topic,
                        interval=interval,
                        values={component: cls._create_generator(base_type, field_info.metadata)},
                    )
                )

        return config

    @classmethod
    def _extract_topic(cls, field_info: FieldInfo) -> str | None:
        """Extract the topic from the metadata."""
        if hasattr(field_info, "json_schema_extra"):
            extra = getattr(field_info, "json_schema_extra", {})
            if isinstance(extra, dict) and "topic" in extra:
                return extra["topic"]

        return None

    @classmethod
    def _create_generator(cls, base_type: Any, meta: list[Any]) -> Generator:
        """Create a data generator based on the type and constraints."""
        constraints = cls._extract_constraints(meta)

        lower = constraints.get("ge", constraints.get("gt", 0))
        upper = constraints.get("le", constraints.get("lt", 100))

        type = gen.validate_type(cls._type_name(base_type))
        return create_generator(type, lt=lower, gt=upper)

    @staticmethod
    def _extract_constraints(meta: list[Any]) -> Dict[str, Any]:
        return {attr: getattr(m, attr) for m in meta for attr in ("gt", "ge", "lt", "le") if hasattr(m, attr)}

    @staticmethod
    def _unwrap_annotated(tp: Any) -> tuple[type | Any, list[Any]]:
        if get_origin(tp) is Annotated:
            args = get_args(tp)
            return args[0], list(args[1:])
        return tp, []

    @staticmethod
    def _type_name(tp: Any) -> str:
        try:
            return tp.__name__
        except AttributeError:
            return str(tp)
