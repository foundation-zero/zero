from collections.abc import AsyncGenerator, Iterable
from contextlib import asynccontextmanager

from thrs.orchestration.module import Module


@asynccontextmanager
async def control_shutdown_context(
    control_modules: Iterable[Module],
) -> AsyncGenerator[None, None]:
    """Shutdown control modules after the context is exited."""
    try:
        yield
    finally:
        for module in control_modules:
            await module.control_state_logger.shutdown()
