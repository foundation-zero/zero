from datetime import datetime
from typing import Callable

from aiomqtt import Client as MqttClient

from thrs.classes.database import PostgresDatabase
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
    MachineStateLoggingServiceNoop,
)
from thrs.input_output.base import CombinedValues
from thrs.orchestration.comms import (
    ControlChannels,
    DirectivesChannels,
    MqttConnector,
    SimulationChannels,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import CombinedAlarms, CombinedControl
from thrs.orchestration.simulation import Simulation
from thrs.runtime.descriptions.simulation import Mode
from thrs.runtime.directives import DirectiveHandling
from thrs.runtime.runners.lockstep import LockstepRunner
from thrs.runtime.runtime import Runtime


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
    machine_state_logging_service_enabled: bool = True,
) -> tuple[CombinedControl, ControlChannels, CombinedAlarms]:
    control_channels = ControlChannels(connector, config, mode.control_module)
    pg_database = PostgresDatabase(config)

    parameters = {
        module: mode.control_module.parameters_for_module(module)()
        for module in mode.control_module.modules
    }

    machine_state_logging_service = (
        MachineStateLoggingService(pg_database)
        if machine_state_logging_service_enabled
        else MachineStateLoggingServiceNoop()
    )

    control = mode.control_module.control(
        CombinedValues(parameters),
        time_fn,
        machine_state_logging_service,
    )

    return control, control_channels, mode.control_module.alarms()



def setup_lockstep(mode: Mode, settings: Config, mqtt_client: MqttClient) -> Runtime:

    connector = MqttConnector(mqtt_client)

    simulation, simulation_channels = setup_simulation(connector, settings, mode)

    control, control_channels, alarms = setup_control(
        connector, settings, mode, simulation.time
    )

    runner = LockstepRunner(
        control=control,
        control_channels=control_channels,
        alarms=alarms,
        simulation=simulation,
        simulation_channels=simulation_channels,
    )

    directives_channels = DirectivesChannels(connector, settings)

    directive_handling = DirectiveHandling(
        directives_channels,
        mode,
        simulation.time,
    )
    return Runtime(
        runner,
        connector,
        simulation.tick_duration,
        directive_handling,
    )

