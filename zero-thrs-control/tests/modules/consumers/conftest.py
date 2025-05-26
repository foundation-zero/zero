from pytest import fixture

from input_output.base import Stamped
from input_output.definitions.simulation import Boundary
from input_output.modules.consumers import ConsumersSimulationInputs


from control.modules.consumers import ConsumersControl


@fixture
def control():

    return ConsumersControl()


@fixture
def simulation_inputs():
    return ConsumersSimulationInputs(
        consumers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(42)
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(94)
        ),
        consumers_boosting_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(29)
        ),
    )
