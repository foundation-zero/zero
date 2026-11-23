import logging
from collections.abc import Iterable
from datetime import datetime, timedelta

from pydantic import ValidationError

from thrs.classes.persistence.engine import PersistentEngine
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.state import ControlState
from thrs.orchestration.module import Module

logger: logging.Logger = logging.getLogger(__name__)


class PersistManager:
    """Restores module configuration on start and writes it back on change, with a
    periodic heartbeat."""

    def __init__(
        self,
        persistence_engine: PersistentEngine,
        heartbeat: timedelta = timedelta(seconds=60),
        apply_module_defaults_on_corrupt_database: bool = False,
    ) -> None:
        self._persistence_engine = persistence_engine
        self._heartbeat = heartbeat
        self._apply_module_defaults_on_corrupt_database = (
            apply_module_defaults_on_corrupt_database
        )
        # Last snapshot restored or saved per module, and when.
        self._persisted: dict[str, tuple[ModulePersistenceSnapshot, datetime]] = {}

    async def restore(self, module: Module) -> bool:
        """Retrieve the module configuration from the persistence engine and apply it to the module.
        Returns True if a restore was performed. Returns True if restore was applied successfully."""

        logger.debug("Persistence restoring config for module %s", module.name)
        stored = await self._load_snapshot(module.name)

        if stored is not None:
            logger.debug(
                "Persistence applying stored config for module %s", module.name
            )
            self._apply_snapshot(module, stored)
            return True

        return False

    async def restore_all(self, modules: Iterable[Module]) -> None:
        """Restore all modules from the persistence engine."""
        for module in modules:
            await self.restore(module)

    async def persist(self, module_name: str, controller_state: ControlState) -> bool:
        """Write the configuration in a module's controller state if it changed or the
        heartbeat expired. Returns whether a write was performed. Raises if the
        persistence engine fails."""
        snapshot = ModulePersistenceSnapshot.from_controller_state(controller_state)

        persisted = self._persisted.get(module_name)
        if persisted is not None:
            persisted_snapshot, persisted_at = persisted
            if (
                persisted_snapshot == snapshot
                and datetime.now() - persisted_at < self._heartbeat
            ):
                return False

        await self._persistence_engine.save(module_name, snapshot)
        self._persisted[module_name] = (snapshot, datetime.now())
        logger.debug("Saved config for module %s", module_name)
        return True

    def _apply_snapshot(
        self, module: Module, snapshot: ModulePersistenceSnapshot
    ) -> None:
        """Apply a stored configuration snapshot to the module. Raises if the stored
        config no longer matches the module's current models."""
        module.apply_persistence_snapshot(snapshot)

        # Cached as saved, so the first tick after a restore doesn't write it back.
        self._persisted[module.name] = (snapshot, datetime.now())
        logger.info(
            "Restored config for module %s (mode: %s)",
            module.name,
            snapshot.control_mode,
        )

    async def _load_snapshot(
        self, module_name: str
    ) -> ModulePersistenceSnapshot | None:
        """Load a stored configuration snapshot for the module from the persistence
        engine. Returns None if no snapshot is found. Raises if the persistence engine
        itself fails, unless the stored row is corrupt (fails validation) and
        `apply_module_defaults_on_corrupt_database` is set, in which case it degrades
        that one module to defaults instead."""
        try:
            is_stored = await self._persistence_engine.load(module_name)
        except ValidationError:
            if not self._apply_module_defaults_on_corrupt_database:
                raise

            logger.exception(
                "Stored database config for module %s is corrupt (failed validation) - using defaults",
                module_name,
            )
            return None

        if is_stored is None:
            logger.info("No stored config found for module %s", module_name)

        return is_stored
