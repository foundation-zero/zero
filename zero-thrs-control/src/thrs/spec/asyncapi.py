"""The AsyncAPI 3.0 document of the THRS control system.

The channels come from the real channel wiring (``thrs.orchestration.comms``):
a recording connector builds the same ``*Channels`` the runtime builds, so the
document cannot drift from the topics actually used. One channel per MQTT
address template, one operation per direction, one message per distinct
payload; a parametrized address (``{field}``, ``{module}``) carries an
``x-{param}-schema`` pinning each parameter value to its own payload schema.

``components.schemas`` are the pydantic models' JSON Schemas, plus what the
GraphQL contract needs the schemas to say about themselves:
``x-enum-varnames`` (the members of an enum, as OpenAPI tooling names them),
``x-invariants`` (a model's cross-field rules, ``ThrsValues.invariants``) and
``x-derived`` (the components a model mirrors from others on serialization).
"""

from __future__ import annotations

import re
import warnings
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from functools import reduce
from operator import or_
from types import NoneType, UnionType
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue

from thrs.input_output.base import Stamped, ThrsValues
from thrs.orchestration.comms import (
    DEVICE_NAMESPACE,
    SIMULATION_INPUTS_TOPIC,
    SIMULATION_OUTPUTS_TOPIC,
    ControlApiChannels,
    ControlChannels,
    DirectivesApiChannels,
    DirectivesChannels,
    DirectMqttMapping,
    MergedModuleMqttMapping,
    ModuleMqttMapping,
    MqttConnector,
    PartialMqttMapping,
    SimulationApiChannels,
    SimulationChannels,
    device_module_prefix,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription
from thrs.runtime.descriptions.simulation import lookup_mode, simulation_io_classes
from thrs.spec import validators

# Only shapes the example topics printed in the spec -
# the runtime always reads these from Config/env, never from here.
# model_validate skips the settings sources (.env, os.environ): pure defaults.
DEFAULT_CONFIG = Config.model_validate({})

# Topics with a fixed "kind" segment per module, e.g. thrs/controller/{module}/parameters.
# Field names are always hyphenized so they never collide with these.
TYPE_TOPIC_KINDS = (
    "parameters",
    "control-mode",
    "controller-state",
    "manual-values",
    "automation-mode",
)

# The bridge serves the last message of every THRS channel until the next one
# replaces it (`x-ttl`), as thrs-api does; a value never expires into null.
CHANNEL_TTL = "unbounded"

SCHEMA_REF_PREFIX = "#/components/schemas/"

Direction = Literal["send", "receive"]


def spec_config(
    devices_prefix: str | None = None,
    controller_prefix: str | None = None,
    simulator_prefix: str | None = None,
) -> Config:
    """``DEFAULT_CONFIG`` with the chosen MQTT topic prefixes baked in, so a
    document can target a differently-prefixed broker; an omitted prefix keeps
    the default one."""
    overrides = {
        "mqtt_devices_topic_prefix": devices_prefix,
        "mqtt_controller_topic_prefix": controller_prefix,
        "mqtt_simulator_topic_prefix": simulator_prefix,
    }
    return DEFAULT_CONFIG.model_copy(
        update={key: value for key, value in overrides.items() if value}
    )


def all_module_descriptions() -> dict[str, ModuleDescription]:
    """Every distinct module, keyed by name. Mode "thrs" covers the union of all modes."""
    return dict(lookup_mode("thrs").control_modules)


# --- Recording connector: builds the real mapping graph, records nothing else ---


@dataclass
class _Registration:
    mapping: object
    direction: Direction
    retain: bool = False


class RecordingConnector(MqttConnector):
    """Fake MqttConnector that records what the *Channels constructors register.

    Lets us derive the spec from the real mapping graph instead of re-implementing topic names.
    """

    def __init__(self) -> None:
        self.registrations: list[_Registration] = []
        self._listeners = []
        self._started = False

    def _register_listener(self, receiver) -> None:
        self._listeners.append(receiver)
        self.registrations.append(_Registration(receiver, "receive"))

    def _create_publisher(self, sender, qos: int = 1, retain: bool = False):
        self.registrations.append(_Registration(sender, "send", retain))

        async def _publish(
            value,
        ):  # pragma: no cover - never invoked for spec generation
            return None

        return _publish


def _collect_registrations(config: Config) -> list[_Registration]:
    modules = all_module_descriptions()
    thrs_mode = lookup_mode("thrs")
    simulation_description = thrs_mode.simulation_description
    if simulation_description is None:
        raise RuntimeError(
            'Mode "thrs" has no simulation description; cannot build the spec.'
        )

    connector = RecordingConnector()

    for module_name, description in modules.items():
        ControlChannels(connector, config, module_name, description)
        ControlApiChannels(connector, config, module_name, description)

    sensor_values_clss = {name: d.sensor_values_cls for name, d in modules.items()}
    control_values_clss = {name: d.control_values_cls for name, d in modules.items()}
    simulation_inputs_cls = type(simulation_description.simulation_inputs)
    simulation_outputs_cls = simulation_description.simulation_outputs_cls

    SimulationChannels(
        connector,
        config,
        sensor_values_clss,
        control_values_clss,
        simulation_inputs_cls,
        simulation_outputs_cls,
    )
    # The API subscribes to the simulation inputs/outputs topics with the
    # union of *every* simulation's model, not just mode "thrs"'s: whichever
    # simulation runs publishes its own class. Describe the API side that way
    # so the channel payload (and so payload validation) accepts each of them.
    io_classes = simulation_io_classes()
    SimulationApiChannels(
        connector,
        config,
        tuple(dict.fromkeys(inputs for inputs, _ in io_classes.values())),
        tuple(dict.fromkeys(outputs for _, outputs in io_classes.values())),
    )
    # The simulator side (`SimulationChannels` above) publishes the running
    # mode's own inputs/outputs classes; the spec is built from mode "thrs"
    # only, but every simulation can run. Declare each simulation's classes as
    # publishers of those topics too, so the channel payload is the anyOf of
    # all of them (what the wire can carry) rather than mode "thrs"'s alone.
    for inputs_cls, outputs_cls in io_classes.values():
        for cls, kind in (
            (inputs_cls, SIMULATION_INPUTS_TOPIC),
            (outputs_cls, SIMULATION_OUTPUTS_TOPIC),
        ):
            connector.registrations.append(
                _Registration(
                    DirectMqttMapping(
                        cls, f"{config.mqtt_simulator_topic_prefix}/{kind}"
                    ),
                    "send",
                )
            )
    DirectivesChannels(connector, config)
    DirectivesApiChannels(connector, config)

    return connector.registrations


# --- Reading (topic, payload type) pairs back off the real mappings ---


def _is_union(annotation: Any) -> bool:
    """Both spellings of a union: `X | None` (`types.UnionType`) and
    `typing.Union`/`Optional` (what `Annotated[...] | None` produces)."""
    return get_origin(annotation) in (UnionType, Union)


def _strip_none(annotation: Any) -> Any:
    if _is_union(annotation):
        args = [a for a in get_args(annotation) if a is not NoneType]
        return _union(args) if len(args) > 1 else args[0]
    return annotation


def _union(types: list[Any]) -> Any:
    deduped = list(dict.fromkeys(types))
    return reduce(or_, deduped) if len(deduped) > 1 else deduped[0]


def _field_annotation(field: FieldInfo | ComputedFieldInfo) -> Any:
    raw = field.annotation if isinstance(field, FieldInfo) else field.return_type
    return _strip_none(raw)


def _wire_type(topic: str, declared: Any) -> Any:
    """The type actually on the wire for a direct mapping. The control loop's
    control-mode publisher is declared with the bare mode class but actually
    publishes a switching wrapper (`{"AutomaticMode": <mode> | null}`), which
    is also what the API reads. A send mapping only dumps the model it's
    given, so the declaration never mattered at runtime; describe the real
    wire shape for the spec (and payload validation)."""
    from thrs.classes.control import ControlMode  # noqa: PLC0415
    from thrs.control.switching import SwitchingControlMode  # noqa: PLC0415

    if (
        topic.endswith("/control-mode")
        and isinstance(declared, type)
        and issubclass(declared, ControlMode)
        and not issubclass(declared, SwitchingControlMode)
    ):
        return SwitchingControlMode[declared]
    return declared


def describe_mapping(mapping: object) -> list[tuple[str, Any]]:
    """(topic, payload type) pairs from a mapping, using its own topic-building logic."""
    if isinstance(mapping, PartialMqttMapping):
        fields = (
            mapping._cls.model_computed_fields
            if mapping._only_computed_fields
            else mapping._cls.model_fields
        )
        return [
            (mapping._topic(name, field), _field_annotation(field))
            for name, field in fields.items()
        ]
    if isinstance(mapping, DirectMqttMapping):
        # A multi-class mapping (the simulation inputs/outputs union) is one
        # entry per class; grouping by topic turns them into the payload anyOf.
        return [(mapping._topic, _wire_type(mapping._topic, t)) for t in mapping._types]
    if isinstance(mapping, ModuleMqttMapping):
        return [
            pair for sub in mapping._mappings.values() for pair in describe_mapping(sub)
        ]
    if isinstance(mapping, MergedModuleMqttMapping):
        return [
            *describe_mapping(mapping._sensor_values_mapping),
            *describe_mapping(mapping._control_values_mapping),
        ]
    raise TypeError(
        f"Don't know how to describe {type(mapping)!r} for the AsyncAPI spec"
    )


@dataclass
class _Entry:
    topic: str
    direction: Direction
    payload_type: Any
    retain: bool
    template: str
    param_name: str | None = None
    param_value: str | None = None


# A topic's channel template and the parameter value it fills in.
Classify = Callable[[str], tuple[str, str | None, str | None]]


def _classifier(config: Config) -> Classify:
    module_names = sorted(all_module_descriptions(), key=len, reverse=True)
    modules_alt = "|".join(re.escape(m) for m in module_names)
    kinds_alt = "|".join(re.escape(k) for k in TYPE_TOPIC_KINDS)
    controller = re.escape(config.mqtt_controller_topic_prefix)
    devices = re.escape(config.mqtt_devices_topic_prefix)
    suffix = re.escape(config.mqtt_controller_topic_suffix)
    control_suffix = re.escape(config.mqtt_control_topic_suffix)

    type_topic_re = re.compile(
        rf"^{controller}/(?P<module>{modules_alt})/(?P<kind>{kinds_alt})(?P<set>/{suffix})?$"
    )
    device_field_re = re.compile(
        rf"^{devices}/{re.escape(DEVICE_NAMESPACE)}/(?P<module>{modules_alt})/(?P<field>[^/]+)"
        rf"(?P<cmd>/{control_suffix})?$"
    )
    controller_field_re = re.compile(
        rf"^{controller}/(?P<module>{modules_alt})/(?P<field>[^/]+)$"
    )

    def classify(topic: str) -> tuple[str, str | None, str | None]:
        if m := type_topic_re.match(topic):
            kind, module, set_ = (
                m.group("kind"),
                m.group("module"),
                m.group("set") or "",
            )
            template = f"{config.mqtt_controller_topic_prefix}/{{module}}/{kind}{set_}"
            return (template, "module", module)
        if m := device_field_re.match(topic):
            module, field, cmd = (
                m.group("module"),
                m.group("field"),
                m.group("cmd") or "",
            )
            template = f"{config.mqtt_devices_topic_prefix}/{device_module_prefix(module)}/{{field}}{cmd}"
            return (template, "field", field)
        if m := controller_field_re.match(topic):
            module, field = m.group("module"), m.group("field")
            template = f"{config.mqtt_controller_topic_prefix}/{module}/{{field}}"
            return (template, "field", field)
        # Literal: either a global (non-module) topic, or a field with an
        # explicit ``topic_override`` that breaks the module/field pattern
        # outright (may live under another module, or a synthetic
        # dummy-pcs/dummy-pms namespace - see ComponentMeta.topic_override).
        return (topic, None, None)

    return classify


def _flatten(registrations: list[_Registration], classify: Classify) -> list[_Entry]:
    entries: list[_Entry] = []
    for registration in registrations:
        for topic, payload_type in describe_mapping(registration.mapping):
            template, param_name, param_value = classify(topic)
            entries.append(
                _Entry(
                    topic=topic,
                    direction=registration.direction,
                    payload_type=payload_type,
                    retain=registration.retain,
                    template=template,
                    param_name=param_name,
                    param_value=param_value,
                )
            )
    return entries


@dataclass
class _Group:
    template: str
    direction: Direction
    param_name: str | None
    types: set[Any] = dataclass_field(default_factory=set)
    param_values: set[str] = dataclass_field(default_factory=set)
    value_to_types: dict[str, set[Any]] = dataclass_field(
        default_factory=lambda: defaultdict(set)
    )
    retain: bool = False
    example_topics: set[str] = dataclass_field(default_factory=set)


def _group(entries: list[_Entry]) -> dict[tuple[str, str], _Group]:
    groups: dict[tuple[str, str], _Group] = {}
    for entry in entries:
        key = (entry.template, entry.direction)
        group = groups.get(key)
        if group is None:
            group = _Group(
                template=entry.template,
                direction=entry.direction,
                param_name=entry.param_name,
            )
            groups[key] = group
        group.types.add(entry.payload_type)
        group.retain = group.retain or entry.retain
        group.example_topics.add(entry.topic)
        if entry.param_value is not None:
            group.param_values.add(entry.param_value)
            group.value_to_types[entry.param_value].add(entry.payload_type)
    return groups


def _type_name(t: Any) -> str:
    return getattr(t, "__name__", str(t))


def _type_sort_key(t: Any) -> tuple[str, str]:
    """(name, module) so same-named classes across modules sort deterministically.

    Without __module__, id()-based tie-breaking shuffles types between runs and produces spurious diffs.
    """
    return (_type_name(t), getattr(t, "__module__", ""))


# --- The document ------------------------------------------------------------


def channel_key(template: str) -> str:
    """The channel key of an address template: its static segments joined by
    dots (``thrs/controller/{module}/parameters`` ->
    ``thrs.controller.parameters``), the same identity zero-mqtt-graphql
    derives for a topic group."""
    return ".".join(
        segment
        for segment in template.split("/")
        if not (segment.startswith("{") and segment.endswith("}"))
    )


def operation_key(template: str, direction: Direction) -> str:
    """The key of the operation for a channel template and direction, exactly
    as the document emits it: the channel key plus the direction."""
    return f"{channel_key(template)}.{direction}"


@dataclass(frozen=True)
class Document:
    """A built document, with what the extension needs to bind to it: the
    channel wiring it was built from and where each model's schema lives."""

    data: dict[str, Any]
    config: Config
    classify: Classify
    groups: Mapping[tuple[str, str], _Group]
    _schema_ref: Mapping[int, str]

    def schema_ref(self, cls: type) -> str:
        """The ``$ref`` of a payload or shared-definition class's schema."""
        try:
            return self._schema_ref[id(cls)]
        except KeyError:
            raise KeyError(f"{cls!r} has no schema in the document") from None

    def property_ref(self, schema_ref: str, key: str) -> str:
        """The ``$ref`` of the object a property of a schema holds (through a
        nullable ``anyOf``)."""
        schema = self.data["components"]["schemas"][
            schema_ref.removeprefix(SCHEMA_REF_PREFIX)
        ]
        prop = schema["properties"][key]
        for candidate in prop.get("anyOf", [prop]):
            if "$ref" in candidate:
                return candidate["$ref"]
        raise KeyError(f"{schema_ref}.{key} holds no object")

    def payload_ref(self, topic: str, direction: Direction) -> str | None:
        """The one ``$ref`` the message for ``topic`` (in ``direction``)
        carries, or None when the topic carries several payload types."""
        template, param, value = self.classify(topic)
        operation = self.data["operations"][operation_key(template, direction)]
        message_key = operation["messages"][0]["$ref"].rsplit("/", 1)[-1]
        message = self.data["channels"][channel_key(template)]["messages"][message_key]
        schema = message["payload"]
        if param and value:
            schema = message[f"x-{param}-schema"][value]
        return schema.get("$ref")

    def operation_ref(self, topic: str, direction: Direction) -> dict[str, Any]:
        """The operation of the document carrying ``topic`` in ``direction``
        (``send``: published by an application; ``receive``: subscribed by
        one), with the channel parameter the topic fills in."""
        template, param, value = self.classify(topic)
        key = operation_key(template, direction)
        if key not in self.data["operations"]:
            raise KeyError(f"no operation {key!r} carries {topic!r}")
        ref: dict[str, Any] = {"operation": key}
        if param and value:
            ref["parameters"] = {param: value}
        return ref


def build_document(
    config: Config = DEFAULT_CONFIG,
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
    extra_schema_classes: tuple[type, ...] = (),
) -> Document:
    """The document for the channel wiring under ``config``. The schemas of
    ``extra_schema_classes`` are included next to the payloads' (the shared
    component definitions the GraphQL types are served from)."""
    classify = _classifier(config)
    groups = _group(_flatten(_collect_registrations(config), classify))

    leaf_classes: list[Any] = []
    seen: set[int] = set()
    for group in groups.values():
        for t in sorted(group.types, key=_type_sort_key):
            if id(t) not in seen:
                seen.add(id(t))
                leaf_classes.append(t)
    for cls in extra_schema_classes:
        if id(cls) not in seen:
            seen.add(id(cls))
            leaf_classes.append(cls)
    schema_ref, schemas = _combined_schemas(leaf_classes)
    for cls in leaf_classes:
        _annotate_schema(
            schemas[schema_ref[id(cls)].removeprefix(SCHEMA_REF_PREFIX)], cls
        )

    return Document(
        data=_document(title, version, groups, schema_ref, schemas),
        config=config,
        classify=classify,
        groups=groups,
        _schema_ref=schema_ref,
    )


def build_asyncapi(
    config: Config = DEFAULT_CONFIG,
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
) -> dict[str, Any]:
    """The AsyncAPI document alone (no extension)."""
    return build_document(config, title=title, version=version).data


def _document(
    title: str,
    version: str,
    groups: Mapping[tuple[str, str], _Group],
    schema_ref: Mapping[int, str],
    schemas: dict[str, Any],
) -> dict[str, Any]:
    """The document for the registered (template, direction) groups."""
    by_template: dict[str, dict[str, _Group]] = defaultdict(dict)
    for (template, direction), group in groups.items():
        by_template[template][direction] = group

    channels: dict[str, Any] = {}
    operations: dict[str, Any] = {}
    templates_by_key: dict[str, str] = {}
    for template in sorted(by_template):
        key = channel_key(template)
        if key in templates_by_key:
            raise RuntimeError(
                f"channel key {key!r} is shared by {templates_by_key[key]!r} and "
                f"{template!r}"
            )
        templates_by_key[key] = template
        directions = by_template[template]

        # One message per distinct payload: both directions share it when they
        # carry the same types (the usual case), otherwise each gets its own.
        described = {d: _message(g, schema_ref) for d, g in sorted(directions.items())}
        if len(set(map(repr, described.values()))) == 1:
            messages = {"message": next(iter(described.values()))}
            message_of = {"send": "message", "receive": "message"}
        else:
            message_of = {"send": "sent", "receive": "received"}
            messages = {message_of[d]: m for d, m in described.items()}

        topics = sorted(set().union(*(g.example_topics for g in directions.values())))
        channel: dict[str, Any] = {
            "address": template,
            "description": f"{len(topics)} topic(s), e.g. {topics[0]}.",
        }
        param = next(iter(directions.values())).param_name
        if param:
            values = sorted(set().union(*(g.param_values for g in directions.values())))
            channel["parameters"] = {param: {"enum": values}}
        channel["messages"] = messages
        channel["x-ttl"] = CHANNEL_TTL
        channels[key] = channel

        for direction, group in sorted(directions.items()):
            binding: dict[str, Any] = {"qos": 1}
            if direction == "send":
                binding["retain"] = group.retain
            binding["bindingVersion"] = "0.2.0"
            kind = "Sent" if direction == "send" else "Received"
            operations[f"{key}.{direction}"] = {
                "action": direction,
                "summary": (
                    f"{kind} on {len(group.example_topics)} topic(s) matching the address."
                ),
                "channel": {"$ref": f"#/channels/{key}"},
                "messages": [
                    {"$ref": f"#/channels/{key}/messages/{message_of[direction]}"}
                ],
                "bindings": {"mqtt": binding},
            }

    return {
        "asyncapi": "3.0.0",
        "info": {"title": title, "version": version},
        "defaultContentType": "application/json",
        "servers": {
            "broker": {
                "host": f"{DEFAULT_CONFIG.mqtt_host}:{DEFAULT_CONFIG.mqtt_port}",
                "protocol": "mqtt",
                "protocolVersion": "5.0",
            }
        },
        "channels": channels,
        "operations": operations,
        "components": {"schemas": schemas},
    }


def _message(group: _Group, schema_ref: Mapping[int, str]) -> dict[str, Any]:
    """The message of one (template, direction) group: its payload (one
    ``$ref`` or an ``anyOf``) and, for a parametrized address,
    ``x-{param}-schema`` pinning each parameter value to its own schema so a
    topic can be validated against that instead of the union."""
    types = sorted(group.types, key=_type_sort_key)
    message: dict[str, Any] = {
        "title": " | ".join(_type_name(t) for t in types),
        "payload": _payload_schema(types, schema_ref),
    }
    if group.param_name:
        message[f"x-{group.param_name}-schema"] = {
            value: _payload_schema(sorted(vtypes, key=_type_sort_key), schema_ref)
            for value, vtypes in sorted(group.value_to_types.items())
        }
    return message


def _payload_schema(types: list[Any], schema_ref: Mapping[int, str]) -> dict[str, Any]:
    """Schema for a payload: a single `$ref` if it has one payload type, else
    an `anyOf` of the refs. Looks up `schema_ref` by object identity."""
    refs = [{"$ref": schema_ref[id(t)]} for t in types]
    return refs[0] if len(refs) == 1 else {"anyOf": refs}


# --- Schemas -------------------------------------------------------------------

ENUM_NAMES_KEY = "x-enum-varnames"
INVARIANTS_KEY = "x-invariants"
DERIVED_KEY = "x-derived"


class ContractJsonSchema(GenerateJsonSchema):
    """Pydantic's JSON Schema, with every enum's member names alongside its
    values (``x-enum-varnames``): the wire carries the value, the API serves
    the name. Every model property also carries its Python field name and
    every Python validator its recorded behaviour (``thrs.spec.validators``),
    so the bridge rejects - in pydantic's words - what the API rejects."""

    def enum_schema(self, schema: Any) -> JsonSchemaValue:
        json_schema = super().enum_schema(schema)
        json_schema[ENUM_NAMES_KEY] = [member.name for member in schema["members"]]
        return json_schema

    def model_schema(self, schema: Any) -> JsonSchemaValue:
        json_schema = super().model_schema(schema)
        cls = schema["cls"]
        properties = json_schema.get("properties", {})
        for name, fld in cls.model_fields.items():
            prop = properties.get(fld.alias or name)
            if prop is not None:
                prop[validators.PYTHON_NAME_KEY] = name
        rules = validators.field_rules_of(cls)
        if rules:
            json_schema[validators.FIELD_RULES_KEY] = rules
        return json_schema

    def function_after_schema(self, schema: Any) -> JsonSchemaValue:
        json_schema = super().function_after_schema(schema)
        function = schema["function"]["function"]
        # A number wrapped by a validator (a unit such as Ratio): record what
        # it does. Validators on models or fields are recorded with their
        # model (`x-invariants`, `x-field-rules`); pydantic's own are skipped.
        if schema["schema"].get("type") in ("float", "int") and not (
            validators.is_pydantic_internal(function)
        ):
            json_schema[validators.CLAMP_KEY] = validators.clamp_of(function)
        return json_schema


def _combined_schemas(leaf_classes: list[Any]) -> tuple[dict[int, str], dict[str, Any]]:
    ref_template = SCHEMA_REF_PREFIX + "{model}"
    if len(leaf_classes) == 1:
        (only,) = leaf_classes
        schema = only.model_json_schema(
            ref_template=ref_template, schema_generator=ContractJsonSchema
        )
        defs = schema.pop("$defs", {})
        title = schema.get("title") or only.__name__
        schemas = {**defs, title: schema}
        return {id(only): f"{SCHEMA_REF_PREFIX}{title}"}, schemas

    combined = reduce(or_, leaf_classes)
    schema = TypeAdapter(combined).json_schema(
        ref_template=ref_template, schema_generator=ContractJsonSchema
    )
    defs: dict[str, Any] = schema.get("$defs", {})
    members = schema.get("anyOf", [])
    if len(members) != len(leaf_classes):
        raise RuntimeError(
            f"Combined AsyncAPI schema generation produced {len(members)} union "
            f"members for {len(leaf_classes)} classes; pydantic's anyOf-ordering "
            "assumption this generator relies on no longer holds."
        )
    schema_ref = {
        id(cls): member["$ref"]
        for cls, member in zip(leaf_classes, members, strict=True)
    }
    return schema_ref, defs


def _annotate_schema(schema: dict[str, Any], cls: Any) -> None:
    """Add what a model's JSON Schema does not say by itself: its
    ``x-invariants`` and its ``x-derived`` components."""
    if not (isinstance(cls, type) and issubclass(cls, ThrsValues)):
        return
    if cls.invariants:
        schema[INVARIANTS_KEY] = [
            {
                "lhs": wire_key(invariant.lhs, cls.model_fields[invariant.lhs]),
                "op": invariant.op,
                "rhs": wire_key(invariant.rhs, cls.model_fields[invariant.rhs]),
                "error": invariant.error,
            }
            for invariant in cls.invariants
        ]
    derived = _derived_fields(cls)
    if derived:
        schema[DERIVED_KEY] = derived


def wire_key(name: str, field: FieldInfo | ComputedFieldInfo) -> str:
    """The by-alias JSON key of a field, as its model's alias generator set it."""
    if field.alias is None:
        raise RuntimeError(f"field {name!r} has no alias; not a ThrsValues model?")
    return field.alias


def _derived_fields(object_cls: type[ThrsValues]) -> list[dict[str, Any]]:
    """The ``computed_field``s of a whole object that mirror other
    components' stamped leaves, with the source of each leaf. Found by
    identity on a ``zero()`` instance; a computed field whose leaves are not
    all such copies is left out."""
    if not object_cls.model_computed_fields:
        return []
    with warnings.catch_warnings():
        # `zero()` builds placeholder values a model's own validators may warn
        # about; only the structure matters here.
        warnings.simplefilter("ignore")
        instance = object_cls.zero()
    sources: dict[int, dict[str, str]] = {}
    for name, fld in object_cls.model_fields.items():
        component = getattr(instance, name)
        if not isinstance(component, ThrsValues) or isinstance(component, Stamped):
            continue
        for leaf_name, leaf_fld in type(component).model_fields.items():
            leaf = getattr(component, leaf_name)
            if isinstance(leaf, Stamped):
                sources[id(leaf)] = {
                    "component": wire_key(name, fld),
                    "leaf": wire_key(leaf_name, leaf_fld),
                }
    derived: list[dict[str, Any]] = []
    for name, info in object_cls.model_computed_fields.items():
        value = getattr(instance, name)
        if not isinstance(value, ThrsValues) or isinstance(value, Stamped):
            continue
        leaves: dict[str, dict[str, Any]] = {}
        for leaf_name, leaf_fld in type(value).model_fields.items():
            leaf = getattr(value, leaf_name)
            source = sources.get(id(leaf))
            if source is not None:
                leaves[wire_key(leaf_name, leaf_fld)] = source
            elif isinstance(leaf, Stamped) and leaf == leaf_fld.default:
                # A leaf the mirror leaves at its (constant) default, e.g.
                # FlowSensor.quantity: serialized as-is.
                leaves[wire_key(leaf_name, leaf_fld)] = {
                    "constant": leaf.model_dump(by_alias=True, mode="json")
                }
            else:
                break
        else:
            if leaves:
                derived.append({"key": wire_key(name, info), "leaves": leaves})
    return derived


# --- Reading a document back (for tests that seed or capture MQTT) --------------


def operation_topic(ref: Mapping[str, Any], document: Mapping[str, Any]) -> str:
    """The concrete topic an operation reference stands for in ``document``:
    the operation's channel address with the reference's parameters filled in
    (what zero-mqtt-graphql resolves it to)."""
    operation = document["operations"][ref["operation"]]
    key = operation["channel"]["$ref"].rsplit("/", 1)[-1]
    parameters = ref.get("parameters") or {}
    return re.sub(
        r"\{([^{}]+)\}",
        lambda m: parameters[m.group(1)],
        document["channels"][key]["address"],
    )


def field_topics(
    cls: type[ThrsValues],
    topic_prefix: str,
    module_prefix: str,
    *,
    computed: bool = False,
) -> dict[str, str]:
    """Each field's MQTT topic, from the real mapping's own topic logic."""
    mapping = PartialMqttMapping(
        cls, topic_prefix, module_prefix, only_computed_fields=computed
    )
    fields = cls.model_computed_fields if computed else cls.model_fields
    return {name: mapping._topic(name, field) for name, field in fields.items()}


__all__ = [
    "DEFAULT_CONFIG",
    "DERIVED_KEY",
    "ENUM_NAMES_KEY",
    "INVARIANTS_KEY",
    "Document",
    "all_module_descriptions",
    "build_asyncapi",
    "build_document",
    "channel_key",
    "field_topics",
    "operation_key",
    "operation_topic",
    "simulation_io_classes",
    "spec_config",
    "wire_key",
]
