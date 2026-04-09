from typing import Sequence

from loads.sensors import LoadsModel

from .registry import AT_MODELS, FIBER_OPTIC_MODELS, SAIL_SYSTEM_MODELS


class MessagingModule:
    """Module handling one source of MQTT messages"""

    def __init__(self, models: Sequence[type[LoadsModel]], display_name: str) -> None:
        self.display_name = display_name
        self._models = models
        self._mapping = {model.TOPIC: model for model in models}

    @property
    def topics(self) -> list[str]:
        return list(self._mapping.keys())

    def gen_config(self):
        return [model.gen_config() for model in self._models]


sail_system_sensors = MessagingModule(
    models=SAIL_SYSTEM_MODELS, display_name="sail_system_sensors"
)

at_sensors = MessagingModule(models=AT_MODELS, display_name="at_sensors")

fiber_optic_sensors = MessagingModule(
    models=FIBER_OPTIC_MODELS, display_name="fiber_optic_sensors"
)
