from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator


@asynccontextmanager
async def control_shutdown_context(control_modules: Any) -> AsyncGenerator[None, None]:
    """Shutdown control modules after the context is exited."""
    try:
        yield
    finally:
        for module in control_modules:
            await module.control_state_logger.shutdown()
