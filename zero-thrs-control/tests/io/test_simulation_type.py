import pytest

from thrs.runtime.descriptions.simulation import MODES, Mode

SIMULATED_MODES = [mode for mode in MODES if mode.simulation_description]


@pytest.mark.parametrize("mode", SIMULATED_MODES, ids=lambda mode: mode.name)
def test_simulation_payloads_name_their_mode(mode: Mode):
    assert mode.simulation_description
    inputs = mode.simulation_description.simulation_inputs
    outputs_cls = mode.simulation_description.simulation_outputs_cls

    assert inputs.model_dump(by_alias=True)["SimulationType"] == mode.name
    for cls in (type(inputs), outputs_cls):
        schema = cls.model_json_schema(by_alias=True, mode="serialization")
        assert schema["properties"]["SimulationType"]["const"] == mode.name
        assert "SimulationType" in schema["required"]


@pytest.mark.parametrize("mode", SIMULATED_MODES, ids=lambda mode: mode.name)
def test_simulation_inputs_read_back_with_their_simulation_type(mode: Mode):
    assert mode.simulation_description
    inputs = mode.simulation_description.simulation_inputs

    # A set echoes the published payload, SimulationType included; it is not read back.
    payload = inputs.model_dump_json(by_alias=True)
    assert type(inputs).model_validate_json(payload) == inputs
