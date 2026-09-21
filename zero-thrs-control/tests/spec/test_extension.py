"""Tests for the ``x-mqtt-graphql`` extension (``thrs print-asyncapi``).

The extension is the GraphQL side of the contract; these check that it binds
only to what the document declares, that it names things the way the API
does (against the API's own schema, for as long as the API exists), and that
it says nothing the schemas already say.
"""

import re
from typing import Any

import pytest

from thrs.input_output.definitions import control, sensor, simulation
from thrs.spec import contract, naming
from thrs.spec.asyncapi import (
    DEFAULT_CONFIG,
    all_module_descriptions,
    build_asyncapi,
    operation_topic,
    spec_config,
)
from thrs.spec.extension import (
    EXTENSION_KEY,
    EXTENSION_VERSION,
    build_thrs_spec,
    shared_definitions,
)


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    return build_thrs_spec()


@pytest.fixture(scope="module")
def extension(spec: dict[str, Any]) -> dict[str, Any]:
    return spec[EXTENSION_KEY]


def _resolve(doc: dict[str, Any], ref: str) -> Any:
    node: Any = doc
    for part in ref.removeprefix("#/").split("/"):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _walk(node: Any, key: str) -> list[Any]:
    """Every value under ``key`` anywhere in ``node``."""
    if isinstance(node, dict):
        found = [node[key]] if key in node else []
        return found + [v for value in node.values() for v in _walk(value, key)]
    if isinstance(node, list):
        return [v for item in node for v in _walk(item, key)]
    return []


def test_thrs_spec_is_the_document_plus_the_extension(spec, extension) -> None:
    """``build_thrs_spec`` adds one root key to the document. The document is
    the channel document plus the shared component definitions' schemas."""
    without = {k: v for k, v in spec.items() if k != EXTENSION_KEY}
    document = build_asyncapi()
    assert set(without) == set(document)
    assert without["channels"] == document["channels"]
    assert without["operations"] == document["operations"]
    assert set(without["components"]["schemas"]) >= set(
        document["components"]["schemas"]
    )
    assert set(extension) == {"version", "types", "views", "metadata", "lifecycles"}
    assert extension["version"] == EXTENSION_VERSION
    assert [m["gql"] for m in extension["views"][0]["members"]] == sorted(
        all_module_descriptions()
    )
    assert all(m["mutations"] for m in extension["views"][0]["members"])


def test_every_declared_type_is_served_from_a_schema_of_the_document(
    spec, extension
) -> None:
    """``types`` pairs each GraphQL object type with one schema the document
    holds, and every type a field or section names is declared."""
    types = extension["types"]
    assert types, "types are declared"
    for name, entry in types.items():
        assert set(entry) == {"schema"}, name
        assert _resolve(spec, entry["schema"]["$ref"]) is not None, name
    schemas = [entry["schema"]["$ref"] for entry in types.values()]
    assert len(schemas) == len(set(schemas)), "one type per schema"

    containers = {
        contract.MODULES_TYPE_NAME,
        contract.SIMULATION_STATE_TYPE_NAME,
        *(m["typeName"] for m in extension["views"][0]["members"]),
        *(
            s["typeName"]
            for m in extension["views"][0]["members"]
            for s in m["sections"]
            if s["kind"] in ("stampedFields", "switch")
        ),
    }
    for name in _walk(extension["views"], "typeName") + _walk(
        extension["lifecycles"], "typeName"
    ):
        assert name in types or name in containers, name
    for name in _walk(extension, "objectTypeName"):
        assert name in types, name


def test_extension_repeats_nothing_the_schemas_say(extension) -> None:
    """No leaf, scalar type, enum, bound or default is spelled out in the
    extension: a section names its type and, per field, at most the operation
    that feeds it and what the schema cannot know."""
    forbidden = {
        "leaves",
        "type",
        "enumValues",
        "enumType",
        "bounds",
        "inputFields",
        "optional",
        "default",
    }
    for key in forbidden:
        assert _walk(extension, key) == [], key
    for member in extension["views"][0]["members"]:
        for section in member["sections"]:
            for field in section.get("fields", []):
                assert set(field) <= {
                    "gql",
                    "key",
                    "operation",
                    "typeName",
                    "computed",
                    "wireKeys",
                }, field


def _operation_refs(node: Any, parent: str = "") -> list[tuple[str, dict[str, Any]]]:
    """Every operation reference in the extension with the key it sits under
    (``operation``/``state`` for reads, ``target`` for writes)."""
    refs: list[tuple[str, dict[str, Any]]] = []
    if isinstance(node, dict):
        if "operation" in node and isinstance(node["operation"], str):
            # A metadata entry names its operation without parameters: it
            # enumerates them (checked separately below).
            return [] if "instances" in node else [(parent, node)]
        for key, value in node.items():
            refs += _operation_refs(value, key)
    elif isinstance(node, list):
        for item in node:
            refs += _operation_refs(item, parent)
    return refs


