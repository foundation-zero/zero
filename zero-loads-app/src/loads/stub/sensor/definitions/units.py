from dataclasses import dataclass
from typing import Annotated, Any, Dict, TypeAlias, get_args, get_origin, get_type_hints

from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
)

from .util import hyphenize


# Unit definition
@dataclass(frozen=True)
class Unit:
    unit: str


# Unit definition
RelativePosition: TypeAlias = Annotated[float, Field(ge=0, lt=1), Unit(unit="%")]
Load: TypeAlias = Annotated[float, Field(ge=0), Unit(unit="ton")]


# Component metadata
class ComponentMeta(BaseModel):
    name: str


def component_meta(*args, **kwargs):
    return Field(json_schema_extra=ComponentMeta(*args, **kwargs).model_dump())


class LoadsModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )

    @classmethod
    def gen_config(cls, interval: int = 1) -> list[dict]:
        """Generate configuration for data generation."""
        hints = get_type_hints(cls, include_extras=True)
        config = []

        for component, value_definition in hints.items():
            base_type, meta = cls._unwrap_annotated(value_definition)

            if isinstance(base_type, type) and issubclass(base_type, LoadsModel):
                values = {}
                for field_name, field_info in base_type.model_fields.items():
                    values[field_name] = cls.gen_single_value(field_info.annotation, field_info.metadata)

                config.append(
                    {
                        "topic": component,
                        "interval": interval,
                        "values": values,
                    }
                )
            else:
                config.append(
                    {
                        "topic": component,
                        "interval": interval,
                        "values": {component: cls.gen_single_value(base_type, meta)},
                    }
                )

        return config

    @classmethod
    def gen_single_value(cls, base_type, meta):
        constraints = cls._extract_constraints(meta)

        lower = constraints.get("ge", constraints.get("gt", 0))
        upper = constraints.get("le", constraints.get("lt", 100))
        if lower >= upper:
            return [cls._type_name(base_type), lower, upper]
        else:
            return cls._type_name(base_type)

    @staticmethod
    def _extract_constraints(meta: list[Any]) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {}
        for m in meta:
            for attr in ("gt", "ge", "lt", "le"):
                if hasattr(m, attr):
                    constraints[attr] = getattr(m, attr)

        print(constraints)
        return constraints

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
