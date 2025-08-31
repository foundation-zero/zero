import asyncio
import logging
from adapter import PCanAdapter


logging.basicConfig(level=logging.DEBUG)

adapter = PCanAdapter(localIP="127.0.0.1", localPort=55001)


async def read():
    logging.info("Read")
    message = await adapter.read()
    logging.info("Received message:", message)


asyncio.run(read())
