from abc import ABC, abstractmethod
from dataclasses import dataclass

from zero_domestic_control.messages import (
    Room,
)


class AcProperty(ABC):
    value: float

    @staticmethod
    @abstractmethod
    def get(room: Room) -> float | None: ...

    @abstractmethod
    def set(self, room: Room): ...


@dataclass
class TermodinamicaUpdate:
    room: str
    value: AcProperty


### TEMPERATURE ###
@dataclass
class AcTempChange:
    room: str
    temperature: float


@dataclass
class ActualTemperature(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.actual_temperature

    def set(self, room: Room):
        room.actual_temperature = self.value


@dataclass
class TemperatureSetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.temperature_setpoint

    def set(self, room: Room):
        room.temperature_setpoint = self.value


### HUMIDITY ###
@dataclass
class ActualHumidity(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.actual_humidity

    def set(self, room: Room):
        room.actual_humidity = self.value


@dataclass
class HumiditySetpoint(AcProperty):
    value: float

    @staticmethod
    def get(room: Room) -> float | None:
        return room.humidity_setpoint

    def set(self, room: Room):
        room.humidity_setpoint = self.value
