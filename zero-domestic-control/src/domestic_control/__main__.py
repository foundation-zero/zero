from pydantic_settings import CliApp

from .cli import DomesticControl


def run():
    CliApp.run(DomesticControl)


if __name__ == "__main__":
    run()
