import json
from unittest.mock import Mock

import pytest

from tests.classes.machine_state_logger.conftest import (
    AnotherDummyThrsValues,
    DummyThrsValues,
    added_model,
)
from thrs.classes.machine_state_logger import MachineStateLoggingService
from thrs.db.models.machine_state import MachineStateParametersUpdate


def test_log_parameters_initial_state(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    initial = DummyThrsValues()

    service.log_parameters_initial_state(initial)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateParametersUpdate)
    assert model.control_name == "MachineStateLoggingService"
    assert model.data_container_name == "DummyThrsValues"
    assert model.parameters_from is None
    assert model.parameters_diff is None
    assert json.loads(model.parameters_to) == json.loads(initial.model_dump_json())


def test_log_parameters_on_change_logs_diff(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    values_from = DummyThrsValues(flow=1.0)
    values_to = DummyThrsValues(flow=2.0)

    service.log_parameters_on_change(values_from, values_to)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateParametersUpdate)
    assert model.data_container_name == "DummyThrsValues"
    assert json.loads(model.parameters_from or "") == json.loads(
        values_from.model_dump_json()
    )
    assert json.loads(model.parameters_to) == json.loads(values_to.model_dump_json())
    assert model.parameters_diff is not None
    diff: dict = json.loads(model.parameters_diff)
    assert set(diff.keys()) == {"flow"}


def test_log_parameters_on_change_skips_equal_values(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    service.log_parameters_on_change(DummyThrsValues(), DummyThrsValues())

    mock_session.add.assert_not_called()


def test_log_parameters_on_change_rejects_different_types(
    service: MachineStateLoggingService,
) -> None:
    with pytest.raises(ValueError, match="same type"):
        service.log_parameters_on_change(DummyThrsValues(), AnotherDummyThrsValues())
