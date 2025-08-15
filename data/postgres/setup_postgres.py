import asyncio
import codecs
import logging

import psycopg
from dotenv import load_dotenv

from config import Settings

load_dotenv(dotenv_path=".env")

settings = Settings()


async def setup():
    logging.info("Initializing postgres tables")
    async with await psycopg.AsyncConnection.connect(settings.pg_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open("./domestic_control.sql", encoding="utf-8") as query:
                await cur.execute(bytes(query.read(), "utf-8"))


if __name__ == "__main__":
    asyncio.run(setup())
