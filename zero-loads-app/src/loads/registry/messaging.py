from typing import Sequence

from loads.registry.registry import AT_MODELS, SAIL_SYSTEM_MODELS
from loads.sensors import LoadsModel


class MessagingModule:
    """Module handling one source of MQTT messages"""

    def __init__(self, models: Sequence[type[LoadsModel]]) -> None:
        self._models = models
        self._mapping = {model.TOPIC: model for model in models}

    @property
    def topics(self) -> list[str]:
        return list(self._mapping.keys())

    def gen_config(self):
        return [model.gen_config() for model in self._models]


sail_system_sensors = MessagingModule(models=SAIL_SYSTEM_MODELS)


at_sensors = MessagingModule(models=AT_MODELS)
