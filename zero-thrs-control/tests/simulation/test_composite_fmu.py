from datetime import datetime, timedelta

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
from thrs.simulation.models.fmu_paths import boilers_path, lt1_path


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


def test_cosimulation():
    lt1_boilers = CoSimulationMaster(
        [
            CoSimulationParticipant(
                Fmu(lt1_path),
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
                ],  # TODO: no sensor for the supply flow of lt1 in boilers when low temp boosting!)
            ),
            CoSimulationParticipant(
                Fmu(boilers_path),
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

    with lt1_boilers as composite_fmu:
        outputs = composite_fmu.tick(
            inputs,
            duration=timedelta(seconds=1),
        )

        assert len(outputs) > 0
