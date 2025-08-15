import asyncio
import codecs
import logging

import psycopg
from dotenv import load_dotenv

from config import Settings

load_dotenv(dotenv_path=".env")

settings = Settings()

logging.info("Initializing postgres tables")

print(settings)


async def setup():
    async with await psycopg.AsyncConnection.connect(settings.pg_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open(
                "./postgres/domestic_control.sql", encoding="utf-8"
            ) as query:
                await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup())
