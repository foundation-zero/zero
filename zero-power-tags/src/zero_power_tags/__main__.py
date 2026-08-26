from pydantic_settings import CliApp

from zero_power_tags.cli import ZeroPowerTags

if __name__ == "__main__":
    CliApp.run(ZeroPowerTags)
