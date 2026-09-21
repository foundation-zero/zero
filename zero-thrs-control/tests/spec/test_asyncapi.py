"""Tests for the generated AsyncAPI document (``thrs print-asyncapi``).

These guard what matters for a generated document: it must not drift from
the real MQTT wiring in ``orchestration.comms``, it must not misrepresent a
payload, and its schemas must say what the GraphQL contract reads off them
(enum member names, cross-field invariants, derived components).
"""

import re
from typing import Any

import pytest
from pydantic import ValidationError

from thrs.input_output.definitions.sensor import Thruster as SensorThruster
from thrs.input_output.definitions.simulation import Thruster as SimulationThruster
from thrs.input_output.definitions.units import PcsMode
from thrs.runtime.descriptions.simulation import MODES, simulation_io_classes
from thrs.spec.asyncapi import (
    DEFAULT_CONFIG,
    DERIVED_KEY,
    ENUM_NAMES_KEY,
    INVARIANTS_KEY,
    _classifier,
    _collect_registrations,
    _combined_schemas,
    _flatten,
    _group,
    all_module_descriptions,
    build_asyncapi,
    build_document,
    describe_mapping,
    spec_config,
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


def _resolve(doc: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    node: Any = doc
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _broken_refs(doc: dict[str, Any]) -> list[str]:
    def walk(node: Any) -> list[str]:
        if isinstance(node, dict):
            return [
                value
                for key, value in node.items()
                if key == "$ref"
                and isinstance(value, str)
                and _resolve(doc, value) is None
            ] + [broken for value in node.values() for broken in walk(value)]
        if isinstance(node, list):
            return [broken for item in node for broken in walk(item)]
        return []

    return walk(doc)


def test_build_asyncapi_has_no_broken_refs() -> None:
    assert _broken_refs(build_asyncapi()) == []


def _all_strings(node: Any) -> list[str]:
    if isinstance(node, dict):
        out: list[str] = []
        for key, value in node.items():
            out.append(key)
            out += _all_strings(value)
        return out
    if isinstance(node, list):
        return [s for item in node for s in _all_strings(item)]
    return [node] if isinstance(node, str) else []


def test_build_asyncapi_default_prefix_is_a_noop() -> None:
    """Passing the default prefixes explicitly changes nothing."""
    config = spec_config(
        devices_prefix=DEFAULT_CONFIG.mqtt_devices_topic_prefix,
        controller_prefix=DEFAULT_CONFIG.mqtt_controller_topic_prefix,
    )
    assert build_asyncapi(config) == build_asyncapi()


def test_build_asyncapi_reprefix_swaps_every_topic_form_without_breaking_refs() -> None:
    """Every channel address, key, MQTT binding and $ref moves to the chosen
    prefix (both `/` and `.` forms), nothing keeps the old prefix, unrelated
    (simulator) channels are untouched, and no ref breaks."""
    doc = build_asyncapi(spec_config(devices_prefix="xsim", controller_prefix="xctrl"))
    strings = _all_strings(doc)
    assert not any(
        s.startswith(
            ("simulation/", "simulation.", "thrs/controller/", "thrs.controller.")
        )
        for s in strings
    ), "an old prefix survived the reprefix"
    assert any(s.startswith("xsim/") for s in strings)
    assert any(s.startswith("xctrl/") for s in strings)
    # Unrelated simulator channels keep their own prefix.
    assert any(s.startswith(("thrs/simulator/", "thrs.simulator.")) for s in strings)
    assert _broken_refs(doc) == []


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
    for key, op in doc["operations"].items():
        channel_key = op["channel"]["$ref"].rsplit("/", 1)[-1]
        assert key == f"{channel_key}.{op['action']}"
        for ref in op["messages"]:
            assert _resolve(doc, ref["$ref"]) is not None, ref
    # One channel per address, keys without parameters or role suffixes.
    addresses = [c["address"] for c in doc["channels"].values()]
    assert len(addresses) == len(set(addresses))
    assert all("{" not in key and ":" not in key for key in doc["channels"])


def test_same_named_classes_are_not_merged_into_one_wrong_schema() -> None:
    """Two *different* classes sharing a name (``definitions.sensor.Thruster``
    vs ``definitions.simulation.Thruster``) get two schemas; merging them by
    bare class name is a bug this generator once had."""
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


def test_one_channel_per_address_with_one_message_per_distinct_payload() -> None:
    """A send-group and a receive-group sharing one address template (e.g.
    thrs/controller/{module}/control-mode - ControlChannels sends
    the raw control-mode class, ControlApiChannels listens for it
    wrapped in ``SwitchingControlMode[...]``, which ``_wire_type`` maps to the
    same wrapper on the wire) are one channel. Its directions share one
    message when they carry the same payload, else each has its own
    (sent/received); every operation references the message of its
    direction, and a parametrized message pins each parameter value to its
    schema."""
    doc = build_asyncapi()
    channel = doc["channels"]["thrs.controller.control-mode"]
    assert set(channel["messages"]) == {"message"}
    message = channel["messages"]["message"]
    assert set(channel["parameters"]["module"]["enum"]) == set(
        message["x-module-schema"]
    )
    # The message describes the switching wrapper actually on the wire
    # (`_wire_type`), not the bare mode class the sender is declared with.
    ref = message["x-module-schema"]["thrusters"]["$ref"].rsplit("/", 1)[-1]
    assert set(doc["components"]["schemas"][ref]["properties"]) == {"AutomaticMode"}

    for key, channel in doc["channels"].items():
        assert set(channel["messages"]) in ({"message"}, {"sent", "received"}), key
        # Every THRS value is served until the next message replaces it.
        assert channel["x-ttl"] == "unbounded", key
        for direction in ("send", "receive"):
            operation = doc["operations"].get(f"{key}.{direction}")
            if operation is None:
                continue
            own = {"send": "sent", "receive": "received"}[direction]
            expected = own if own in channel["messages"] else "message"
            assert operation["messages"] == [
                {"$ref": f"#/channels/{key}/messages/{expected}"}
            ], key
        for param in channel.get("parameters", {}):
            for message in channel["messages"].values():
                assert set(message[f"x-{param}-schema"]) <= set(
                    channel["parameters"][param]["enum"]
                ), key


def test_every_registered_topic_is_covered_by_exactly_one_channel() -> None:
    """Every concrete (topic, direction) pair the real ``*Channels`` classes
    register must be described by exactly one generated channel - nothing
    silently dropped, nothing double-counted."""
    registrations = _collect_registrations(DEFAULT_CONFIG)
    classify = _classifier(DEFAULT_CONFIG)

    doc = build_asyncapi()
    operations = {
        (
            doc["channels"][op["channel"]["$ref"].rsplit("/", 1)[-1]]["address"],
            op["action"],
        )
        for op in doc["operations"].values()
    }
    assert len(operations) == len(doc["operations"])

    for registration in registrations:
        for topic, _ in describe_mapping(registration.mapping):
            template, _, _ = classify(topic)
            assert (template, registration.direction) in operations, (
                topic,
                registration.direction,
            )


def test_field_level_parameter_enum_matches_the_real_field_names() -> None:
    """The {field} enum on a device-field channel must be exactly the set of
    hyphenized field names that actually round-trip through that address -
    not a superset (would imply a topic that doesn't exist) or a subset
    (would silently hide a real topic)."""
    entries = _flatten(
        _collect_registrations(DEFAULT_CONFIG), _classifier(DEFAULT_CONFIG)
    )
    groups = _group(entries)

    thrusters_sensor = groups[("simulation/500000-thrs/thrusters/{field}", "receive")]
    assert "thrusters-pump1" in thrusters_sensor.param_values
    assert "thrusters-mix-recovery" in thrusters_sensor.param_values


def test_document_knows_where_each_class_and_property_lives() -> None:
    """``Document`` resolves a payload class to its schema and a property to
    the object it holds, following the document's own references."""
    document = build_document()
    thrusters = all_module_descriptions()["thrusters"]
    parameters_ref = document.schema_ref(thrusters.parameters_cls)
    assert _resolve(document.data, parameters_ref) is not None
    control_values_ref = document.schema_ref(thrusters.control_values_cls)
    pump_key = thrusters.control_values_cls.model_fields["thrusters_pump1"].alias
    pump_ref = document.property_ref(control_values_ref, pump_key)
    assert set(_resolve(document.data, pump_ref)["properties"]) >= {"Dutypoint", "On"}
    with pytest.raises(KeyError):
        document.property_ref(parameters_ref, "CoolingFlow")
    with pytest.raises(KeyError):
        document.schema_ref(dict)


# --- What the schemas say about themselves ---------------------------------------


def test_enum_schemas_name_their_members() -> None:
    """Every enum schema pairs its wire values with the Python members' names
    (``x-enum-varnames``), in order; the API serves the names."""
    schemas = build_asyncapi()["components"]["schemas"]
    pcs_mode = schemas["PcsMode"]
    assert pcs_mode["enum"] == [member.value for member in PcsMode]
    assert pcs_mode[ENUM_NAMES_KEY] == [member.name for member in PcsMode]
    enums = [s for s in schemas.values() if "enum" in s and ENUM_NAMES_KEY in s]
    assert len(enums) >= 5
    for schema in enums:
        assert len(schema["enum"]) == len(schema[ENUM_NAMES_KEY])


def test_parameter_schemas_carry_the_models_invariants() -> None:
    """A parameters schema states every cross-field invariant of its model
    (``x-invariants``, by wire key): a value that breaks one is exactly what
    the model itself rejects on assignment, with the same error."""
    document = build_document()
    schemas = document.data["components"]["schemas"]
    modules_with_invariants = set()
    for module, description in all_module_descriptions().items():
        params_cls = description.parameters_cls
        schema = schemas[document.schema_ref(params_cls).rsplit("/", 1)[-1]]
        invariants = schema.get(INVARIANTS_KEY, [])
        assert len(invariants) == len(params_cls.invariants), module
        by_alias = {f.alias: name for name, f in params_cls.model_fields.items()}
        for inv in invariants:
            modules_with_invariants.add(module)
            lhs, rhs = by_alias[inv["lhs"]], by_alias[inv["rhs"]]
            base = params_cls()
            # Break the invariant by moving lhs past rhs.
            right = getattr(base, rhs)
            value = {
                "lt": right,
                "le": right + 1,
                "gt": right,
                "ge": right - 1,
            }[inv["op"]]
            with pytest.raises(ValidationError, match=re.escape(inv["error"])):
                setattr(base.model_copy(), lhs, value)
    assert modules_with_invariants >= {"thrusters", "dhw", "pvt", "adsorption"}


def test_simulation_inputs_schema_states_its_derived_components() -> None:
    """A simulation inputs ``computed_field`` that merely mirrors another
    component's stamped leaves (dhw's recovery sensors) is stated on the
    schema (``x-derived``) with, per leaf, the component and leaf it copies;
    the mapping is found by object identity on a zero instance, so it can't
    drift from the model. Simulations without such fields state none."""
    document = build_document()
    schemas = document.data["components"]["schemas"]
    for mode, (inputs_cls, _) in simulation_io_classes().items():
        schema = schemas[document.schema_ref(inputs_cls).rsplit("/", 1)[-1]]
        derived = {d["key"]: d["leaves"] for d in schema.get(DERIVED_KEY, [])}
        if mode != "dhw":
            assert derived == {}, mode
            continue
        assert derived["DrivesFlowRecovery"] == {
            "Flow": {"component": "DhwDrivesSupply", "leaf": "Flow"},
            "Temperature": {"component": "DhwDrivesSupply", "leaf": "Temperature"},
            # FlowSensor.quantity keeps its constant default; the API serializes it.
            "Quantity": {
                "constant": {"Value": 0.0, "TimeStamp": "1970-01-01T00:00:00Z"}
            },
        }
        assert derived["DrivesTemperatureRecovery"] == {
            "Temperature": {"component": "DhwDrivesSupply", "leaf": "Temperature"},
        }
        # One entry per mirroring computed field, keyed by its wire alias.
        assert set(derived) == {
            inputs_cls.model_computed_fields[name].alias or name
            for name in inputs_cls.model_computed_fields
        }
