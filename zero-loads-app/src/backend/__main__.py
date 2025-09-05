import asyncio
import logging
from .adapter import PCanAdapter
from .config import Settings
from .logging import setup_logging
from .stub import PCanStub

# For development
setup_logging(logging.DEBUG)

settings = Settings()


async def adapter():
    async with PCanAdapter.init_from_settings(settings) as adapter:
        await adapter.run()


async def stub():
    async with PCanStub.init_from_settings(settings) as stub:
        await stub.run()


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(adapter())
        tg.create_task(stub())


if __name__ == "__main__":
    asyncio.run(main())
