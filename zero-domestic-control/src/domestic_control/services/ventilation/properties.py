from abc import ABC, abstractmethod
from dataclasses import dataclass

from domestic_control.messages import Ventilation


class VentilationProperty(ABC):
    value: float

    @staticmethod
    @abstractmethod
    def get(room: Ventilation) -> float | None: ...

    @abstractmethod
    def set(self, room: Ventilation): ...


@dataclass
class VentilationUpdate:
    room: str
    value: VentilationProperty


@dataclass
class ActualCo2(VentilationProperty):
    value: float

    @staticmethod
    def get(room: Ventilation) -> float | None:
        return room.actual_co2

    def set(self, room: Ventilation):
        room.actual_co2 = self.value


@dataclass
class Co2Setpoint(VentilationProperty):
    value: float

    @staticmethod
    def get(room: Ventilation) -> float | None:
        return room.co2_setpoint

    def set(self, room: Ventilation):
        room.co2_setpoint = self.value
