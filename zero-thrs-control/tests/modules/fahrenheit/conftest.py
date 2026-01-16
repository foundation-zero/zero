from pytest import fixture

from thrs.input_output.definitions.simulation import ExchangerBoundary
from thrs.input_output.modules.fahrenheit import FahrenheitSimulationInputs


@fixture
def simulation_inputs():
    return FahrenheitSimulationInputs(
        fahrenheit_hot_supply=ExchangerBoundary(),
        fahrenheit_waste_supply=ExchangerBoundary(),
        fahrenheit_cld_supply = TemperatureBoundary(),
        fahrenheit_available_cold_temperature=Temperature
    )