from datetime import datetime
from typing import Callable

from thrs.input_output.base import CombinedValues
from thrs.orchestration.comms import (
    ControlChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation
from thrs.runtime.descriptions.simulation import Mode


def setup_simulation(
    connector: MqttConnector,
    config: Config,
    mode: Mode,
) -> tuple[Simulation, SimulationChannels]:
    simulation = mode.setup_simulation()
    if simulation is None:
        raise ValueError("simulation must be defined for simulation mode")

    return (
        simulation,
        SimulationChannels(
            connector,
            config,
            mode.control_module.sensor_values_clss,
            mode.control_module.control_values_clss,
            simulation.inputs_cls,
            simulation.outputs_cls,
        ),
    )


def setup_control(
    connector: MqttConnector,
    config: Config,
    mode: Mode,
    time_fn: Callable[[], datetime],
) -> tuple[CombinedControl, ControlChannels, CombinedAlarms]:
    control_channels = ControlChannels(connector, config, mode.control_module)

    parameters = {
        module: mode.control_module.parameters_for_module(module)()
        for module in mode.control_module.modules
    }

    control = mode.control_module.control(CombinedValues(parameters), time_fn)

    return control, control_channels, mode.control_module.alarms()
