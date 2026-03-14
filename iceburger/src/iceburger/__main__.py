from iceburger.iceburger import Iceburger
from iceburger.settings import Config, Settings
from pydantic_settings import BaseSettings, CliApp
import yaml
from iceburger.logging import setup_logging


class Run(BaseSettings):
    async def cli_cmd(self):
        settings = Settings()  # type: ignore
        with open(settings.config_path, "r") as f:
            config_data = yaml.safe_load(f)
            config = Config.model_validate(config_data)
        iceburger = await Iceburger.from_settings(settings, config)
        await iceburger.run()


if __name__ == "__main__":
    setup_logging()
    CliApp.run(Run)
