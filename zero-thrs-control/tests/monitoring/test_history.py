"""Runs the monitoring queries against a real GreptimeDB.

Start a throwaway one and point GREPTIME_TEST_URL at it, e.g.:

    docker run --rm -p 14002:4002 greptime/greptimedb:v1.1.3 standalone start --mysql-addr 0.0.0.0:4002
    GREPTIME_TEST_URL=mysql://localhost:14002/public uv run pytest tests/monitoring
"""
# ruff: noqa: S608 - the fixtures build constant SQL from module-level literals

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from secrets import token_hex

import pytest
from sqlalchemy import text

from thrs.monitoring.history import MonitoringHistory, create_engine
from thrs.monitoring.segments import Segment, merge_segments
from thrs.monitoring.sources import MonitoringMetric, MonitoringModule, MonitoringSignal

pytestmark = pytest.mark.greptime

START = datetime(2026, 11, 10, 12, tzinfo=UTC)
END = START + timedelta(hours=1)


def at(minutes: float) -> str:
    return (START + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")


SCHEMA = [
    """CREATE TABLE marpower__thrs__temperatures (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, technical_name STRING,
        yard_tag STRING, temperature__value DOUBLE, PRIMARY KEY (topic, technical_name))""",
    """CREATE TABLE marpower__thrs__pumps (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, technical_name STRING,
        yard_tag STRING, cc_on_off__value BOOLEAN, PRIMARY KEY (topic, technical_name))""",
    """CREATE TABLE thrs__controller__dhw__control_mode (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING,
        automatic_mode__boosting_mode STRING, automatic_mode__filling_mode STRING)""",
    """CREATE TABLE marpower__thrs__tank_controllers (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, technical_name STRING,
        tank_1_state__value STRING, tank_2_state__value STRING, tank_3_state__value STRING,
        PRIMARY KEY (topic, technical_name))""",
    """CREATE TABLE marpower__thrs__amcs_modes (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, technical_name STRING,
        mode__value BIGINT, PRIMARY KEY (topic, technical_name))""",
    """CREATE TABLE marpower__thrs__heat_transfers (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, technical_name STRING,
        heat__value DOUBLE, PRIMARY KEY (topic, technical_name))""",
    """CREATE TABLE marpower__500000_thrs__dhw__alarm (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, alarm__value BOOLEAN)""",
    """CREATE TABLE thrs__controller__dhw__parameters__set (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, minimum_tank_temperature DOUBLE)""",
    """CREATE TABLE thrs__controller__dhw__parameters (
        `timestamp` TIMESTAMP(9) TIME INDEX, topic STRING, minimum_tank_temperature DOUBLE)""",
]

TANK1 = "'marpower/500000-thrs/dhw/dhw-temperature-tank1', 'dhw-temperature-tank1', '50001001'"
TANK2 = "'marpower/500000-thrs/dhw/dhw-temperature-tank2', 'dhw-temperature-tank2', ''"
OTHER_MODULE = (
    "'marpower/500000-thrs/pvt/pvt-temperature', 'pvt-temperature', '50002001'"
)
PUMP = "'marpower/500000-thrs/dhw/dhw-pump', 'dhw-pump', '50001022'"
TANKS = "'thrs/controller/dhw/dhw-tanks-controller', 'dhw-tanks-controller'"
HEATPUMP_HEAT = "'thrs/controller/dhw/dhw-heatpump-heat', 'dhw-heatpump-heat'"
PVT_HEAT = "'thrs/controller/pvt/pvt-main-heat', 'pvt-main-heat'"
MODE = "'thrs/controller/dhw/control-mode'"
PARAMETERS = "'thrs/controller/dhw/parameters'"
AMCS_DHW = "'marpower/500000-thrs/dhw/mode', 'dhw-mode'"
AMCS_PVT = "'marpower/500000-thrs/pvt/mode', 'pvt-mode'"

ROWS = [
    "INSERT INTO marpower__thrs__temperatures VALUES "
    + ", ".join(
        [
            f"('{at(0)}', {TANK1}, 50.0)",
            f"('{at(0.5)}', {TANK1}, 52.0)",
            f"('{at(30)}', {TANK1}, 60.0)",
            f"('{at(10)}', {TANK2}, 40.0)",
            f"('{at(10)}', {OTHER_MODULE}, 99.0)",
            f"('{at(-10)}', {TANK1}, 10.0)",
        ]
    ),
    "INSERT INTO marpower__thrs__pumps VALUES "
    + ", ".join([f"('{at(0)}', {PUMP}, true)", f"('{at(0.5)}', {PUMP}, false)"]),
    "INSERT INTO thrs__controller__dhw__control_mode VALUES "
    + ", ".join(
        [
            f"('{at(-20)}', {MODE}, 'boosting_high_temperature', 'idle')",
            f"('{at(5)}', {MODE}, 'boosting_high_temperature', 'idle')",
            f"('{at(10)}', {MODE}, 'idle', 'filling')",
            f"('{at(20)}', {MODE}, NULL, NULL)",
            f"('{at(40)}', {MODE}, 'idle', 'idle')",
            f"('{at(58)}', {MODE}, 'idle', 'idle')",
        ]
    ),
    "INSERT INTO marpower__thrs__tank_controllers VALUES "
    + ", ".join(
        [
            f"('{at(0)}', {TANKS}, 'in use', 'filling', 'standby')",
            f"('{at(30)}', {TANKS}, 'in use', 'standby', 'standby')",
            f"('{at(50)}', {TANKS}, 'in use', 'standby', 'standby')",
        ]
    ),
    "INSERT INTO marpower__thrs__amcs_modes VALUES "
    + ", ".join(
        [
            f"('{at(-5)}', {AMCS_DHW}, 1)",
            f"('{at(30)}', {AMCS_DHW}, 3)",
            f"('{at(59)}', {AMCS_DHW}, 3)",
            f"('{at(10)}', {AMCS_PVT}, 2)",
        ]
    ),
    "INSERT INTO marpower__thrs__heat_transfers VALUES "
    + ", ".join(
        [
            f"('{at(0)}', {HEATPUMP_HEAT}, 2000.0)",
            f"('{at(0.5)}', {HEATPUMP_HEAT}, 4000.0)",
            f"('{at(10)}', {PVT_HEAT}, 9000.0)",
        ]
    ),
    "INSERT INTO marpower__500000_thrs__dhw__alarm VALUES "
    + ", ".join(
        [
            f"('{at(-5)}', 'marpower/500000-thrs/dhw/alarm', false)",
            f"('{at(10)}', 'marpower/500000-thrs/dhw/alarm', true)",
            f"('{at(11)}', 'marpower/500000-thrs/dhw/alarm', true)",
            f"('{at(20)}', 'marpower/500000-thrs/dhw/alarm', false)",
        ]
    ),
    "INSERT INTO thrs__controller__dhw__parameters__set VALUES "
    + ", ".join(
        [
            f"('{at(-600)}', 'thrs/controller/dhw/parameters/set', 51.0)",
            f"('{at(15)}', 'thrs/controller/dhw/parameters/set', 55.0)",
        ]
    ),
    "INSERT INTO thrs__controller__dhw__parameters VALUES "
    + ", ".join(
        [
            f"('{at(-2 * 24 * 60)}', {PARAMETERS}, 51.0)",
            f"('{at(15)}', {PARAMETERS}, 55.0)",
            f"('{at(59)}', {PARAMETERS}, 55.0)",
        ]
    ),
]


@pytest.fixture
async def history() -> AsyncIterator[MonitoringHistory]:
    base_url = os.environ.get("GREPTIME_TEST_URL", "mysql://localhost:14002/public")
    database = f"thrs_monitoring_test_{token_hex(4)}"
    admin = create_engine(base_url)
    engine = create_engine(f"{base_url.rsplit('/', 1)[0]}/{database}")
    try:
        async with admin.connect() as connection:
            await connection.execute(text(f"CREATE DATABASE {database}"))
        async with engine.connect() as connection:
            for statement in [*SCHEMA, *ROWS]:
                await connection.execute(text(statement))
        yield MonitoringHistory(engine)
    finally:
        await engine.dispose()
        async with admin.connect() as connection:
            await connection.execute(text(f"DROP DATABASE IF EXISTS {database}"))
        await admin.dispose()


async def test_sensor_series_bins_per_device_within_the_module(history):
    series = await history.series(
        MonitoringModule.DHW, MonitoringMetric.TEMPERATURE, START, END
    )

    assert series.unit == "°C"
    assert series.bin == timedelta(seconds=10)
    assert not series.step
    tank1, tank2 = series.devices
    assert tank1.device == "dhw-temperature-tank1"
    assert tank1.yard_tag == "50001001"
    assert tank1.values == [50.0, 52.0, 60.0]
    assert tank1.latest is not None
    assert tank1.latest.value == 60.0
    assert tank1.latest.timestamp == START + timedelta(minutes=30)
    assert tank2.yard_tag is None


async def test_sensor_series_filters_devices(history):
    series = await history.series(
        MonitoringModule.DHW,
        MonitoringMetric.TEMPERATURE,
        START,
        END,
        devices=["dhw-temperature-tank2"],
    )

    assert [device.device for device in series.devices] == ["dhw-temperature-tank2"]


async def test_boolean_sensors_average_as_integers(history):
    series = await history.series(
        MonitoringModule.DHW, MonitoringMetric.PUMP_ON_OFF, START, END
    )

    (pump,) = series.devices
    assert pump.values == [1.0, 0.0]


async def test_parameter_series_steps_from_an_opening_value_days_before(history):
    series = await history.series(
        MonitoringModule.DHW, MonitoringMetric.MINIMUM_TANK_TEMPERATURE, START, END
    )

    assert series.step
    (parameter,) = series.devices
    assert parameter.values == [51.0, 55.0, 55.0]
    assert parameter.times[0] == START
    assert parameter.times[-1] == END


async def test_mode_states_open_with_the_state_before_the_range(history):
    samples = await history.states(
        MonitoringModule.DHW, MonitoringSignal.BOOSTING_MODE, START, END
    )

    assert merge_segments(samples, START, END, null_state="manual") == [
        Segment(
            state="boosting_high_temperature",
            start=START,
            end=START + timedelta(minutes=10),
        ),
        Segment(
            state="idle",
            start=START + timedelta(minutes=10),
            end=START + timedelta(minutes=20),
        ),
        Segment(
            state="manual",
            start=START + timedelta(minutes=20),
            end=START + timedelta(minutes=40),
        ),
        Segment(state="idle", start=START + timedelta(minutes=40), end=END),
    ]


async def test_tank_states_read_their_own_column(history):
    samples = await history.states(
        MonitoringModule.DHW, MonitoringSignal.TANK_2_STATE, START, END
    )

    assert merge_segments(samples, START, END) == [
        Segment(state="filling", start=START, end=START + timedelta(minutes=30)),
        Segment(
            state="standby",
            start=START + timedelta(minutes=30),
            end=START + timedelta(minutes=50),
        ),
    ]


async def test_amcs_mode_reads_only_its_module_and_names_values(history):
    samples = await history.states(
        MonitoringModule.DHW, MonitoringSignal.AMCS_MODE, START, END
    )

    assert merge_segments(samples, START, END) == [
        Segment(state="amcs_manual", start=START, end=START + timedelta(minutes=30)),
        Segment(state="advisory", start=START + timedelta(minutes=30), end=END),
    ]


async def test_heat_comes_in_kilowatt_per_exchanger_without_yard_tag(
    history: MonitoringHistory,
):
    series = await history.series(
        MonitoringModule.DHW, MonitoringMetric.HEAT, START, END
    )
    assert series.unit == "kW"
    [heatpump] = series.devices
    assert heatpump.device == "dhw-heatpump-heat"
    assert heatpump.yard_tag is None
    assert heatpump.values == pytest.approx([2.0, 4.0])
    assert heatpump.latest is not None
    assert heatpump.latest.value == pytest.approx(4.0)


async def test_alarm_changes_open_with_the_value_before_the_range(history):
    changes = await history.alarm_changes(MonitoringModule.DHW, START, END)

    assert [(time, bool(value)) for time, value in changes][:3] == [
        (START - timedelta(minutes=5), False),
        (START + timedelta(minutes=10), True),
        (START + timedelta(minutes=20), False),
    ]


async def test_parameter_sets_start_with_the_last_set_before_the_range(history):
    sets = await history.parameter_sets(MonitoringModule.DHW, START, END)

    assert [row["minimum_tank_temperature"] for row in sets] == [51.0, 55.0]
