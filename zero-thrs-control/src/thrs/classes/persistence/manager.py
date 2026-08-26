import logging
import os
from collections.abc import Iterable
from datetime import datetime, timedelta
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from thrs.classes.persistence.engine import PersistentEngine
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.orchestration.module import Module

logger: logging.Logger = logging.getLogger(__name__)


class PersistManager:
    """Restores module configuration on start and writes it back on change, with a
    periodic heartbeat."""

    def __init__(
        self,
        persistence_engine: PersistentEngine,
        heartbeat: timedelta = timedelta(seconds=60),
    ) -> None:
        self._persistence_engine = persistence_engine
        self._heartbeat = heartbeat
        self._persisted: dict[str, ModulePersistenceSnapshot] = {}
        self._persisted_at: dict[str, datetime] = {}

    async def restore(self, module: Module) -> bool:
        """Retrieve the module configuration from the persistence engine and apply it to the module.
        Returns True if a restore was performed."""

        logger.debug("Persistence restoring config for module %s", module.name)
        stored = await self._load_snapshot(module.name)

        if stored is not None:
            logger.debug(
                "Persistence applying stored config for module %s", module.name
            )
            return self._apply_snapshot(module, stored)

        return False

    async def restore_all(self, modules: Iterable[Module]) -> None:
        """Restore all modules from the persistence engine."""
        for module in modules:
            await self.restore(module)

    async def persist(self, module: Module) -> bool:
        """Write the module configuration if it changed or the heartbeat expired.
        Returns whether a write was performed."""

        logger.debug("Persisting config for module %s", module.name)
        snapshot: ModulePersistenceSnapshot = module.get_persistence_snapshot()

        is_saved = await self._save_snapshot(module.name, snapshot)

        if is_saved:
            logger.debug("Saved config for module %s", module.name)
            self._save_to_cache(module.name, snapshot)

        return is_saved

    async def _save_snapshot(
        self, module_name: str, snapshot: ModulePersistenceSnapshot
    ) -> bool:
        """Save the module configuration to the persistence engine if it changed or the heartbeat expired.
        Returns True if a write was performed."""
        if not self._require_save(module_name, snapshot):
            return False

        try:
            await self._persistence_engine.save(module_name, snapshot)
        except SQLAlchemyError:
            logger.exception("Could not persist config for module %s", module_name)
            return False

        return True

    async def persist_all(self, modules: Iterable[Module]) -> None:
        """Persist all modules, per module is checked if it changed or the heartbeat expired."""
        for module in modules:
            await self.persist(module)

    def _require_save(
        self, module_name: str, snapshot: ModulePersistenceSnapshot
    ) -> bool:
        """Check if the module configuration has changed or the heartbeat expired."""
        persisted_at: datetime | None = self._persisted_at.get(module_name)

        if persisted_at is None:
            return True

        persisted_snapshot = self._persisted.get(module_name)
        if (
            persisted_snapshot is None
            or not persisted_snapshot.equals_ignoring_timestamps(snapshot)
        ):
            return True

        return datetime.now() - persisted_at >= self._heartbeat

    def _save_to_cache(
        self, module_name: str, snapshot: ModulePersistenceSnapshot
    ) -> None:
        """Save the snapshot to the in-memory cache. Used for comparison on a subsequent persist call to avoid unnecessary writes."""
        self._persisted[module_name] = snapshot
        self._persisted_at[module_name] = datetime.now()

    def _apply_snapshot(
        self, module: Module, snapshot: ModulePersistenceSnapshot
    ) -> bool:
        """Apply a stored configuration snapshot to the module. Returns True if applied successfully."""
        try:
            module.apply_persistence_snapshot(snapshot)
        except ValidationError:
            logger.exception(
                "Stored config for module %s does not match the current models, keeping defaults",
                module.name,
            )
            return False

        # Save to cache, so on a subsequent persist call, the snapshot can be compared to avoid unnecessary writes only if the module configuration has changed.
        self._save_to_cache(module.name, module.get_persistence_snapshot())
        logger.info(
            "Restored config for module %s (mode: %s)",
            module.name,
            snapshot.control_mode,
        )
        return True

    async def _load_snapshot(
        self, module_name: str
    ) -> ModulePersistenceSnapshot | None:
        """Load a stored configuration snapshot for the module from the persistence engine. Returns None if no snapshot is found or if an error occurred during loading."""
        try:
            is_stored = await self._persistence_engine.load(module_name)
        except SQLAlchemyError:
            logger.exception("Unable to load stored config for module %s", module_name)
            return None

        if is_stored is None:
            logger.info("No stored config found for module %s", module_name)

        return is_stored
