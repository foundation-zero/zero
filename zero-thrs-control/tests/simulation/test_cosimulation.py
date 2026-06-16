from datetime import datetime, timedelta
from typing import Any

from thrs.control.modules.boilers import BoilersControl, BoilersParameters
from thrs.control.modules.lt1 import Lt1Control, Lt1Parameters
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
)
from thrs.input_output.definitions import simulation
from thrs.input_output.modules.boilers import (
    BoilersControlValues,
    BoilersSensorValues,
    BoilersSimulationInputs,
    BoilersSimulationOutputs,
)
from thrs.input_output.modules.lt1 import (
    Lt1ControlValues,
    Lt1SensorValues,
    Lt1SimulationInputs,
    Lt1SimulationOutputs,
)
from thrs.simulation.cosimulation import (
    CoSimulationMaster,
    CoSimulationParticipant,
    Coupling,
)
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import CombinedIoMapping


class Lt1BoilersSimulationInputs(SimulationInputs):
    lt1_oil_cooler_aft: simulation.HeatSource
    lt1_oil_cooler_fwd: simulation.HeatSource
    lt1_propdrive_aft1: simulation.PropulsionDrive
    lt1_propdrive_aft2: simulation.PropulsionDrive
    lt1_propdrive_fwd1: simulation.PropulsionDrive
    lt1_propdrive_fwd2: simulation.PropulsionDrive
    lt1_shorepower: simulation.Converter
    lt1_seawater_supply: simulation.Boundary
    boilers_lt2_supply: simulation.Boundary
    boilers_fahrenheit_supply: simulation.Boundary
    boilers_ht_supply: simulation.Boundary
    boilers_freshwater_supply: simulation.OverpressureTemperatureBoundary
    boilers_hvac_exchanger: simulation.HvacExchanger
    boilers_seawater_supply: simulation.TemperatureBoundary
    boilers_hotwater_demand: simulation.FlowBoundary


class Lt1BoilersSimulationOutputs(SimulationValues):
    lt1_seawater_return: simulation.TemperatureBoundary
    lt1_boilers_return: simulation.TemperatureBoundary
    boilers_lt1_return: simulation.TemperatureBoundary
    boilers_lt2_return: simulation.TemperatureBoundary
    boilers_fahrenheit_return: simulation.TemperatureBoundary
    boilers_ht_return: simulation.TemperatureBoundary
    boilers_seawater_return: simulation.TemperatureBoundary
    boilers_seawater_supply: simulation.FlowBoundary
    boilers_freshwater_return: simulation.FlowBoundary


