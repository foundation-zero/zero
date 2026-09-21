import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.types.union import StrawberryUnion

from thrs.graphql.base import add_simulation_input_mutations
from thrs.graphql.helpers import pydantic_to_strawberry_type
from thrs.runtime.descriptions.simulation import simulation_io_classes

io_mapping = simulation_io_classes()

inputs_strawberry_type_mapping = {
    name: pydantic_to_strawberry_type(inputs)
    for name, (inputs, _) in io_mapping.items()
}

outputs_strawberry_type_mapping = {
    name: pydantic_to_strawberry_type(outputs)
    for name, (_, outputs) in io_mapping.items()
}


SimulationInputsType = StrawberryUnion(
    "SimulationInputsType",
    tuple(StrawberryAnnotation(t) for t in inputs_strawberry_type_mapping.values()),  # type: ignore
)

SimulationOutputsType = StrawberryUnion(
    "SimulationOutputsType",
    tuple(StrawberryAnnotation(t) for t in outputs_strawberry_type_mapping.values()),  # type: ignore
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
@add_simulation_input_mutations(
    "thrs",
    io_mapping,
    inputs_strawberry_type_mapping,
    lambda context: context.simulation_messaging,
)
class SimulationMutations:
    pass
