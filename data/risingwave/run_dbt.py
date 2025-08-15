import asyncio
import codecs

from config import Settings
from dotenv import load_dotenv
import psycopg
import subprocess

settings = Settings()

load_dotenv(dotenv_path=".env")

subprocess.run(["poetry", "run", "dbt", "compile"])

subprocess.run(["poetry", "run", "dbt", "run", "--full-refresh"])


async def setup_domestic_control():
    async with await psycopg.AsyncConnection.connect(settings.risingwave_url) as conn:
        async with conn.cursor() as cur:
            with codecs.open(
                "./scripts/domestic_control.sql", encoding="utf-8"
            ) as query:
                await cur.execute(bytes(query.read(), "utf-8"))


if __name__ == "__main__":
    asyncio.run(setup_domestic_control())