def test_extension_binds_only_to_operations_the_document_declares(
    spec, extension
) -> None:
    """The extension never names a topic: every read binds to a ``send``
    operation and every write to a ``receive`` operation of the same document,
    with exactly the parameters that operation's channel address has, and every
    metadata group is a channel address of the document."""
    operations = spec["operations"]
    channels = spec["channels"]
    refs = _operation_refs(extension)
    assert refs, "the extension binds to operations"
    for under, ref in refs:
        operation = operations[ref["operation"]]
        expected = "receive" if under == "target" else "send"
        assert operation["action"] == expected, (under, ref)
        channel = channels[operation["channel"]["$ref"].rsplit("/", 1)[-1]]
        address = channel["address"]
        parameters = ref.get("parameters") or {}
        assert set(parameters) == set(re.findall(r"\{(\w+)\}", address)), ref
        for name, value in parameters.items():
            assert value in channel["parameters"][name]["enum"], (ref, name)
        # The bound topic is the address with its parameters filled in.
        assert operation_topic(ref, spec) == re.sub(
            r"\{(\w+)\}", lambda m, p=parameters: p[m.group(1)], address
        )

    # Metadata enumerates the instances of a send operation's one parameter,
    # each a value the channel declares.
    for entry in extension["metadata"]:
        operation = operations[entry["operation"]]
        assert operation["action"] == "send"
        channel = channels[operation["channel"]["$ref"].rsplit("/", 1)[-1]]
        (param,) = channel["parameters"]
        assert set(entry["instances"]) <= set(channel["parameters"][param]["enum"])


def test_a_field_names_its_type_only_where_the_schema_cannot(spec, extension) -> None:
    """A ``typeName`` on a field appears exactly when the bridge could not
    find the type from the schema it reads the field through: the topic
    carries several payload types, or the component is served as its base's
    type (``PropulsionDrive`` as ``SimulationHeatSourceType``)."""
    types = {
        entry["schema"]["$ref"]: name for name, entry in extension["types"].items()
    }
    thrusters = next(
        m for m in extension["views"][0]["members"] if m["gql"] == "thrusters"
    )
    sensor_values = next(s for s in thrusters["sections"] if s["gql"] == "sensorValues")
    for field in sensor_values["fields"]:
        topic = operation_topic(field["operation"], spec)
        operation = spec["operations"][field["operation"]["operation"]]
        channel = spec["channels"][operation["channel"]["$ref"].rsplit("/", 1)[-1]]
        message = next(iter(channel["messages"].values()))
        pinned = message["payload"]
        for param, value in field["operation"].get("parameters", {}).items():
            pinned = message[f"x-{param}-schema"][value]
        if "$ref" in pinned and pinned["$ref"] in types:
            assert "typeName" not in field, (topic, "the schema says it")
        else:
            assert "typeName" in field, (topic, "the schema cannot say it")

    drives = next(
        m for m in extension["lifecycles"][0]["members"] if m["name"] == "drives"
    )
    inputs = next(s for s in drives["sections"] if s["gql"] == "inputs")
    overrides = {f["key"]: f["typeName"] for f in inputs.get("fields", [])}
    assert overrides["DrivesPropdriveAft1"] == naming.type_name(
        simulation.PropulsionDrive
    )
    assert naming.type_name(simulation.PropulsionDrive) == "SimulationHeatSourceType"


def test_every_mutation_is_confirmed_the_way_the_contract_says(extension) -> None:
    """Every mutation (module and simulation) waits for the controller's echo
    with the contract's timeout and error; the automation switch is confirmed
    on the control-mode object by the presence of the automatic mode."""
    for member in extension["views"][0]["members"]:
        for m in member["mutations"]:
            confirm = m["confirm"]
            assert confirm["timeoutS"] == contract.WAIT_TIMEOUT, m["gql"]
            if m["kind"] == "setFlag":
                assert confirm["presence"] is True
                assert confirm["key"] == "AutomaticMode"
                assert confirm["operation"]["operation"].endswith("control-mode.send")
                assert confirm["timeoutError"] == contract.AUTOMATION_MODE_TIMEOUT_ERROR
            else:
                assert set(confirm) == {"timeoutS", "timeoutError"}, m["gql"]
                assert (
                    confirm["timeoutError"]
                    == {
                        "setField": contract.PARAMETERS_TIMEOUT_ERROR,
                        "setComponent": contract.CONTROL_VALUES_TIMEOUT_ERROR,
                    }[m["kind"]]
                )
    for member in extension["lifecycles"][0]["members"]:
        for m in member["mutations"]:
            assert m["confirm"] == {
                "timeoutS": contract.WAIT_TIMEOUT,
                "timeoutError": contract.SIMULATION_INPUTS_TIMEOUT_ERROR,
            }
    directives = {d["gql"]: d for d in extension["lifecycles"][0]["directives"]}
    assert (
        directives["simulationPause"]["preconditionError"]
        == contract.PAUSE.precondition_error
    )
    assert "key" not in directives["simulationPause"]
    assert directives["simulationPlay"]["key"] == "PlaybackRate"


