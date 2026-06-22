from pydantic_settings import CliApp

from zero_termodinamica.cli import ZeroTermodinamica

if __name__ == "__main__":
    CliApp.run(ZeroTermodinamica)
