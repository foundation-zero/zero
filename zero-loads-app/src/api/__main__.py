from pydantic_settings import CliApp

from .cli import ZeroLoads

if __name__ == "__main__":
    CliApp.run(ZeroLoads)