def test_prefixes_reach_every_part_of_the_extension() -> None:
    """The three prefix flags of ``print-asyncapi`` land in every binding of
    the extension, so one invocation targets one broker prefix consistently."""
    spec = build_thrs_spec(
        spec_config(
            devices_prefix="dev", controller_prefix="ctl", simulator_prefix="sim"
        )
    )
    extension = spec[EXTENSION_KEY]
    topics = [operation_topic(ref, spec) for _, ref in _operation_refs(extension)]
    assert topics
    for topic in topics:
        assert topic.startswith(("dev/", "ctl/", "sim/")), topic
    thrusters = next(
        m for m in extension["views"][0]["members"] if m["gql"] == "thrusters"
    )
    sensor_values = next(s for s in thrusters["sections"] if s["gql"] == "sensorValues")
    assert any(
        operation_topic(f["operation"], spec).startswith("dev/")
        for f in sensor_values["fields"]
    )
    parameters = next(s for s in thrusters["sections"] if s["gql"] == "parameters")
    assert operation_topic(parameters["operation"], spec).startswith("ctl/")
    defaults = (
        DEFAULT_CONFIG.mqtt_devices_topic_prefix + "/",
        DEFAULT_CONFIG.mqtt_controller_topic_prefix + "/",
        DEFAULT_CONFIG.mqtt_simulator_topic_prefix + "/",
    )
    assert not any(topic.startswith(defaults) for topic in topics)


# --- Naming parity with the API, for as long as the API exists -------------------


@pytest.fixture(scope="module")
def api_schema():
    strawberry = pytest.importorskip("thrs.graphql.strawberry")
    return strawberry.schema._schema


def test_field_name_is_the_api_name_converter() -> None:
    converters = pytest.importorskip("strawberry.utils.str_converters")
    names = {
        name
        for description in all_module_descriptions().values()
        for cls in (
            description.sensor_values_cls,
            description.control_values_cls,
            description.parameters_cls,
            description.controller_state_cls,
            description.control_mode_cls,
        )
        for name in [*cls.model_fields, *cls.model_computed_fields]
    }
    names |= {"pvt_flow_main_string1_2", "sensor_values", "set_automation_mode"}
    for name in names:
        assert naming.field_name(name) == converters.to_camel_case(name), name


def test_type_names_are_the_api_type_names(api_schema) -> None:
    """Every type the extension declares, and every shared definition's type,
    is a type of the API's schema under exactly that name."""
    api_types = set(api_schema.type_map)
    extension = build_thrs_spec()[EXTENSION_KEY]
    for name in extension["types"]:
        assert name in api_types, name
    for name in _walk(extension, "typeName") + _walk(extension, "objectTypeName"):
        assert name in api_types, name
    # A shared definition's type is in the schema once something serves it.
    served = {naming.type_name(cls) for cls in shared_definitions()}
    assert served & api_types >= {"ControlPumpType", "SensorFlowSensorType"}
    # An unexported subclass is served as its base's type, an exported one as
    # its own.
    assert naming.type_name(simulation.PropulsionDrive) == naming.type_name(
        simulation.HeatSource
    )
    assert naming.type_name(simulation.Thruster) == "SimulationThrusterType"
    assert naming.type_name(sensor.Thruster) == "SensorThrusterType"
    assert naming.type_name(control.Pump) == "ControlPumpType"
    assert naming.input_type_name(control.Pump) == "PumpInputType"
    assert "PumpInputType" in api_types
    assert contract.SIMULATION_INPUTS_UNION in api_types


def test_mutations_are_exactly_the_api_mutations(api_schema) -> None:
    """The extension's mutations (module, simulation and directives) are
    exactly the API's, with the same argument name and input type."""
    api_mutations = api_schema.mutation_type.fields
    extension = build_thrs_spec()[EXTENSION_KEY]
    declared: dict[str, dict[str, Any]] = {}
    for member in (
        extension["views"][0]["members"] + extension["lifecycles"][0]["members"]
    ):
        for m in member["mutations"]:
            declared[m["gql"]] = m
    for d in extension["lifecycles"][0]["directives"]:
        declared[d["gql"]] = d
    assert set(declared) == set(api_mutations)
    for name, m in declared.items():
        args = api_mutations[name].args
        if "argName" in m:
            assert set(args) == {m["argName"]}, name
            arg_type = str(args[m["argName"]].type).rstrip("!")
            if m["kind"] == "setComponent":
                assert arg_type == m["inputTypeName"], name
        elif "key" in m:
            directive = next(
                d
                for d in contract.SIMULATION_DIRECTIVES
                if d.message.model_fields
                and next(iter(d.message.model_fields.values())).alias == m["key"]
            )
            (python_name,) = directive.message.model_fields
            assert set(args) == {naming.field_name(python_name)}, name
        else:
            assert args == {}, name
