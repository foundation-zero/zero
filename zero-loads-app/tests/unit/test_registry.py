from collections import Counter

from loads.registry.registry import (
    AT_MODELS,
    FIBER_OPTIC_MODELS,
    SAIL_SYSTEM_MODELS,
    VARIABLES,
    _build_at_variable_definitions,
    _build_loads_model_variable_definitions,
    _build_sail_system_alarm_definitions,
)


def _duplicates(ids: list[str]) -> list[str]:
    return [id for id, count in Counter(ids).items() if count > 1]


def test_variable_ids_are_unique():
    variable_ids = [
        *(
            variable.id
            for model in [*SAIL_SYSTEM_MODELS, *FIBER_OPTIC_MODELS]
            for variable in _build_loads_model_variable_definitions(model)
        ),
        *(_build_at_variable_definitions(model).id for model in AT_MODELS),
    ]

    assert _duplicates(variable_ids) == []


def test_alarm_ids_are_unique():
    alarm_ids = [
        alarm.id
        for model in SAIL_SYSTEM_MODELS
        for alarm in _build_sail_system_alarm_definitions(
            model, list(VARIABLES.values())
        )
    ]

    assert _duplicates(alarm_ids) == []
