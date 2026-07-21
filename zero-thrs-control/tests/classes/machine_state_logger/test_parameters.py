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
    assert model.parameters_to == initial.model_dump(mode="json")


def test_log_parameters_on_change_logs_diff(
    service: MachineStateLoggingService, mock_session: Mock
) -> None:
    values_from = DummyThrsValues(flow=1.0)
    values_to = DummyThrsValues(flow=2.0)

    service.log_parameters_on_change(values_from, values_to)

    model = added_model(mock_session)
    assert isinstance(model, MachineStateParametersUpdate)
    assert model.data_container_name == "DummyThrsValues"
    assert model.parameters_from == values_from.model_dump(mode="json")
    assert model.parameters_to == values_to.model_dump(mode="json")
    assert model.parameters_diff is not None
    assert set(model.parameters_diff.keys()) == {"flow"}
    assert model.parameters_diff["flow"] == {"from": 1.0, "to": 2.0}


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
