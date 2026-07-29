from datetime import datetime, timedelta
from typing import Any, Self

from thrs.classes.machine_state_logger import MachineStateLoggingServiceNoop
from thrs.control.modules.dhw import DhwControl, DhwParameters
from thrs.control.modules.drives import DrivesControl, DrivesParameters
from thrs.input_output.base import (
    CombinedValues,
    SimulationInputs,
    SimulationValues,
    Stamped,
)
from thrs.input_output.definitions import simulation
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.drives import (
    DrivesControlValues,
    DrivesSensorValues,
    DrivesSimulationInputs,
    DrivesSimulationOutputs,
)
from thrs.simulation.cosimulation import (
    CoSimulationMaster,
    CoSimulationParticipant,
    Coupling,
)
from thrs.simulation.fmu import Fmu
from thrs.simulation.io_mapping import CombinedIoMapping


class MockFmu(Fmu):
    # This mock FMU ignores the inputs and always returns the same outputs, but it records the inputs it receives for assertions in the test.
    def __init__(self, outputs: dict[str, Any]):
        self.inputs: list[dict[str, Any]] = []
        self._outputs = outputs

    def tick(self, inputs: dict[str, Any], duration: timedelta) -> dict[str, Any]:
        self.inputs.append(dict(inputs))
        return self._outputs

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> bool:
        return True

    @property
    def solver_time(self) -> float:
        return 0.0


class DrivesDhwSimulationInputs(SimulationInputs):
    drives_oil_cooler_aft: simulation.HeatSource
    drives_oil_cooler_fwd: simulation.HeatSource
    drives_propdrive_aft1: simulation.PropulsionDrive
    drives_propdrive_aft2: simulation.PropulsionDrive
    drives_propdrive_fwd1: simulation.PropulsionDrive
    drives_propdrive_fwd2: simulation.PropulsionDrive
    drives_shorepower: simulation.Converter
    drives_seawater_supply: simulation.Boundary
    dhw_dc_supply: simulation.Boundary
    dhw_adsorption_supply: simulation.Boundary
    dhw_consumers_supply: simulation.Boundary
    dhw_freshwater_supply: simulation.OverpressureTemperatureBoundary
    dhw_hvac_exchanger: simulation.HvacExchanger
    dhw_seawater_supply: simulation.TemperatureBoundary
    dhw_hotwater_demand: simulation.FlowBoundary


class DrivesDhwSimulationOutputs(SimulationValues):
    drives_seawater_return: simulation.TemperatureBoundary
    drives_dhw_exchanger: simulation.ExchangerBoundary
    drives_dhw_return: simulation.TemperatureBoundary
    dhw_drives_exchanger: simulation.ExchangerBoundary
    dhw_drives_return: simulation.TemperatureBoundary
    dhw_dc_exchanger: simulation.ExchangerBoundary
    dhw_dc_return: simulation.TemperatureBoundary
    dhw_adsorption_exchanger: simulation.ExchangerBoundary
    dhw_adsorption_return: simulation.TemperatureBoundary
    dhw_consumers_exchanger: simulation.ExchangerBoundary
    dhw_consumers_return: simulation.TemperatureBoundary
    dhw_seawater_return: simulation.TemperatureBoundary
    dhw_seawater_supply: simulation.FlowBoundary
    dhw_freshwater_return: simulation.FlowBoundary


