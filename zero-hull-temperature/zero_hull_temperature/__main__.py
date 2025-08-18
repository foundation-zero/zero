from pydantic_settings import CliApp

from zero_hull_temperature.cli import ZeroHullTemperature

if __name__ == "__main__":
    CliApp.run(ZeroHullTemperature)
