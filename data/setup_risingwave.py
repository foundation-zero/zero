import asyncio
import codecs

from config import Settings
from dotenv import load_dotenv
import psycopg
import subprocess
import argparse
from glob import glob

load_dotenv(dotenv_path=".env")

settings = Settings()

print("Risingwave: Initializing tables")

parser = argparse.ArgumentParser(description="Setup Risingwave tables")
parser.add_argument("--upgrade", action="store_true", help="Upgrade tables if set")
args = parser.parse_args()

if args.upgrade:
    print("Risingwave: Upgrade option enabled")
    subprocess.run(["poetry", "run", "dbt", "build"], cwd="./risingwave")
else:
    subprocess.run(
        ["poetry", "run", "dbt", "build", "--full-refresh"], cwd="./risingwave"
    )


async def setup_domestic_control():
    async with await psycopg.AsyncConnection.connect(settings.risingwave_url) as conn:
        async with conn.cursor() as cur:
            files = sorted(glob("./risingwave/scripts/*.sql"))
            for file in files:
                with codecs.open(file, encoding="utf-8") as query:
                    await cur.execute(bytes(query.read(), "utf-8"))


asyncio.run(setup_domestic_control())
print("Risingwave: Done")
