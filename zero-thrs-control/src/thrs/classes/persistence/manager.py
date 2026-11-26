import logging
from datetime import datetime, timedelta

from thrs.classes.persistence.engine import PersistentEngine
from thrs.classes.persistence.module_snapshot import ModulePersistenceSnapshot
from thrs.control.state import ControlState

logger: logging.Logger = logging.getLogger(__name__)


class PersistManager:
    """Loads module configuration on start and writes it back on change, with a
    periodic heartbeat."""

    def __init__(
        self,
        persistence_engine: PersistentEngine,
        heartbeat: timedelta = timedelta(seconds=60),
    ) -> None:
        self._persistence_engine = persistence_engine
        self._heartbeat = heartbeat
        # Last snapshot loaded or saved per module, and when.
        self._persisted: dict[str, tuple[ModulePersistenceSnapshot, datetime]] = {}

    async def load(self, module_name: str) -> ModulePersistenceSnapshot | None:
        """The module's stored configuration, if there is one. Raises if the
        persistence engine fails or the stored row doesn't validate."""
        snapshot = await self._persistence_engine.load(module_name)
        if snapshot is None:
            logger.info("No stored config found for module %s", module_name)
            return None

        # Cached as saved, so the first tick after loading doesn't write it back.
        self._persisted[module_name] = (snapshot, datetime.now())
        logger.info(
            "Loaded config for module %s (mode: %s)",
            module_name,
            snapshot.control_mode,
        )
        return snapshot

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
