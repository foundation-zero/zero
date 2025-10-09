import asyncio
import codecs
from glob import glob

import psycopg
from dotenv import load_dotenv

from config import Settings

load_dotenv(dotenv_path=".env")

settings = Settings()

print(f"Postgres: Initializing tables to Postgres: {settings.pg_host}:{settings.pg_port}/{settings.pg_db}")


async def setup():
    async with await psycopg.AsyncConnection.connect(settings.pg_url) as conn:
        async with conn.cursor() as cur:
            files = sorted(glob("./postgres/*.sql"))
            for file in files:
                with codecs.open(
                    file, encoding="utf-8"
                ) as query:
                    await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup())
print("Postgres: Done")
