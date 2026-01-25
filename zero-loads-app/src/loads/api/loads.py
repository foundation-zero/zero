from dataclasses import dataclass

from loads.sensors import sail_system
from loads.sensors.base import LoadsModel


@dataclass
class VariableDefinition:
    id: str
    function_id: str
    field_name: str
    unit: str
    suffix: str
    minimum: float | None
    maximum: float | None


@dataclass
class FunctionDefinition:
    id: str
    model: type[LoadsModel]
    topic: str
    variables: list[VariableDefinition]


def build_function_definition(model: type[LoadsModel]) -> FunctionDefinition:
    function_id = model.__name__.lower()  # TODO: camel to kebab

    variables = [
        VariableDefinition(
            id=f"{function_id}-{variable_meta.suffix}",
            function_id=function_id,
            field_name=field,  # TODO: needed?
            unit=variable_meta.unit,
            suffix=variable_meta.suffix,
            minimum=model.extract_minimum(field_info.metadata),
            maximum=model.extract_maximum(field_info.metadata),
        )
        for field, field_info in model.model_fields.items()
        if (variable_meta := model.extract_variable_meta(field_info.metadata))
    ]

    return FunctionDefinition(
        id=function_id,
        model=model,
        topic=model.TOPIC,
        variables=variables,
    )


MODELS: list[type[LoadsModel]] = [
    sail_system.BladeAdjuster,
    sail_system.BladeCunningham,
    sail_system.BladeSheetCaptivePS,
    sail_system.BladeSheetCaptiveSB,
    sail_system.BladeSheetFeederPs,
    sail_system.BladeSheetFeederSb,
    sail_system.BladeTweakerPS,
    sail_system.BladeTweakerSB,
    sail_system.CodeSailTack,
    sail_system.HeadsailLocks,
    sail_system.MainCheckstayDeflector,
    sail_system.MainCunningham,
    sail_system.MainHalyard,
    sail_system.MainOuthaul,
    sail_system.MainPreventer,
    sail_system.MainRunnerSb,
    sail_system.MainRunnerPs,
    sail_system.MainSheet,
    sail_system.MainTraveler,
    sail_system.MainVang,
    sail_system.MizzenCheckstayDeflector,
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
    sail_system.StaysailSheetPs,
    sail_system.StaysailSheetSb,
    sail_system.StaysailSheetFeederPs,
    sail_system.StaysailSheetFeederSb,
    sail_system.StaysailStayAdjuster,
]

FUNCTIONS: dict[str, FunctionDefinition] = {
    function_definition.id: function_definition
    for function_definition in [build_function_definition(model) for model in MODELS]
}

VARIABLES: dict[str, VariableDefinition] = {
    variable.id: variable
    for function in FUNCTIONS.values()
    for variable in function.variables
}
