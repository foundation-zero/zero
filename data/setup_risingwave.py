import asyncio
import codecs

from config import Settings
from dotenv import load_dotenv
import psycopg
import subprocess
import argparse
from glob import glob

load_dotenv(dotenv_path=".env")

settings = Settings()  # type:ignore

parser = argparse.ArgumentParser(description="Setup Risingwave tables", add_help=True)
parsed_args, dbt_args = parser.parse_known_args()

subprocess.run(["poetry", "run", "dbt", "build"] + dbt_args, cwd="./risingwave")

print("Risingwave: Initializing tables")


async def setup_domestic_control():
    async with await psycopg.AsyncConnection.connect(settings.risingwave_url) as conn:
        async with conn.cursor() as cur:
            files = sorted(glob("./risingwave/scripts/*.sql"))
            for file in files:
                with codecs.open(file, encoding="utf-8") as query:
                    await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup_domestic_control())


print("Risingwave: Generate model documentation")

subprocess.run(["poetry", "run", "dbt", "docs", "generate"], cwd="./risingwave")


print("Risingwave: Done")
