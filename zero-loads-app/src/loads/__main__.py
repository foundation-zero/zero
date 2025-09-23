from pydantic_settings import CliApp

from .cli import ZeroLoads


def run():
    CliApp.run(ZeroLoads)


if __name__ == "__main__":
    run()
