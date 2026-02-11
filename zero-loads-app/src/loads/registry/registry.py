from dataclasses import dataclass
from functools import partial
from typing import Callable, cast

from loads.sensors import at, sail_system
from loads.sensors.base import LoadsModel
from loads.util import camel_to_kebab, hyphenize


@dataclass
class VariableDefinition:
    id: str
    name: str
    topic: str
    get_actual: Callable[[LoadsModel], float | None]
    unit: str
    scale_min: float | None
    scale_max: float | None
    scale_min_label: str | None
    scale_max_label: str | None


@dataclass
class AlarmDefinition:
    id: str
    name: str
    topic: str
    get_active: Callable[[LoadsModel], bool | None]
    get_actual: Callable[[LoadsModel], float | None]
    get_threshold: Callable[[LoadsModel], float | None]
    actual_definition: VariableDefinition


def _build_sail_system_variable_definitions(
    model: type[LoadsModel],
) -> list[VariableDefinition]:
    function_id = camel_to_kebab(model.__name__)

    return [
        VariableDefinition(
            id=f"{function_id}-{hyphenize(variable_meta.name or '')}",
            name=model.field_display_name(field, field_info.metadata),
            topic=model.TOPIC,
            get_actual=partial(
                lambda field, model_instance: getattr(model_instance, field), field
            ),
            unit=cast(str, variable_meta.unit),
            scale_min=variable_meta.scale_min,
            scale_max=variable_meta.scale_max,
            scale_min_label=variable_meta.scale_min_label,
            scale_max_label=variable_meta.scale_max_label,
        )
        for field, field_info in model.model_fields.items()
        if (variable_meta := model.extract_variable_meta(field, field_info.metadata))
        and variable_meta.type == "actual"
    ]


def _lookup_variable_definition_by_id(
    variable_definitions: list[VariableDefinition], id: str
) -> VariableDefinition:
    try:
        return next((vd for vd in variable_definitions if vd.id == id))
    except StopIteration:
        raise ValueError(f"No variable definition found for id: {id}")


def _build_sail_system_alarm_definitions(
    model: type[LoadsModel],
    variable_definitions: list[VariableDefinition],
) -> list[AlarmDefinition]:
    function_id = camel_to_kebab(model.__name__)

    return [
        AlarmDefinition(
            id=f"{function_id}-alarm",
            name=model.field_display_name(field, field_info.metadata),
            topic=model.TOPIC,
            get_active=partial(
                lambda field, model_instance: getattr(model_instance, field), field
            ),
            get_actual=partial(
                lambda field, model_instance: getattr(model_instance, cast(str, field)),
                variable_meta.alarm_for_field,
            ),
            get_threshold=lambda model_instance: model_instance.relief_load,  # type: ignore[attr-defined]
            actual_definition=_lookup_variable_definition_by_id(
                variable_definitions,
                f"{function_id}-{variable_meta.alarm_for_field}",
            ),
        )
        for field, field_info in model.model_fields.items()
        if (variable_meta := model.extract_variable_meta(field, field_info.metadata))
        and variable_meta.is_alarm
    ]


SAIL_SYSTEM_MODELS: list[type[LoadsModel]] = [
    sail_system.PrimaryWinchPs,
    sail_system.PrimaryWinchSb,
    sail_system.AftWinchPs,
    sail_system.AftWinchSb,
    sail_system.BladeAdjuster,
    sail_system.BladeCunningham,
    sail_system.BladeSheetFeederPs,
    sail_system.BladeSheetFeederSb,
    sail_system.BladeTweakerPs,
    sail_system.BladeTweakerSb,
    sail_system.CodeZeroTack,
    sail_system.A2Tack,
    sail_system.StormJibTack,
    sail_system.CombinedHeadstay,
    sail_system.HeadsailLocks,
    sail_system.MainCheckstay,
    sail_system.MainCunningham,
    sail_system.MainHalyard,
    sail_system.MainOuthaul,
    sail_system.MainPreventer,
    sail_system.MainRunnerSb,
    sail_system.MainRunnerPs,
    sail_system.MainSheet,
    sail_system.MainTraveller,
    sail_system.MainVang,
    sail_system.MizzenCheckstay,
    sail_system.MizzenCunningham,
    sail_system.MizzenHalyard,
    sail_system.MizzenHeadsailLocks,
    sail_system.MizzenHeadsailTackAdjuster,
    sail_system.MizzenOuthaul,
    sail_system.MizzenPreventer,
    sail_system.MizzenRunnerPs,
    sail_system.MizzenRunnerSb,
    sail_system.MizzenSheet,
    sail_system.MizzenVang,
    sail_system.StaysailSheetFeederPs,
    sail_system.StaysailSheetFeederSb,
    sail_system.StaysailStayAdjuster,
]
AT_MODELS = [at.ApparentWindSpeed, at.ApparentWindAngle]

_SAIL_SYSTEM_VARIABLES: dict[str, VariableDefinition] = {
    variable.id: variable
    for model in SAIL_SYSTEM_MODELS
    for variable in _build_sail_system_variable_definitions(model)
}


def _build_at_variable_definitions(model: type[LoadsModel]) -> VariableDefinition:
    field_info = model.model_fields["value"]
    variable_meta = model.extract_variable_meta("value", field_info.metadata)

    if not variable_meta or not variable_meta.name or not variable_meta.unit:
        raise ValueError(f"No valid VariableMeta found for A+T model {model.__name__}")

    return VariableDefinition(
        id=variable_meta.name,
        name=model.class_display_name(),
        topic=model.TOPIC,
        get_actual=lambda model_instance: model_instance.value,  # type: ignore[attr-defined]
        unit=variable_meta.unit,
        scale_min=variable_meta.scale_min,
        scale_max=variable_meta.scale_max,
        scale_min_label=variable_meta.scale_min_label,
        scale_max_label=variable_meta.scale_max_label,
    )


_AT_VARIABLES: dict[str, VariableDefinition] = {
    variable.id: variable
    for model in AT_MODELS
    for variable in [_build_at_variable_definitions(model)]
}

VARIABLES = {**_SAIL_SYSTEM_VARIABLES, **_AT_VARIABLES}
ALARMS = {
    alarm.id: alarm
    for model in SAIL_SYSTEM_MODELS
    for alarm in _build_sail_system_alarm_definitions(
        model,
        list(VARIABLES.values()),
    )
}
