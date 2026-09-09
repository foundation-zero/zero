"""Tests for the generated AsyncAPI spec (``thrs spec print-asyncapi``).

These guard the two properties that actually matter for a generated spec:
it must not silently drift from the real MQTT wiring in
``orchestration.comms``, and it must not silently misrepresent a payload
(the point of ``spec/asyncapi.py``'s docstring warning about same-named
classes and about send/receive sharing one address template).
"""

from typing import Any

import pytest

from thrs.input_output.definitions.sensor import Thruster as SensorThruster
from thrs.input_output.definitions.simulation import Thruster as SimulationThruster
from thrs.runtime.descriptions.simulation import MODES
from thrs.spec.asyncapi import (
    DEFAULT_CONFIG,
    _classifier,
    _collect_registrations,
    _combined_schemas,
    _flatten,
    _group,
    all_module_descriptions,
    build_asyncapi,
    describe_mapping,
)


def test_all_module_descriptions_is_the_union_of_every_mode() -> None:
    """``all_module_descriptions`` takes a shortcut (mode "thrs" alone)
    instead of walking every mode in ``MODES``. This is what proves that
    shortcut stays correct as modes are added or changed."""
    union: dict[str, Any] = {}
    for mode in MODES:
        union.update(mode.control_modules)

    assert set(all_module_descriptions()) == set(union)
    for name, description in union.items():
        assert all_module_descriptions()[name] is description


def test_build_asyncapi_has_no_broken_refs() -> None:
    doc = build_asyncapi()

    def walk(node: Any, path: str) -> list[tuple[str, str]]:
        broken: list[tuple[str, str]] = []
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    if _resolve(doc, value) is None:
                        broken.append((value, path))
                else:
                    broken += walk(value, f"{path}/{key}")
        elif isinstance(node, list):
            for index, item in enumerate(node):
                broken += walk(item, f"{path}[{index}]")
        return broken

    broken = walk(doc, "")
    assert broken == []


def _resolve(doc: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    node: Any = doc
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def test_asyncapi_document_is_valid() -> None:
    """Structural sanity a broken generator would fail immediately: exactly
    one operation/message per channel, and every channel/message actually
    referenced from somewhere."""
    doc = build_asyncapi()
    assert doc["asyncapi"] == "3.0.0"
    assert len(doc["channels"]) > 0
    referenced_channels = {
        op["channel"]["$ref"].rsplit("/", 1)[-1] for op in doc["operations"].values()
    }
    assert referenced_channels == set(doc["channels"])


def test_same_named_classes_are_not_merged_into_one_wrong_schema() -> None:
    """Regression test for a real bug this generator hit: FastStream merges
    each channel's independently-generated schema into one
    ``components.schemas`` dict keyed by bare class name, so two *different*
    classes sharing a name (``definitions.sensor.Thruster`` vs
    ``definitions.simulation.Thruster``) silently overwrote each other.
    """
    assert SensorThruster is not SimulationThruster
    assert SensorThruster.__name__ == SimulationThruster.__name__

    ref_for, schemas = _combined_schemas([SensorThruster, SimulationThruster])
    sensor_ref = ref_for[id(SensorThruster)]
    simulation_ref = ref_for[id(SimulationThruster)]

    assert sensor_ref != simulation_ref
    sensor_schema = schemas[sensor_ref.rsplit("/", 1)[-1]]
    simulation_schema = schemas[simulation_ref.rsplit("/", 1)[-1]]

    # The sensor Thruster only has an "active" flag; the simulation-input
    # Thruster additionally carries a heat flow. Getting these swapped is
    # exactly the bug this generator must not reintroduce.
    assert set(sensor_schema["properties"]) == {"Active"}
    assert set(simulation_schema["properties"]) == {"HeatFlow", "Active"}


def test_send_and_receive_on_the_same_address_get_independent_metadata() -> None:
    """Regression test for a real bug this generator hit: a send-group and a
    receive-group sharing one address template (e.g.
    ``thrs/controller/{module}/control-mode`` - ``ControlChannels`` sends
    the raw control-mode class, ``ControlApiChannels`` listens for it
    wrapped in ``SwitchingControlMode[...]``) were keyed only by template,
    so whichever direction finalized last overwrote the other's
    parameters/x-module-schema.
    """
    doc = build_asyncapi()
    handler = doc["channels"]["thrs.controller.{module}.control-mode:Handler"]
    publisher = doc["channels"]["thrs.controller.{module}.control-mode:Publisher"]

    handler_schema = handler["x-module-schema"]["thrusters"]
    publisher_schema = publisher["x-module-schema"]["thrusters"]

    assert handler_schema == ["SwitchingControlMode[ThrustersControlMode]"]
    assert publisher_schema == ["ThrustersControlMode"]
    assert handler_schema != publisher_schema


def test_every_registered_topic_is_covered_by_exactly_one_channel() -> None:
    """Every concrete (topic, direction) pair the real ``*Channels`` classes
    register must be described by exactly one generated channel - nothing
    silently dropped, nothing double-counted."""
    registrations = _collect_registrations()
    classify = _classifier(
        sorted(all_module_descriptions(), key=len, reverse=True), DEFAULT_CONFIG
    )

    doc = build_asyncapi()
    addresses = {c["address"] for c in doc["channels"].values()}

    for registration in registrations:
        for topic, _ in describe_mapping(registration.mapping):
            template, _, _ = classify(topic)
            suffix = ":Publisher" if registration.direction == "send" else ":Handler"
            assert f"{template}{suffix}" in addresses, (topic, registration.direction)


def test_field_level_parameter_enum_matches_the_real_field_names() -> None:
    """The {field} enum on a device-field channel must be exactly the set of
    hyphenized field names that actually round-trip through that address -
    not a superset (would imply a topic that doesn't exist) or a subset
    (would silently hide a real topic)."""
    entries = _flatten(_collect_registrations())
    groups = _group(entries)

    thrusters_sensor = groups[("simulation/500000-thrs/thrusters/{field}", "receive")]
    assert "thrusters-pump1" in thrusters_sensor.param_values
    assert "thrusters-mix-recovery" in thrusters_sensor.param_values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
