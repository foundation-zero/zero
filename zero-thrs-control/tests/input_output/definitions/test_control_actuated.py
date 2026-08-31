import json

import pytest
from pydantic import ValidationError

from thrs.input_output.base import Stamped
from thrs.input_output.definitions.control import Pump, Valve
from thrs.input_output.definitions.wire_context import (
    AMCS_RECEIVE_CONTEXT,
    AMCS_WRITE_CONTEXT,
)


def _stamped(value: float | bool) -> dict:
    return {"Value": value, "TimeStamp": "2026-01-01T00:00:00Z"}


# (model, field name, plain-key payload, CC_-key payload)
ACTUATED_CASES = [
    pytest.param(
        Pump,
        "dutypoint",
        {"Dutypoint": _stamped(0.4), "On": _stamped(True)},
        {"CC_Dutypoint": _stamped(0.4), "On": _stamped(True)},
        id="pump",
    ),
    pytest.param(
        Valve,
        "setpoint",
        {"Setpoint": _stamped(0.4)},
        {"CC_Setpoint": _stamped(0.4)},
        id="valve",
    ),
]


def _control_value(model_cls, field_name: str, value: float):
    if model_cls is Pump:
        return Pump(dutypoint=Stamped.stamp(value), on=Stamped.stamp(True))
    return Valve(setpoint=Stamped.stamp(value))


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_amcs_receive_validation_reads_cc_keys(
    model_cls, field_name, plain_payload, cc_payload
):
    model = model_cls.model_validate_json(
        json.dumps(cc_payload), context=AMCS_RECEIVE_CONTEXT
    )

    assert getattr(model, field_name).value == 0.4


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_amcs_receive_validation_rejects_plain_actuated_keys(
    model_cls, field_name, plain_payload, cc_payload
):
    # A plain actuated key is a command echo, not an actuated value: it must
    # not complete the actuated model.
    with pytest.raises(ValidationError):
        model_cls.model_validate_json(
            json.dumps(plain_payload), context=AMCS_RECEIVE_CONTEXT
        )


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_amcs_receive_serialization_writes_cc_keys(
    model_cls, field_name, plain_payload, cc_payload
):
    # The simulation mimics the AMCS and publishes with this context.
    payload = json.loads(
        _control_value(model_cls, field_name, 0.5).model_dump_json(
            by_alias=True, context=AMCS_RECEIVE_CONTEXT
        )
    )

    assert set(payload) == set(cc_payload)


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_simulation_to_amcs_receive_roundtrip(
    model_cls, field_name, plain_payload, cc_payload
):
    wire = _control_value(model_cls, field_name, 0.5).model_dump_json(
        by_alias=True, context=AMCS_RECEIVE_CONTEXT
    )
    received = model_cls.model_validate_json(wire, context=AMCS_RECEIVE_CONTEXT)

    assert getattr(received, field_name).value == 0.5


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_amcs_write_validation_reads_plain_keys(
    model_cls, field_name, plain_payload, cc_payload
):
    model = model_cls.model_validate_json(
        json.dumps(plain_payload), context=AMCS_WRITE_CONTEXT
    )

    assert getattr(model, field_name).value == 0.4


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_amcs_write_serialization_writes_plain_keys(
    model_cls, field_name, plain_payload, cc_payload
):
    payload = json.loads(
        _control_value(model_cls, field_name, 0.5).model_dump_json(
            by_alias=True, context=AMCS_WRITE_CONTEXT
        )
    )

    assert set(payload) == set(plain_payload)
    assert not any(key.startswith("CC_") for key in payload)


@pytest.mark.parametrize(
    ("model_cls", "field_name", "plain_payload", "cc_payload"), ACTUATED_CASES
)
def test_internal_send_to_amcs_write_roundtrip(
    model_cls, field_name, plain_payload, cc_payload
):
    wire = _control_value(model_cls, field_name, 0.5).model_dump_json(by_alias=True)
    received = model_cls.model_validate_json(wire, context=AMCS_WRITE_CONTEXT)

    assert getattr(received, field_name).value == 0.5
