import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from thrs.control.state import ControlModes
from thrs.input_output.base import CombinedValues
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
from thrs.persistence.database import PostgresDatabase
from thrs.persistence.engine import (
    NoopPersistentEngine,
    PersistentEngine,
    PostgresPersistentEngine,
)
from thrs.persistence.manager import PersistManager

logger: logging.Logger = logging.getLogger(__name__)


def initial_control_values(
    control_modules: dict[str, ModuleDescription], timestamp: datetime
) -> CombinedValues:
    """Every module's control values at their initial values, stamped at `timestamp`."""
    return CombinedValues(
        values={
            module: description.control_values_cls.initial(timestamp)
            for module, description in control_modules.items()
        }
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
    start_time = datetime.now(UTC)

    simulation = Simulation(
        sensor_values_cls,
        simulation_description.simulation_outputs_cls,
        simulation_description.fmu,
        simulation_description.simulation_inputs,
        start_time,
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
            initial_control_values(control_modules, start_time),
        ),
    )


def setup_database(
    config: Config,
    module_persistence_enabled: bool,
) -> PostgresDatabase | None:
    """Single engine shared by every consumer that needs Postgres. Only built when
    persistence actually needs one; `None` otherwise, so the runtime can run against
    MQTT only."""
    if not module_persistence_enabled:
        return None

    return PostgresDatabase(config)


async def setup_persistence_manager(
    database: PostgresDatabase | None,
    module_persistence_enabled: bool,
    allow_boot_without_persistence_having_active_postgres: bool = False,
) -> PersistManager:
    """Build the persist manager. Without persistence enabled it silently no-ops, so
    the runtime can run against MQTT only."""
    engine: PersistentEngine = NoopPersistentEngine()

    if module_persistence_enabled and database is not None:
        if await _is_postgres_reachable(database):
            engine = PostgresPersistentEngine(database)
        elif allow_boot_without_persistence_having_active_postgres:
            logger.warning("Postgres is not reachable - module persistence disabled")
        else:
            raise RuntimeError(
                "Postgres is not reachable and allow_boot_without_persistence_having_active_postgres "
                "is False - refusing to boot without persistence having active postgres"
            )

    return PersistManager(engine)


async def _is_postgres_reachable(database: PostgresDatabase) -> bool:
    """Check if Postgres is reachable."""
    try:
        async with database.session_factory() as session:
            await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False

    return True


async def setup_control_modules(
    connector: MqttConnector,
    config: Config,
    control_modules: dict[str, ModuleDescription],
    time_fn: Callable[[], datetime],
    persistence: PersistManager,
    publish_qos: int = 1,
) -> list[Module]:
    """Build the control modules, each starting from its stored configuration if
    there is one, or else its default parameters in manual. Raises if a stored
    configuration no longer validates against its module's parameters."""
    result = []

    for module_name, description in control_modules.items():
        parameters = None
        automation_mode: ControlModes = "manual"
        stored = await persistence.load(module_name)
        if stored is not None:
            automation_mode = stored.control_mode
            if stored.parameters is not None:
                parameters = description.parameters_cls.model_validate(
                    stored.parameters
                )

        result.append(
            Module(
                module_name,
                description=description,
                channels=ControlChannels(
                    connector, config, module_name, description, publish_qos=publish_qos
                ),
                time_fn=time_fn,
                parameters=parameters,
                automation_mode=automation_mode,
            )
        )

    return result
