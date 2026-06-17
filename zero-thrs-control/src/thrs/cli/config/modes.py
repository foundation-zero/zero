from enum import Enum


class RunnerMode(Enum):
    NORMAL = "normal"
    LOCKSTEP = "lockstep"


class SimulationMode(Enum):
    THRUSTER = "thruster"
    BOILER = "boiler"


class CommConnectorMode(Enum):
    MQTT = "mqtt"
    MEMORY = "memory"