def test_cosimulation_input_routing():
    class MockFmu(Fmu):
        # This mock FMU ignores the inputs and always returns the same outputs, but it records the inputs it receives for assertions in the test.
        def __init__(self, outputs: dict[str, Any]):
            self.inputs: list[dict[str, Any]] = []
            self._outputs = outputs

        def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]:
            self.inputs.append(dict(inputs))
            return self._outputs

        def __enter__(self) -> "MockFmu":
            return self

        def __exit__(self, *_) -> bool:
            return True

        @property
        def solver_time(self) -> float:
            return 0.0

    lt1_mock = MockFmu(
        {
            "lt1_flow_recovery__flow__l_min": 42.0,
            "lt1_temperature_recovery__temperature__C": 35.0,
        }
    )
    boilers_mock = MockFmu(
        {
            "boilers_flow_lt1__flow__l_min": 15.0,
            "boilers_temperature_freshwater_supply__temperature__C": 55.0,
        }
    )

    lt1_boilers = CoSimulationMaster(
        [
            CoSimulationParticipant(
                lt1_mock,
                Lt1SensorValues,
                Lt1ControlValues,
                Lt1SimulationInputs,
                Lt1SimulationOutputs,
                [
                    Coupling(
                        "boilers_flow_lt1", "flow", "lt1_boilers_supply", "flow", 0.0
                    ),
                    Coupling(
                        "boilers_temperature_freshwater_supply",
                        "temperature",
                        "lt1_boilers_supply",
                        "temperature",
                        30.0,
                    ),
                ],
            ),
            CoSimulationParticipant(
                boilers_mock,
                BoilersSensorValues,
                BoilersControlValues,
                BoilersSimulationInputs,
                BoilersSimulationOutputs,
                [
                    Coupling(
                        "lt1_flow_recovery", "flow", "boilers_lt1_supply", "flow", 0.0
                    ),
                    Coupling(
                        "lt1_temperature_recovery",
                        "temperature",
                        "boilers_lt1_supply",
                        "temperature",
                        30.0,
                    ),
                ],
            ),
        ]
    )

    io_mapping = CombinedIoMapping[
        Lt1BoilersSimulationInputs, Lt1BoilersSimulationOutputs
    ](
        {"lt1": Lt1SensorValues, "boilers": BoilersSensorValues},
        Lt1BoilersSimulationOutputs,
    )

    control_values = CombinedValues(
        values={
            "lt1": Lt1Control(Lt1Parameters(), datetime.now).initial().values,
            "boilers": BoilersControl(BoilersParameters(), datetime.now)
            .initial()
            .values,
        }
    )

    simulation_inputs = Lt1BoilersSimulationInputs(
        boilers_lt2_supply=simulation.Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(60)
        ),
        boilers_fahrenheit_supply=simulation.Boundary(
            temperature=Stamped.stamp(30), flow=Stamped.stamp(45)
        ),
        boilers_ht_supply=simulation.Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(0)
        ),
        boilers_freshwater_supply=simulation.OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20), overpressure=Stamped.stamp(0.3)
        ),
        boilers_hotwater_demand=simulation.FlowBoundary(flow=Stamped.stamp(40)),
        boilers_hvac_exchanger=simulation.HvacExchanger(
            heat_flow=Stamped.stamp(1000), maximum_temperature=Stamped.stamp(50)
        ),
        boilers_seawater_supply=simulation.TemperatureBoundary(
            temperature=Stamped.stamp(20)
        ),
        lt1_oil_cooler_aft=simulation.HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_oil_cooler_fwd=simulation.HeatSource(heat_flow=Stamped.stamp(0)),
        lt1_propdrive_aft1=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_aft2=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd1=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_propdrive_fwd2=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        lt1_shorepower=simulation.Converter(
            heat_flow=Stamped.stamp(15000), active=Stamped.stamp(True)
        ),
        lt1_seawater_supply=simulation.Boundary(
            temperature=Stamped.stamp(20.0), flow=Stamped.stamp(64)
        ),
    )

    inputs = io_mapping.generate_inputs(control_values, simulation_inputs)

    lt1_input_keys = set(lt1_boilers._participants[0].fmu_key_input_mapping.values())
    boilers_input_keys = set(
        lt1_boilers._participants[1].fmu_key_input_mapping.values()
    )

    # First tick - couplings use initial values
    lt1_boilers.tick(inputs, duration=timedelta(seconds=1))

    # Each participant should only receive keys from its own input mapping
    assert set(lt1_mock.inputs[0].keys()).issubset(lt1_input_keys)
    assert set(boilers_mock.inputs[0].keys()).issubset(boilers_input_keys)

    # The coupled inputs should carry the initial coupling values on first tick
    assert lt1_mock.inputs[0]["lt1_boilers_supply__flow__l_min"] == 0.0
    assert lt1_mock.inputs[0]["lt1_boilers_supply__temperature__C"] == 30.0
    assert boilers_mock.inputs[0]["boilers_lt1_supply__flow__l_min"] == 0.0
    assert boilers_mock.inputs[0]["boilers_lt1_supply__temperature__C"] == 30.0

    # Second tick - couplings route outputs from the previous tick
    lt1_boilers.tick(inputs, duration=timedelta(seconds=1))

    # lt1 now receives the coupled values from boilers' first tick outputs
    assert lt1_mock.inputs[1]["lt1_boilers_supply__flow__l_min"] == 15.0
    assert lt1_mock.inputs[1]["lt1_boilers_supply__temperature__C"] == 55.0

    # boilers now receives the coupled values from lt1's first tick outputs
    assert boilers_mock.inputs[1]["boilers_lt1_supply__flow__l_min"] == 42.0
    assert boilers_mock.inputs[1]["boilers_lt1_supply__temperature__C"] == 35.0
