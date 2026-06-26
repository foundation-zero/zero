import asyncio
import sys

from pydantic_settings import CliApp

from zero_termodinamica.cli import ZeroTermodinamica

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    CliApp.run(ZeroTermodinamica)
