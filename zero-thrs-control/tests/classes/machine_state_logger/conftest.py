from unittest.mock import Mock

import pytest
from sqlmodel import SQLModel
from transitions import State

from thrs.classes.machine_state_logger import (
    MachineStateLogger,
    MachineStateLoggingService,
    MachineStateLoggingServiceNoop,
    StateLogger,
)
from thrs.input_output.base import ThrsValues


class DummyThrsValues(ThrsValues):
    flow: float = 1.0
    setpoint: float = 50.0


class AnotherDummyThrsValues(ThrsValues):
    temperature: float = 1.0


class DummyControl:
    state: str = "unknown"

    def __init__(self) -> None:
        self.condition_dummy_trigger_result: bool = True
        self._parameters: DummyThrsValues = DummyThrsValues()
        self.state_logger: StateLogger = MachineStateLoggingServiceNoop()

    def condition_dummy_trigger(self, sensor_values: object) -> bool:
        return self.condition_dummy_trigger_result

    def initial(self) -> tuple[DummyThrsValues, DummyThrsValues]:
        return (DummyThrsValues(), DummyThrsValues())

    def control(
        self, sensor_values: DummyThrsValues
    ) -> tuple[DummyThrsValues, DummyThrsValues]:
        return (DummyThrsValues(), DummyThrsValues())

    @property
    def parameters(self) -> DummyThrsValues:
        return self._parameters

    @property
    def mode(self) -> DummyThrsValues | None:
        return None

    def update_parameters(self, parameters: DummyThrsValues) -> None:
        self._parameters = parameters


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
