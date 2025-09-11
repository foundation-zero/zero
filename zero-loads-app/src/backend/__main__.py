from pydantic_settings import CliApp

from .cli import ZeroLoadsBackend

if __name__ == "__main__":
    CliApp.run(ZeroLoadsBackend)
