from pydantic_settings import CliApp

from .cli import ZeroLoadsControl


def run():
    CliApp.run(ZeroLoadsControl)


if __name__ == "__main__":
    run()
