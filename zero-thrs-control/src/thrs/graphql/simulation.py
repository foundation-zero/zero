from thrs.graphql.base import add_simulation_input_mutations
from thrs.graphql.helpers import dedataframed_pydantic_to_strawberry_type
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


ThrustersSimulationInputsType = dedataframed_pydantic_to_strawberry_type(
    ThrustersSimulationInputs
)
ThrustersSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    ThrustersSimulationOutputs
)

PvtSimulationInputsType = dedataframed_pydantic_to_strawberry_type(PvtSimulationInputs)
PvtSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    PvtSimulationOutputs
)


PcmSimulationInputsType = dedataframed_pydantic_to_strawberry_type(PcmSimulationInputs)
PcmSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    PcmSimulationOutputs
)

ConsumersSimulationInputsType = dedataframed_pydantic_to_strawberry_type(
    ConsumersSimulationInputs
)
ConsumersSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    ConsumersSimulationOutputs
)

HighTemperatureSimulationInputsType = dedataframed_pydantic_to_strawberry_type(
    HighTemperatureSimulationInputs
)
HighTemperatureSimulationOutputsType = dedataframed_pydantic_to_strawberry_type(
    HighTemperatureSimulationOutputs
)


@add_simulation_input_mutations(
    "thrusters",
    ThrustersSimulationInputs,
    ThrustersSimulationInputsType,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "pvt",
    PvtSimulationInputs,
    PvtSimulationInputsType,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "pcm",
    PcmSimulationInputs,
    PcmSimulationInputsType,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "consumers",
    ConsumersSimulationInputs,
    ConsumersSimulationInputsType,
    lambda context: context.simulation_messaging,
)
@add_simulation_input_mutations(
    "high_temperature",
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationInputsType,
    lambda context: context.simulation_messaging,
)
class SimulationMutations:
    pass
