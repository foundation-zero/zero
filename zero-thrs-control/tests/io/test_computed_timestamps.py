import random
from datetime import UTC, datetime
from typing import Any

import pytest

from thrs.control.modules.adsorption.io import AdsorptionSensorValues
from thrs.control.modules.consumers.io import ConsumersSensorValues
from thrs.control.modules.dc.io import DcSensorValues
from thrs.control.modules.dhw.io import DhwSensorValues
from thrs.control.modules.drives.io import DrivesSensorValues
from thrs.control.modules.pcm.io import PcmSensorValues
from thrs.control.modules.pvt.io import PvtSensorValues
from thrs.control.modules.thrusters.io import ThrustersSensorValues
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import sensor

SENSOR_TIME = datetime(2026, 1, 1, tzinfo=UTC)
VALVE_POSITIONS = (0.0, 0.5, 1.0)
SAMPLES = 500


def _stamp_inputs(values: ThrsValues) -> None:
    for name in type(values).model_fields:
        field = getattr(values, name)
        if isinstance(field, Stamped):
            field.timestamp = SENSOR_TIME
        elif isinstance(field, ThrsValues):
            _stamp_inputs(field)


def _timestamps(dumped: Any) -> set[datetime]:
    if isinstance(dumped, dict):
        return {
            timestamp
            for key, value in dumped.items()
            for timestamp in ({value} if key == "timestamp" else _timestamps(value))
        }
    if isinstance(dumped, list | tuple):
        return {timestamp for item in dumped for timestamp in _timestamps(item)}
    return set()


@pytest.mark.parametrize(
    "sensor_values_cls",
    [
        AdsorptionSensorValues,
        ConsumersSensorValues,
        DcSensorValues,
        DhwSensorValues,
        DrivesSensorValues,
        PcmSensorValues,
        PvtSensorValues,
        ThrustersSensorValues,
    ],
)
def test_computed_values_take_timestamps_from_their_inputs(
    sensor_values_cls: type[ThrsValues],
):
    sensor_values = sensor_values_cls.zero()
    _stamp_inputs(sensor_values)
    valves = [
        getattr(sensor_values, name)
        for name, field in type(sensor_values).model_fields.items()
        if field.annotation is sensor.Valve
    ]

    rng = random.Random(0)  # noqa: S311
    for _ in range(SAMPLES):
        for valve in valves:
            valve.position_rel.value = rng.choice(VALVE_POSITIONS)

        assert _timestamps(sensor_values.model_dump()) == {SENSOR_TIME}
