from abc import ABC, abstractmethod
from dataclasses import dataclass

from domestic_control.messages import AirConditioning


class AcProperty(ABC):
    value: float

    @staticmethod
    @abstractmethod
    def get(room: AirConditioning) -> float | None: ...

    @abstractmethod
    def set(self, room: AirConditioning): ...


@dataclass
class AcUpdate:
    room: str
    value: AcProperty


@dataclass
class AcTempChange:
    room: str
    temperature: float


@dataclass
class ActualTemperature(AcProperty):
    value: float

    @staticmethod
    def get(room: AirConditioning) -> float | None:
        return room.actual_temperature

    def set(self, room: AirConditioning):
        room.actual_temperature = self.value


@dataclass
class TemperatureSetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: AirConditioning) -> float | None:
        return room.temperature_setpoint

    def set(self, room: AirConditioning):
        room.temperature_setpoint = self.value


@dataclass
class ActualHumidity(AcProperty):
    value: float

    @staticmethod
    def get(room: AirConditioning) -> float | None:
        return room.actual_humidity

    def set(self, room: AirConditioning):
        room.actual_humidity = self.value


@dataclass
class HumiditySetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: AirConditioning) -> float | None:
        return room.humidity_setpoint

    def set(self, room: AirConditioning):
        room.humidity_setpoint = self.value
