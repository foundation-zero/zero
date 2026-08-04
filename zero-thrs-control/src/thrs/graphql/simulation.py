import strawberry

from thrs.graphql.base import add_simulation_input_mutations
from thrs.graphql.helpers import (
    optional_pydantic_to_graphql,
    pydantic_to_strawberry_type,
)
from thrs.graphql.messaging import SimulationMessaging
from thrs.input_output.modules.adsorption import (
    AdsorptionSimulationInputs,
    AdsorptionSimulationOutputs,
)
from thrs.input_output.modules.consumers import (
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dc import DcSimulationInputs, DcSimulationOutputs
from thrs.input_output.modules.dhw import (
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.drives import (
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSimulationInputs, PcmSimulationOutputs
from thrs.input_output.modules.pvt import PvtSimulationInputs, PvtSimulationOutputs
from thrs.input_output.modules.thrs import ThrsSimulationInputs, ThrsSimulationOutputs
from thrs.input_output.modules.thrusters import (
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)

io_mapping = {
    "thrusters": (ThrustersSimulationInputs, ThrustersSimulationOutputs),
    "pcm": (PcmSimulationInputs, PcmSimulationOutputs),
    "pvt": (PvtSimulationInputs, PvtSimulationOutputs),
    "consumers": (ConsumersSimulationInputs, ConsumersSimulationOutputs),
    "adsorption": (AdsorptionSimulationInputs, AdsorptionSimulationOutputs),
    "drives": (DrivesSimulationInputs, DrivesSimulationOutputs),
    "dc": (DcSimulationInputs, DcSimulationOutputs),
    "dhw": (DhwSimulationInputs, DhwSimulationOutputs),
    "high_temperature": (
        HighTemperatureSimulationInputs,
        HighTemperatureSimulationOutputs,
    ),
    "thrs": (ThrsSimulationInputs, ThrsSimulationOutputs),
}

inputs_strawberry_type_mapping = {
    name: pydantic_to_strawberry_type(inputs)
    for name, (inputs, _) in io_mapping.items()
}

outputs_strawberry_type_mapping = {
    name: pydantic_to_strawberry_type(outputs)
    for name, (_, outputs) in io_mapping.items()
}

inputs_strawberry_type_by_cls = {
    inputs_cls: inputs_strawberry_type_mapping[name]
    for name, (inputs_cls, _) in io_mapping.items()
}

outputs_strawberry_type_by_cls = {
    outputs_cls: outputs_strawberry_type_mapping[name]
    for name, (_, outputs_cls) in io_mapping.items()
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
    inputs = simulation.simulation_inputs
    if inputs is None:
        return None

    graphql_type = inputs_strawberry_type_by_cls.get(type(inputs))
    if graphql_type is None:
        raise ValueError(f"Unsupported simulation inputs type: {type(inputs)}")

    return optional_pydantic_to_graphql(inputs)


def resolve_outputs(
    simulation: SimulationMessaging,
) -> SimulationOutputsType | None:  # pyright: ignore[reportInvalidTypeForm]
    outputs = simulation.simulation_outputs
    if outputs is None:
        return None

    graphql_type = outputs_strawberry_type_by_cls.get(type(outputs))
    if graphql_type is None:
        raise ValueError(f"Unsupported simulation outputs type: {type(outputs)}")

    return optional_pydantic_to_graphql(outputs)


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
    "adsorption",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "drives",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "dc",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "dhw",
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
