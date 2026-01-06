from pydantic_settings import CliApp

from .cli import ZeroLoads


def run_app():
    CliApp.run(ZeroLoads)


if __name__ == "__main__":
    run_app()
