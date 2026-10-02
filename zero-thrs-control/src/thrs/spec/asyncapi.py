"""The AsyncAPI 3.0 document of the THRS control system.

Channels are recorded from the runtime's own channel wiring, so the document cannot drift from it.
"""

from __future__ import annotations

import copy
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

# The settings that shape a topic. The document keeps each as an address
# parameter, which its consumer fills in from the environment variable of the
# same name, as the THRS services do.
TOPIC_SETTINGS = tuple(
    name
    for name in Config.model_fields
    if name.startswith("mqtt_") and name.endswith(("_topic_prefix", "_topic_suffix"))
)


# The settings that locate the broker, kept as server variables the same way.
SERVER_SETTINGS = ("mqtt_host", "mqtt_port")

# The config the document is built with: each topic setting is its own
# placeholder. Only the topic settings are read, so nothing else is validated.
TEMPLATE_CONFIG = Config.model_construct().model_copy(
    update={name: f"{{{name}}}" for name in TOPIC_SETTINGS}
)

# Marks an address parameter as a setting and names its environment variable.
ENV_KEY = "x-env"

# e.g. thrs/controller/{module}/parameters; hyphenized field names never collide with these.
TYPE_TOPIC_KINDS = (
    "parameters",
    "control-mode",
    "controller-state",
    "manual-values",
    "automation-mode",
)

# As in thrs-api, a served value never expires into null.
CHANNEL_TTL = "unbounded"

SCHEMA_REF_PREFIX = "#/components/schemas/"

Direction = Literal["send", "receive"]


def all_module_descriptions() -> dict[str, ModuleDescription]:
    """Every distinct module, keyed by name; mode "thrs" covers all modes."""
    return dict(lookup_mode("thrs").control_modules)


# --- Recording connector ---


@dataclass
class _Registration:
    mapping: object
    direction: Direction
    retain: bool = False


class RecordingConnector(MqttConnector):
    """Fake MqttConnector that records what the *Channels constructors register."""

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
    # Any simulation can run, so both sides carry every simulation's
    # inputs/outputs classes, not just mode "thrs"'s.
    io_classes = simulation_io_classes()
    SimulationApiChannels(
        connector,
        config,
        tuple(dict.fromkeys(inputs for inputs, _ in io_classes.values())),
        tuple(dict.fromkeys(outputs for _, outputs in io_classes.values())),
    )
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


# --- (topic, payload type) pairs from the mappings ---


def _is_union(annotation: Any) -> bool:
    """`X | None` or `typing.Union` (which `Annotated[...] | None` produces)."""
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
    """The type actually on the wire for a direct mapping.

    The control-mode publisher is declared with the bare mode class but
    publishes a switching wrapper.
    """
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
        # A global topic, or a field whose ComponentMeta.topic_override breaks the pattern.
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
    """(name, module) so same-named classes sort deterministically across runs."""
    return (_type_name(t), getattr(t, "__module__", ""))


# --- The document ------------------------------------------------------------


def _settings_of(template: str) -> list[str]:
    """The topic settings in ``template``, in address order."""
    return [
        name for name in re.findall(r"\{(\w+)\}", template) if name in TOPIC_SETTINGS
    ]


def _setting(name: str) -> dict[str, str]:
    """The parameter or server variable of a ``Config`` setting."""
    return {"description": f"The {name.upper()} setting.", ENV_KEY: name.upper()}


def channel_key(template: str) -> str:
    """Static segments and setting names joined by dots; other parameters are dropped."""
    segments = []
    for segment in template.split("/"):
        name = segment.removeprefix("{").removesuffix("}")
        if name == segment or name in TOPIC_SETTINGS:
            segments.append(name)
    return ".".join(segments)


def operation_key(template: str, direction: Direction) -> str:
    """The operation key for a channel template and direction."""
    return f"{channel_key(template)}.{direction}"


@dataclass(frozen=True)
class Document:
    """A built document, plus the wiring and schema locations the extension binds to."""

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
        """The ``$ref`` of the object a schema property holds, also when nullable."""
        schema = self.data["components"]["schemas"][
            schema_ref.removeprefix(SCHEMA_REF_PREFIX)
        ]
        prop = schema["properties"][key]
        for candidate in prop.get("anyOf", [prop]):
            if "$ref" in candidate:
                return candidate["$ref"]
        raise KeyError(f"{schema_ref}.{key} holds no object")

    def payload_ref(self, topic: str, direction: Direction) -> str | None:
        """The payload ``$ref`` of ``topic``, or None when it carries several types."""
        template, param, value = self.classify(topic)
        operation = self.data["operations"][operation_key(template, direction)]
        message_key = operation["messages"][0]["$ref"].rsplit("/", 1)[-1]
        message = self.data["channels"][channel_key(template)]["messages"][message_key]
        schema = message["payload"]
        if param and value:
            schema = message[f"x-{param}-schema"][value]
        return schema.get("$ref")

    def operation_ref(self, topic: str, direction: Direction) -> dict[str, Any]:
        """The operation reference carrying ``topic`` in ``direction``, with its parameter."""
        template, param, value = self.classify(topic)
        key = operation_key(template, direction)
        if key not in self.data["operations"]:
            raise KeyError(f"no operation {key!r} carries {topic!r}")
        ref: dict[str, Any] = {"operation": key}
        if param and value:
            ref["parameters"] = {param: value}
        return ref


