import json
from abc import ABC

from pydantic import Field

from loads.sensors.base import LoadsModel
from loads.sensors.units import Millimeter, RatioFromPerMille, TonneFromDecaKilogram


class PlcSensor(LoadsModel, ABC):
    TOPIC = "test-topic"

    load: TonneFromDecaKilogram = Field(validation_alias="load")
    position: Millimeter = Field(validation_alias="position")
    relative_position: RatioFromPerMille = Field(validation_alias="relative_position")
    lock: bool = Field(validation_alias="lock")


def test_validate_message():
    message = {
        "load": 1500,
        "position": 2000,
        "relative_position": 500,
        "lock": True,
    }
    sensor = PlcSensor.model_validate(message)
    assert sensor.load == 15.0
    assert sensor.position == 2000
    assert sensor.relative_position == 0.5
    assert sensor.lock is True


def test_generate_data():
    generated_data = json.loads(PlcSensor.make_generator().gen())

    assert isinstance(generated_data["load"], int)
    assert isinstance(generated_data["position"], int)
    assert isinstance(generated_data["relative_position"], int)
    assert isinstance(generated_data["lock"], bool)
