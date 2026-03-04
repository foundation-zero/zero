from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.alias_generators import to_pascal
from typing import Annotated, Any
import random

from datetime import UTC, datetime

from zero_data.data_gen import Generator
from zero_data.io_list.types import IOTopic, IOValue


class MarpowerStruct[T](BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_pascal)
    value: T
    timestamp: Annotated[datetime, Field(alias="TimeStamp")]
    is_valid: bool = True
    has_value: bool = True


class MarpowerGenerator(Generator):
    def get_topic(self, topic: IOTopic):
        return topic.topic.removeprefix("marpower/")

    def serialize_message(self, message):
        return TypeAdapter(dict[str, dict[str, Any]]).dump_json(message, by_alias=True)

    def generate_random_value(self, field: IOValue):
        return self._random_message(field.data_type).model_dump(by_alias=True)

    def _random_message(self, data_type: str) -> MarpowerStruct:
        """Generate a random value based on the data type."""
        match data_type:
            case "BOOLEAN":
                return self._generate_marpower_struct(
                    random.choice([True, False]),
                )
            case "REAL":
                return self._generate_marpower_struct(
                    random.normalvariate(mu=10, sigma=1.0)
                )
            case "BIGINT":
                return self._generate_marpower_struct(random.randint(0, 100))
            case "INTEGER":
                return self._generate_marpower_struct(
                    random.binomialvariate(n=10, p=0.5)
                )
            case "TIMESTAMP":
                return self._generate_marpower_struct(datetime.now(tz=UTC))
            case "STRING":
                return self._generate_marpower_struct(
                    "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
                )
        raise KeyError(f"Unknown type: {data_type}")

    def _generate_marpower_struct[T](self, value: T) -> MarpowerStruct[T]:
        return MarpowerStruct[T](
            value=value, timestamp=datetime.now(tz=UTC), is_valid=True, has_value=True
        )
