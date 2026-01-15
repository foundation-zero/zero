from .cli import DomesticControl
from pydantic_settings import CliApp


def run():
    CliApp.run(DomesticControl)


if __name__ == "__main__":
    run()
