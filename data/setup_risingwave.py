import asyncio
import codecs

from config import Settings
from dotenv import load_dotenv
import psycopg
import subprocess

load_dotenv(dotenv_path=".env")

settings = Settings()

print("Risingwave: Initializing tables")

subprocess.run(["poetry", "run", "dbt", "build", "--full-refresh"], cwd="./risingwave")


async def setup_domestic_control():
    async with await psycopg.AsyncConnection.connect(settings.risingwave_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open(
                "./risingwave/scripts/domestic_control.sql", encoding="utf-8"
            ) as query:
                await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup_domestic_control())
print("Risingwave: Done")