def build_document(
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
    extra_schema_classes: tuple[type, ...] = (),
) -> Document:
    """The document for the channel wiring, plus ``extra_schema_classes``."""
    config = TEMPLATE_CONFIG
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
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
) -> dict[str, Any]:
    """The AsyncAPI document alone (no extension)."""
    return build_document(title=title, version=version).data


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

        # Directions share a message when their payloads match.
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
        parameters: dict[str, Any] = {
            name: _setting(name) for name in _settings_of(template)
        }
        param = next(iter(directions.values())).param_name
        if param:
            values = sorted(set().union(*(g.param_values for g in directions.values())))
            parameters[param] = {"enum": values}
        if parameters:
            channel["parameters"] = parameters
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
                "host": ":".join(f"{{{name}}}" for name in SERVER_SETTINGS),
                "protocol": "mqtt",
                "protocolVersion": "5.0",
                "variables": {name: _setting(name) for name in SERVER_SETTINGS},
            }
        },
        "channels": channels,
        "operations": operations,
        "components": {"schemas": schemas},
    }


def _message(group: _Group, schema_ref: Mapping[int, str]) -> dict[str, Any]:
    """The message of one (template, direction) group.

    ``x-{param}-schema`` pins each parameter value to its own schema, so a
    topic validates against that, not the union.
    """
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
    """A single `$ref`, or an `anyOf` of refs for several payload types."""
    refs = [{"$ref": schema_ref[id(t)]} for t in types]
    return refs[0] if len(refs) == 1 else {"anyOf": refs}


# --- Schemas -------------------------------------------------------------------

ENUM_NAMES_KEY = "x-enum-varnames"
INVARIANTS_KEY = "x-invariants"
DERIVED_KEY = "x-derived"


class ContractJsonSchema(GenerateJsonSchema):
    """Pydantic's JSON Schema, plus enum member names and Python validator behaviour.

    The wire carries enum values but the API serves names; validators let the
    bridge reject what the API rejects.
    """

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
        # Only number units (e.g. Ratio); model/field validators are recorded with their model.
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
    """Add a model's ``x-invariants`` and ``x-derived`` components to its schema."""
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
    """The ``computed_field``s that mirror other components' stamped leaves, with their sources.

    Found by leaf identity on a ``zero()`` instance.
    """
    if not object_cls.model_computed_fields:
        return []
    with warnings.catch_warnings():
        # Validators may warn about zero() placeholders; only structure matters.
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
                # A constant default, e.g. FlowSensor.quantity.
                leaves[wire_key(leaf_name, leaf_fld)] = {
                    "constant": leaf.model_dump(by_alias=True, mode="json")
                }
            else:
                break
        else:
            if leaves:
                derived.append({"key": wire_key(name, info), "leaves": leaves})
    return derived


# --- Reading a document back (for tests) ---


def resolve_settings(document: Mapping[str, Any], config: Config) -> dict[str, Any]:
    """``document`` with each setting parameter filled in from ``config``, as
    zero-mqtt-graphql fills it in from the environment at load."""
    resolved = copy.deepcopy(dict(document))
    for channel in resolved["channels"].values():
        parameters = channel.get("parameters", {})
        for name in [n for n, p in parameters.items() if ENV_KEY in p]:
            del parameters[name]
            channel["address"] = channel["address"].replace(
                f"{{{name}}}", getattr(config, name)
            )
        if "parameters" in channel and not parameters:
            del channel["parameters"]
    for server in resolved["servers"].values():
        for name in server.pop("variables", {}):
            server["host"] = server["host"].replace(
                f"{{{name}}}", str(getattr(config, name))
            )
    return resolved


def operation_topic(ref: Mapping[str, Any], document: Mapping[str, Any]) -> str:
    """The concrete topic an operation reference resolves to in ``document``."""
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
    "DERIVED_KEY",
    "ENUM_NAMES_KEY",
    "ENV_KEY",
    "INVARIANTS_KEY",
    "SERVER_SETTINGS",
    "TEMPLATE_CONFIG",
    "TOPIC_SETTINGS",
    "Document",
    "all_module_descriptions",
    "build_asyncapi",
    "build_document",
    "channel_key",
    "field_topics",
    "operation_key",
    "operation_topic",
    "resolve_settings",
    "simulation_io_classes",
    "wire_key",
]