def test_cosimulation_input_routing():
    drives_mock = MockFmu(
        {
            "drives_dhw_exchanger__flow__l_min": 42.0,
            "drives_dhw_exchanger__temperature_supply__C": 35.0,
        }
    )
    dhw_mock = MockFmu(
        {
            "dhw_drives_exchanger__flow__l_min": 15.0,
            "dhw_drives_exchanger__temperature_supply__C": 55.0,
        }
    )

    drives_dhw = CoSimulationMaster(
        [
            CoSimulationParticipant(
                lambda: drives_mock,
                [DrivesSensorValues],
                [DrivesControlValues],
                DrivesSimulationInputs,
                DrivesSimulationOutputs,
                [
                    Coupling(
                        "dhw_drives_exchanger", "flow", "drives_dhw_supply", "flow", 0.0
                    ),
                    Coupling(
                        "dhw_drives_exchanger",
                        "temperature_supply",
                        "drives_dhw_supply",
                        "temperature",
                        30.0,
                    ),
                ],
            ),
            CoSimulationParticipant(
                lambda: dhw_mock,
                [DhwSensorValues],
                [DhwControlValues],
                DhwSimulationInputs,
                DhwSimulationOutputs,
                [
                    Coupling(
                        "drives_dhw_exchanger", "flow", "dhw_drives_supply", "flow", 0.0
                    ),
                    Coupling(
                        "drives_dhw_exchanger",
                        "temperature_supply",
                        "dhw_drives_supply",
                        "temperature",
                        30.0,
                    ),
                ],
            ),
        ]
    )

    io_mapping = CombinedIoMapping[
        DrivesDhwSimulationInputs, DrivesDhwSimulationOutputs
    ](
        {"drives": DrivesSensorValues, "dhw": DhwSensorValues},
        DrivesDhwSimulationOutputs,
    )

    control_values = CombinedValues(
        values={
            "drives": DrivesControl(
                DrivesParameters(), datetime.now, MachineStateLoggingServiceNoop()
            ).initial()[0],
            "dhw": DhwControl(
                DhwParameters(), datetime.now, MachineStateLoggingServiceNoop()
            ).initial()[0],
        }
    )

    simulation_inputs = DrivesDhwSimulationInputs(
        dhw_dc_supply=simulation.Boundary(
            temperature=Stamped.stamp(60), flow=Stamped.stamp(60)
        ),
        dhw_adsorption_supply=simulation.Boundary(
            temperature=Stamped.stamp(30), flow=Stamped.stamp(45)
        ),
        dhw_consumers_supply=simulation.Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(0)
        ),
        dhw_freshwater_supply=simulation.OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20), overpressure=Stamped.stamp(0.3)
        ),
        dhw_hotwater_demand=simulation.FlowBoundary(flow=Stamped.stamp(40)),
        dhw_hvac_exchanger=simulation.HvacExchanger(
            heat_flow=Stamped.stamp(1000), maximum_temperature=Stamped.stamp(50)
        ),
        dhw_seawater_supply=simulation.TemperatureBoundary(
            temperature=Stamped.stamp(20)
        ),
        drives_oil_cooler_aft=simulation.HeatSource(heat_flow=Stamped.stamp(0)),
        drives_oil_cooler_fwd=simulation.HeatSource(heat_flow=Stamped.stamp(0)),
        drives_propdrive_aft1=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_aft2=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_fwd1=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_propdrive_fwd2=simulation.PropulsionDrive(
            heat_flow=Stamped.stamp(0), active=Stamped.stamp(False)
        ),
        drives_shorepower=simulation.Converter(
            heat_flow=Stamped.stamp(15000), active=Stamped.stamp(True)
        ),
        drives_seawater_supply=simulation.Boundary(
            temperature=Stamped.stamp(20.0), flow=Stamped.stamp(64)
        ),
    )

    inputs = io_mapping.generate_inputs(control_values, simulation_inputs)

    drives_input_keys = set(drives_dhw._participants[0].fmu_key_input_mapping.values())
    dhw_input_keys = set(drives_dhw._participants[1].fmu_key_input_mapping.values())

    # First tick - couplings use initial values
    drives_dhw.tick(inputs, duration=timedelta(seconds=1))

    # Each participant should only receive keys from its own input mapping
    assert set(drives_mock.inputs[0].keys()).issubset(drives_input_keys)
    assert set(dhw_mock.inputs[0].keys()).issubset(dhw_input_keys)

    # The coupled inputs should carry the initial coupling values on first tick
    assert drives_mock.inputs[0]["drives_dhw_supply__flow__l_min"] == 0.0
    assert drives_mock.inputs[0]["drives_dhw_supply__temperature__C"] == 30.0
    assert dhw_mock.inputs[0]["dhw_drives_supply__flow__l_min"] == 0.0
    assert dhw_mock.inputs[0]["dhw_drives_supply__temperature__C"] == 30.0

    # Second tick - couplings route outputs from the previous tick
    drives_dhw.tick(inputs, duration=timedelta(seconds=1))

    # drives now receives the coupled values from dhw' first tick outputs
    assert drives_mock.inputs[1]["drives_dhw_supply__flow__l_min"] == 15.0
    assert drives_mock.inputs[1]["drives_dhw_supply__temperature__C"] == 55.0

    # dhw now receives the coupled values from drives's first tick outputs
    assert dhw_mock.inputs[1]["dhw_drives_supply__flow__l_min"] == 42.0
    assert dhw_mock.inputs[1]["dhw_drives_supply__temperature__C"] == 35.0
