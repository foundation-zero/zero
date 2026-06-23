from enum import Enum


class CLIRunnerMode(Enum):
    NORMAL = "normal"
    LOCKSTEP = "lockstep"


class SimulationMode(Enum):
    ADSORPTION = "adsorption"
    CONSUMERS = "consumers"
    DC = "DC"
    DHW = "dhw"
    DRIVERS = "drivers"
    HT = "ht"
    PCM = "pcm"
    PVT = "pvt"
    THRUSTER = "thruster"


class ControlMode(Enum):
    ADSORPTION = "adsorption"
    CONSUMERS = "consumers"
    CONVERTERS = "converters"
    DC = "DC"
    DRIVERS = "drivers"
    PCM = "pcm"
    PVT_GROUP = "pvt_group"
    PVT = "pvt"
    DHW = "dhw"
    THRUSTER = "thruster"

class CommConnectorMode(Enum):
    MQTT = "mqtt"
    MEMORY = "memory"
