from pydantic_settings import CliApp

from .cli import ZeroLoadsAdapter


def run():
    CliApp.run(ZeroLoadsAdapter)


if __name__ == "__main__":
    run()
