from abc import ABC, abstractmethod
from dataclasses import dataclass

from domestic_control.messages import AirConditioning


class AcProperty(ABC):
    value: float

    @staticmethod
    @abstractmethod
    def get(ac: AirConditioning) -> float | None: ...

    @abstractmethod
    def set(self, ac: AirConditioning): ...


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
    def get(ac: AirConditioning) -> float | None:
        return ac.actual_temperature

    def set(self, ac: AirConditioning):
        ac.actual_temperature = self.value


@dataclass
class TemperatureSetpoint(AcProperty):
    value: float

    @staticmethod
    def get(ac: AirConditioning) -> float | None:
        return ac.temperature_setpoint

    def set(self, ac: AirConditioning):
        ac.temperature_setpoint = self.value


@dataclass
class ActualHumidity(AcProperty):
    value: float

    @staticmethod
    def get(ac: AirConditioning) -> float | None:
        return ac.actual_humidity

    def set(self, ac: AirConditioning):
        ac.actual_humidity = self.value


@dataclass
class HumiditySetpoint(AcProperty):
    value: float

    @staticmethod
    def get(ac: AirConditioning) -> float | None:
        return ac.humidity_setpoint

    def set(self, ac: AirConditioning):
        ac.humidity_setpoint = self.value
