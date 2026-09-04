from pydantic_settings import CliApp

from zero_atpx_nmea.cli import ZeroAtpxNmea

if __name__ == "__main__":
    CliApp.run(ZeroAtpxNmea)
