import asyncio
import logging
from .adapter import PCanAdapter
from .config import Settings
from .logging import setup_logging
from .stub.pcan import PCanStub

setup_logging(logging.DEBUG)

settings = Settings()


async def read():
    async with PCanAdapter.init_from_settings(settings) as adapter:
        await adapter.run()

async def stub():



if __name__ == "__main__":
    asyncio.run(read())
