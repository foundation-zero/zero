from pathlib import Path

import pytest

from zero_data.asyncapi import (
    JSON_TYPES,
    SCHEMA_REF_PREFIX,
    build_asyncapi,
    channel,
    component_name,
    extract_schemas,
    key,
    served_fields,
)
from zero_data.io_list import read_io_list
from zero_data.io_list.enums import ENUMS
from zero_data.io_list.managed_topics import (
    ComponentType,
    ManagedTopic,
    ValveType,
    extract_managed_topics,
    extract_parts,
)
from zero_data.io_list.types import IOResult, IOTopic, IOValue


@pytest.fixture(scope="module")
def io_result() -> IOResult:
    return read_io_list([Path("io_lists/ZERO mocked IO-List.xlsx")], "marpower")


@pytest.fixture(scope="module")
def managed_topics(io_result: IOResult) -> list[ManagedTopic]:
    managed_topics, *_ = extract_managed_topics(io_result.topics)

    return managed_topics


@pytest.fixture(scope="module")
def document(io_result: IOResult) -> dict:
    return build_asyncapi(io_result)


def test_every_topic_has_one_channel_and_one_receive_operation(
    managed_topics: list[ManagedTopic], document: dict
):
    keys = {key(topic) for topic in managed_topics}

    assert set(document["channels"]) > keys
    assert set(document["operations"]) > keys
    for operation_key, operation in document["operations"].items():
        assert operation["action"] == "send"
        assert operation["channel"] == {"$ref": f"#/channels/{operation_key}"}


def test_every_field_is_a_stamped_value_of_its_data_type(
    managed_topics: list[ManagedTopic], document: dict
):
    schemas = document["components"]["schemas"]
    for topic in managed_topics:
        payload = document["channels"][key(topic)]["messages"]["message"]["payload"]

        assert set(payload["properties"]) == {
            field for field in served_fields(topic.topic)
        }
        for field in topic.topic.fields:
            ref = payload["properties"][field.name]["$ref"]
            stamped = schemas[ref.removeprefix(SCHEMA_REF_PREFIX)]
            assert set(stamped["properties"]) == {"Value", "TimeStamp"}
            value = stamped["properties"]["Value"]
            if "$ref" in value:
                value = schemas[value["$ref"].removeprefix(SCHEMA_REF_PREFIX)]
            assert value["type"] == JSON_TYPES[field.data_type]


@pytest.mark.parametrize(
    ("component", "field", "enum"),
    [
        (ComponentType.AMCS_MODE, "Mode", "AmcsControlMode"),
        (ComponentType.PUMP, "CC_ControlMode", "PumpControlMode"),
    ],
)
def test_enum_fields_have_named_values(component, field, enum):
    topic = ManagedTopic(
        "500000-thrs",
        "dhw",
        "dhw-thing",
        component,
        IOTopic("marpower/500000-thrs/dhw/dhw-thing", [IOValue(field, "INTEGER")]),
    )

    schemas = extract_schemas([topic])

    payload = schemas[component_name(component)]
    assert payload["properties"][field] == {"$ref": f"{SCHEMA_REF_PREFIX}stamped{enum}"}
    assert schemas[f"stamped{enum}"]["properties"]["Value"] == {
        "$ref": f"{SCHEMA_REF_PREFIX}{enum}"
    }
    assert schemas[enum]["type"] == "integer"
    assert schemas[enum]["oneOf"] == [
        {"const": member.value, "title": member.name} for member in ENUMS[field]
    ]


@pytest.mark.parametrize(
    ("technical_name", "valve_type"),
    [
        ("dhw-mix-boosting", ValveType.MIX),
        ("dhw-switch-aft", ValveType.SWITCH),
        ("dhw-flowcontrol-aft", ValveType.FLOW_CONTROL),
    ],
)
def test_valves_carry_their_valve_type(technical_name, valve_type):
    address = f"marpower/500000-thrs/dhw/{technical_name}"
    topic = extract_parts(IOTopic(address, [IOValue("PositionRel", "REAL")]))

    assert isinstance(topic, ManagedTopic)
    assert channel(topic)["x-zero-valve-type"] == valve_type


def test_other_components_have_no_valve_type():
    address = "marpower/500000-thrs/dhw/dhw-flow-dc"
    topic = extract_parts(IOTopic(address, [IOValue("Flow", "REAL")]))

    assert isinstance(topic, ManagedTopic)
    assert "x-zero-valve-type" not in channel(topic)


def test_flow_meters_that_measure_only_a_flow_have_their_own_schema():
    meter = "marpower/500000-thrs/dhw/dhw-flow-dc"
    flow_meter = extract_parts(
        IOTopic(meter, [IOValue(name, "REAL") for name in ("Flow", "Temperature")])
    )
    flow_only_meter = extract_parts(IOTopic(meter, [IOValue("Flow", "REAL")]))
    assert isinstance(flow_meter, ManagedTopic)
    assert isinstance(flow_only_meter, ManagedTopic)

    schemas = extract_schemas([flow_meter, flow_only_meter])

    assert flow_meter.component == ComponentType.FLOW
    assert flow_only_meter.component == ComponentType.FLOW_ONLY
    assert set(schemas["Flow"]["properties"]) == {"Flow", "Temperature"}
    assert set(schemas["FlowOnly"]["properties"]) == {"Flow"}


@pytest.mark.parametrize(
    ("channel_key", "address", "component", "fields"),
    [
        (
            "propulsion.drive.pcs-aft-ara1",
            "marpower/150000-propulsion/pcs-aft-ara1",
            "Drive",
            {"VpEnable", "TempPowerStage", "Power"},
        ),
        (
            "dc_ac.converter.05-12-u101",
            "marpower/45-dc-ac/inverter/05-12-u101",
            "Converter",
            {"Running", "TempPowerStage", "PvPower"},
        ),
        (
            "dc_700v.shore-converter.07-11-tbc1a",
            "marpower/45-dc-700v/shore-converter/07-11-tbc1a",
            "ShoreConverter",
            {
                "Online",
                "EsiTransformerTemperature",
                "EsiIgbtMinTemperature",
                "EsiIgbtMaxTemperature",
                "EsiAcBusActivePower3Phase",
            },
        ),
    ],
)
def test_extra_devices_are_named_by_the_proposal_at_their_address(
    document: dict, channel_key: str, address: str, component: str, fields: set[str]
):
    device = document["channels"][channel_key]

    assert device["address"] == address
    assert device["messages"]["message"]["payload"] == {
        "$ref": f"{SCHEMA_REF_PREFIX}{component}"
    }
    schema = document["components"]["schemas"][component]
    assert set(schema["properties"]) == fields
    assert document["operations"][channel_key]["action"] == "send"


def test_document_does_not_depend_on_io_list_order(io_result: IOResult):
    reversed_result = IOResult(io_result.io_list, list(reversed(io_result.topics)))

    assert build_asyncapi(reversed_result) == build_asyncapi(io_result)


def test_fields_whose_graphql_names_collide_are_both_left_out(caplog):
    topic = IOTopic(
        "marpower/280000-hydraulic-sail/hydraulics",
        [
            IOValue("Tank_Level_Sensor", "BOOLEAN"),
            IOValue("Tank_level_sensor", "INTEGER"),
            IOValue("Pressure", "REAL"),
            IOValue("Temperature", "REAL", yard_tag="50001038-41"),
            IOValue("Temperature", "REAL", yard_tag="50001038-42"),
        ],
    )

    assert [field for field in served_fields(topic)] == ["Pressure", "Temperature"]
    assert "Tank_Level_Sensor, Tank_level_sensor" in caplog.text
