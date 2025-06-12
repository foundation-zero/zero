from pytest import fixture

from control.modules.pcm import PcmControl
from input_output.base import Stamped
from input_output.definitions.simulation import Boundary, TemperatureBoundary
from input_output.modules.pcm import PcmSimulationInputs


@fixture
def control():
    return PcmControl()


@fixture
def simulation_inputs():
    return PcmSimulationInputs(
        pcm_producers_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_return=TemperatureBoundary(temperature=Stamped.stamp(60)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    )
