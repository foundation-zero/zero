from typing import Any


class Control:
    def __init__(self) -> None:
        pass

    def control(
        self, current_parameters: dict[str, Any], current_sensor_values: dict[str, Any]
    ) -> dict[str, Any]:
        return {}
