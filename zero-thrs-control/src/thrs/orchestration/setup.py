from collections.abc import Callable
from datetime import datetime, timedelta

from thrs.control.switching import SwitchingControlMode
from thrs.orchestration.comms import (
    ControlChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import Module, ModuleDescription
from thrs.orchestration.simulation import (
    Simulation,
    SimulationDescription,
    SimulationUnit,
)


def setup_simulation_module(
    connector: MqttConnector,
    config: Config,
    control_modules: dict[str, ModuleDescription],
    simulation_description: SimulationDescription,
) -> SimulationUnit:
    sensor_values_cls = {
        module: desc.sensor_values_cls for module, desc in control_modules.items()
    }

    simulation = Simulation(
        sensor_values_cls,
        simulation_description.simulation_outputs_cls,
        simulation_description.fmu,
        simulation_description.simulation_inputs,
        datetime.now(),
        timedelta(seconds=1),
    )

    return SimulationUnit(
        simulation,
        SimulationChannels(
            connector,
            config,
            sensor_values_cls,
            {
                module: desc.control_values_cls
                for module, desc in control_modules.items()
            },
            type(simulation_description.simulation_inputs),
            simulation_description.simulation_outputs_cls,
        ),
    )


def setup_control_modules(
    connector: MqttConnector,
    config: Config,
    control_modules: dict[str, ModuleDescription],
    time_fn: Callable[[], datetime],
) -> list[Module]:
    result = []
    for module_name, module in control_modules.items():
        parameters = module.parameters_cls()
        control = module.control(parameters, time_fn)

        # This line should not be here since it exposes that we are dealing with a switching module
        # We need to refactor the switching control functionality to be more local/abstractable
        module.control_mode_cls = SwitchingControlMode[module.control_mode_cls]

        channel = ControlChannels(connector, config, module_name, module)

        alarms = module.alarms()

        result.append(Module(module_name, control, alarms, channel))

    return result
