import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from thrs.classes.database import PostgresDatabase
from thrs.classes.machine_state_logger import (
    MachineStateLoggingService,
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.classes.persistence.engine import (
    NoopPersistentEngine,
    PersistentEngine,
    PostgresPersistentEngine,
)
from thrs.classes.persistence.manager import PersistManager
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

logger: logging.Logger = logging.getLogger(__name__)


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
        datetime.now(UTC),
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


def setup_database(
    config: Config,
    module_persistence_enabled: bool,
    machine_state_logging_service_enabled: bool,
) -> PostgresDatabase | None:
    """Single engine shared by every consumer that needs Postgres. Only built when
    persistence or machine-state logging actually needs one; `None` otherwise, so the
    runtime can run against MQTT only."""
    if not module_persistence_enabled and not machine_state_logging_service_enabled:
        return None

    return PostgresDatabase(config)


async def setup_persistence_manager(
    database: PostgresDatabase | None,
    module_persistence_enabled: bool,
) -> PersistManager:
    """Build the persist manager. Without persistence enabled it silently no-ops, so
    the runtime can run against MQTT only."""
    engine: PersistentEngine = NoopPersistentEngine()

    if module_persistence_enabled and database is not None:
        if await _is_postgres_reachable(database):
            engine = PostgresPersistentEngine(database)
        else:
            logger.warning("Postgres is not reachable - module persistence disabled")

    return PersistManager(engine)


async def _is_postgres_reachable(database: PostgresDatabase) -> bool:
    """Check if Postgres is reachable."""
    try:
        async with database.session_factory() as session:
            await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False

    return True


def setup_machine_state_logger(
    database: PostgresDatabase | None,
    machine_state_logging_service_enabled: bool,
) -> StateLogger:
    """Disabled by the caller, it logs machine state to a noop service."""
    if not machine_state_logging_service_enabled or database is None:
        return MachineStateLoggingServiceNoop()

    return MachineStateLoggingService(database)


def setup_control_modules(
    connector: MqttConnector,
    config: Config,
    control_modules: dict[str, ModuleDescription],
    time_fn: Callable[[], datetime],
    database: PostgresDatabase | None,
    machine_state_logging_service_enabled: bool,
) -> list[Module]:
    result = []

    for module_name, module in control_modules.items():
        # Each module gets its own service: it tracks the last state and trigger of one control.
        machine_state_logger = setup_machine_state_logger(
            database, machine_state_logging_service_enabled
        )

        parameters = module.parameters_cls()
        control = module.control(
            parameters,
            time_fn,
            machine_state_logger,
        )

        # This line should not be here since it exposes that we are dealing with a switching module
        # We need to refactor the switching control functionality to be more local/abstractable
        module.control_mode_cls = SwitchingControlMode[module.control_mode_cls]

        channel = ControlChannels(connector, config, module_name, module)

        alarms = module.alarms()

        result.append(Module(module_name, control, alarms, channel))

    return result
