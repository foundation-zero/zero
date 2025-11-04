from dataclasses import dataclass
from typing import Annotated, Any, Dict, TypeAlias, get_args, get_origin, get_type_hints

from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic.fields import FieldInfo

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


def _unwrap_annotated(tp: Any) -> tuple[type | Any, list[Any]]:
    if get_origin(tp) is Annotated:
        args = get_args(tp)
        return args[0], list(args[1:])
    return tp, []


def _type_name(tp: Any) -> str:
    try:
        return tp.__name__
    except AttributeError:
        return str(tp)


def _extract_constraints(meta: list[Any]) -> Dict[str, Any]:
    constraints: Dict[str, Any] = {}
    for m in meta:
        if isinstance(m, FieldInfo):
            for name in ("gt", "ge", "lt", "le"):
                val = getattr(m, name, None)
                if val is not None:
                    constraints[name] = val
    return constraints


class LoadsModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=hyphenize,
        )
    )

    @classmethod
    def gen_config(cls, interval: int = 1) -> dict:
        """Generate configuration for data generation."""
        hints = get_type_hints(cls, include_extras=True)
        values: Dict[str, list] = {}

        print(hints)
        for component, value_definition in hints.items():
            base_type, meta = _unwrap_annotated(value_definition)
            print(base_type, meta)
            constraints = _extract_constraints(meta)
            lower = constraints.get("ge", constraints.get("gt", 0))
            upper = constraints.get("le", constraints.get("lt", 100))
            values[component] = [_type_name(base_type), lower, upper]

        # print(values)
        return {"topic": component, "interval": interval, "values": values}
