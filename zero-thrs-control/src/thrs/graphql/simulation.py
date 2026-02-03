import strawberry
from thrs.graphql.base import add_simulation_input_mutations
from thrs.graphql.helpers import (
    dedataframed_pydantic_to_strawberry_type,
    optional_pydantic_to_graphql,
)
from thrs.graphql.messaging import SimulationMessaging
from thrs.input_output.modules.consumers import (
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSimulationInputs, PcmSimulationOutputs
from thrs.input_output.modules.pvt import PvtSimulationInputs, PvtSimulationOutputs
from thrs.input_output.modules.thrusters import (
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)

io_mapping = {
    "thrusters": (ThrustersSimulationInputs, ThrustersSimulationOutputs),
    "pcm": (PcmSimulationInputs, PcmSimulationOutputs),
    "pvt": (PvtSimulationInputs, PvtSimulationOutputs),
    "consumers": (ConsumersSimulationInputs, ConsumersSimulationOutputs),
    "high_temperature": (
        HighTemperatureSimulationInputs,
        HighTemperatureSimulationOutputs,
    ),
}

inputs_strawberry_type_mapping = {
    name: dedataframed_pydantic_to_strawberry_type(inputs)
    for name, (inputs, _) in io_mapping.items()
}

outputs_strawberry_type_mapping = {
    name: dedataframed_pydantic_to_strawberry_type(outputs)
    for name, (_, outputs) in io_mapping.items()
}

SimulationInputsType = strawberry.union(
    "SimulationInputsType", tuple(inputs_strawberry_type_mapping.values())
)

SimulationOutputsType = strawberry.union(
    "SimulationOutputsType", tuple(outputs_strawberry_type_mapping.values())
)


def resolve_inputs(
    simulation: SimulationMessaging,
) -> SimulationInputsType | None:  # pyright: ignore[reportInvalidTypeForm]
    return optional_pydantic_to_graphql(
        inputs_strawberry_type_mapping[simulation.mode],
        simulation.simulation_inputs,
    )


def resolve_outputs(
    simulation: SimulationMessaging,
) -> SimulationOutputsType | None:  # pyright: ignore[reportInvalidTypeForm]
    return optional_pydantic_to_graphql(
        outputs_strawberry_type_mapping[simulation.mode],
        simulation.simulation_outputs,
    )


@strawberry.type
@add_simulation_input_mutations(
    "thrusters",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "pvt",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "pcm",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "consumers",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "high_temperature",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
class SimulationMutations:
    pass
