from pydantic_settings import CliApp

from .cli import ThrsCli


def run_app():
    CliApp.run(ThrsCli)


if __name__ == "__main__":
    run_app()
