import asyncio
import codecs
from glob import glob

import psycopg
from dotenv import load_dotenv

from config import Settings
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("setup_postgres")

load_dotenv(dotenv_path=".env")

settings = Settings()  # type: ignore


logger.info(settings)
print(f"Postgres: Initializing tables to Postgres: {settings.pg_host}:{settings.pg_port}/{settings.pg_db}")


async def setup():
    async with await psycopg.AsyncConnection.connect(settings.pg_url) as conn:
        async with conn.cursor() as cur:
            files = sorted(glob("./postgres/*.sql"))
            for file in files:
                with codecs.open(file, encoding="utf-8") as query:
                    await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup())
print("Postgres: Done")
