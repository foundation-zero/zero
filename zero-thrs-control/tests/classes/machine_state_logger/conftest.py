from unittest.mock import Mock

import pytest
from sqlmodel import SQLModel
from transitions import State

from thrs.classes.machine_state_logger import (
    MachineStateLogger,
    MachineStateLoggingService,
)
from thrs.input_output.base import ThrsValues


class DummyThrsValues(ThrsValues):
    flow: float = 1.0
    setpoint: float = 50.0


class AnotherDummyThrsValues(ThrsValues):
    temperature: float = 1.0


class DummyControl:
    state: str

    def __init__(self) -> None:
        self.condition_dummy_trigger_result: bool = True

    def condition_dummy_trigger(self, sensor_values: object) -> bool:
        return self.condition_dummy_trigger_result


def make_transitions() -> list[dict]:
    return [
        {
            "trigger": "dummy_trigger",
            "source": "idle",
            "dest": "running",
            "conditions": "condition_dummy_trigger",
        }
    ]


def make_states() -> list[State]:
    return [State("idle"), State("running")]


def added_model(mock_session: Mock) -> SQLModel:
    mock_session.add.assert_called_once()
    return mock_session.add.call_args.args[0]


@pytest.fixture
def logger(postgres_db: Mock) -> MachineStateLogger:
    return MachineStateLogger(postgres_db)


@pytest.fixture
def service(postgres_db: Mock) -> MachineStateLoggingService:
    return MachineStateLoggingService(postgres_db)
