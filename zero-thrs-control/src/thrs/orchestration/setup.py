from thrs.orchestration.comms import (
    ControlChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
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
            {
                module: desc.sensor_values_cls
                for module, desc in mode.control_modules.items()
            },
            {
                module: desc.control_values_cls
                for module, desc in mode.control_modules.items()
            },
            simulation.inputs_cls,
            simulation.outputs_cls,
        ),
    )


def setup_control(
    connector: MqttConnector,
    config: Config,
    mode: Mode,
) -> dict[str, ControlChannels]:
    return {
        module_name: ControlChannels(connector, config, module_name, module)
        for module_name, module in mode.control_modules.items()
    }
