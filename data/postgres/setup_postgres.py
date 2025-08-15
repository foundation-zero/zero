import codecs
import asyncio
import psycopg

from config import Settings
import logging
from dotenv import load_dotenv

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
