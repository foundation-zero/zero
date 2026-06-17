from pydantic_settings import CliApp

from .cli import THRS_cli


def run_app():
    CliApp.run(THRS_cli)


if __name__ == "__main__":
    run_app()
