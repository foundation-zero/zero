from pydantic import BaseModel


class MqttValue(BaseModel):
    value: bool

class TemperatureReading(BaseModel):
    sensor: str
    temperature: float

class Temperatures(BaseModel):
    temperatures: list[TemperatureReading]
