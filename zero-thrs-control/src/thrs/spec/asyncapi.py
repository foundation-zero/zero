"""AsyncAPI 3.0 document generator for thrs-control.

FastStream is used only for spec generation (not at runtime - the runtime uses ``aiomqtt``
directly); real ``MqttMapping`` objects are reused so the spec cannot drift from the actual
topic layout. Parametrized channels (``{field}``, ``{module}``) emit a ``oneOf`` payload plus
``x-field-schema``/``x-module-schema`` extensions that pin each parameter value to its exact
schema. ``_rebuild_schemas_and_payloads`` disambiguates same-named Pydantic classes across
modules by qualifying them with their module path, preventing silent schema overwrites.
"""

from __future__ import annotations

import re
import warnings
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from functools import reduce
from operator import or_
from types import NoneType, UnionType
from typing import Any, Literal, get_args, get_origin

from faststream.mqtt import MQTTBroker, QoS
from faststream.specification import AsyncAPI
from pydantic import TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.orchestration.comms import (
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
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription
from thrs.runtime.descriptions.simulation import lookup_mode

# Only shapes the example topics printed in the spec -
# the runtime always reads these from Config/env, never from here.
DEFAULT_CONFIG = Config(_env_file=None)

# Topics with a fixed "kind" segment per module, e.g. thrs/controller/{module}/parameters.
# Field names are always hyphenized so they never collide with these.
TYPE_TOPIC_KINDS = (
    "parameters",
    "control-mode",
    "controller-state",
    "manual-values",
    "automation-mode",
)


def all_module_descriptions() -> dict[str, ModuleDescription]:
    """Every distinct module, keyed by name. Mode "thrs" covers the union of all modes."""
    return dict(lookup_mode("thrs").control_modules)


# --- Recording connector: builds the real mapping graph, records nothing else ---


@dataclass
class _Registration:
    mapping: object
    direction: Literal["send", "receive"]
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


def _collect_registrations() -> list[_Registration]:
    config = DEFAULT_CONFIG
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
    SimulationApiChannels(
        connector, config, simulation_inputs_cls, simulation_outputs_cls
    )
    DirectivesChannels(connector, config)
    DirectivesApiChannels(connector, config)

    return connector.registrations


# --- Reading (topic, payload type) pairs back off the real mappings ---


def _strip_none(annotation: Any) -> Any:
    if get_origin(annotation) is UnionType:
        args = [a for a in get_args(annotation) if a is not NoneType]
        return _union(args) if len(args) > 1 else args[0]
    return annotation


def _union(types: list[Any]) -> Any:
    deduped = list(dict.fromkeys(types))
    return reduce(or_, deduped) if len(deduped) > 1 else deduped[0]


def _field_annotation(field: FieldInfo | ComputedFieldInfo) -> Any:
    raw = field.annotation if isinstance(field, FieldInfo) else field.return_type
    return _strip_none(raw)


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
        types = list(mapping._types)
        payload = types[0] if len(types) == 1 else _union(types)
        return [(mapping._topic, payload)]
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
    direction: Literal["send", "receive"]
    payload_type: Any
    retain: bool
    template: str
    param_name: str | None = None
    param_value: str | None = None


def _flatten(registrations: list[_Registration]) -> list[_Entry]:
    module_names = sorted(all_module_descriptions(), key=len, reverse=True)
    classify = _classifier(module_names, DEFAULT_CONFIG)

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


def _classifier(module_names: list[str], config: Config):
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
        rf"^{devices}/500000-thrs/(?P<module>{modules_alt})/(?P<field>[^/]+)"
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
            template = f"{config.mqtt_devices_topic_prefix}/500000-thrs/{module}/{{field}}{cmd}"
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


@dataclass
class _Group:
    template: str
    direction: Literal["send", "receive"]
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


def _handler(payload_type: Any):
    async def handler(msg):
        return None

    handler.__annotations__ = {"msg": payload_type}
    return handler


def build_asyncapi(
    title: str = "THRS Control", version: str = "1.0.0"
) -> dict[str, Any]:
    """Build the AsyncAPI 3.0 doc from the real channel wiring in orchestration.comms."""
    registrations = _collect_registrations()
    entries = _flatten(registrations)
    groups = _group(entries)

    broker = MQTTBroker(f"{DEFAULT_CONFIG.mqtt_host}:{DEFAULT_CONFIG.mqtt_port}")
    # Keyed by (template, direction): send/receive can share an address template but have
    # different schemas (e.g. thrs/controller/{module}/control-mode), so direction disambiguates.
    channel_metadata: dict[tuple[str, str], dict[str, Any]] = {}

    for group in groups.values():
        types = sorted(group.types, key=_type_sort_key)
        schema = types[0] if len(types) == 1 else _union(types)
        description = _describe_group(group, types)

        if group.direction == "send":
            broker.publisher(
                group.template,
                schema=schema,
                qos=QoS.AT_LEAST_ONCE,
                retain=group.retain,
                description=description,
            )
        else:
            broker.subscriber(
                group.template,
                qos=QoS.AT_LEAST_ONCE,
                description=description,
            )(_handler(schema))

        if group.param_name:
            # Just the parameter enum here. `_rebuild_schemas_and_payloads`
            # adds `x-{param}-schema` later, where it has `ref_for` to point
            # each value at its exact component schema instead of a short (and
            # possibly ambiguous) class name.
            metadata: dict[str, Any] = {
                "parameters": {group.param_name: {"enum": sorted(group.param_values)}}
            }
            channel_metadata[(group.template, group.direction)] = metadata

    with warnings.catch_warnings():
        # FastStream warns about same-named classes here - harmless since
        # _rebuild_schemas_and_payloads replaces components.schemas anyway.
        warnings.filterwarnings(
            "ignore",
            message=r"Overwriting the message schema.*",
            category=RuntimeWarning,
        )
        doc = (
            AsyncAPI(broker, title=title, version=version)
            .to_specification()
            .to_jsonable()
        )
    _decode_braced_refs(doc)
    _rebuild_schemas_and_payloads(doc, groups)
    _apply_channel_metadata(doc, channel_metadata)
    _sort_top_level_maps(doc)
    return doc


def _describe_group(group: _Group, types: list[Any]) -> str:
    kind = "Sent" if group.direction == "send" else "Received"
    if len(types) == 1:
        return f"{kind} on {len(group.example_topics)} topic(s) matching this address."
    return (
        f"{kind} on {len(group.example_topics)} topic(s) matching this address; "
        f"payload shape depends on {{{group.param_name}}} - see x-{group.param_name}-schema."
    )


def _sort_top_level_maps(doc: dict[str, Any]) -> None:
    """Sort channels/operations/messages by key for reproducible output.
    FastStream's broker registry doesn't guarantee iteration order."""
    doc["channels"] = dict(sorted(doc.get("channels", {}).items()))
    doc["operations"] = dict(sorted(doc.get("operations", {}).items()))
    components = doc.get("components", {})
    for key in ("messages", "schemas"):
        if key in components:
            components[key] = dict(sorted(components[key].items()))


def _decode_braced_refs(node: Any) -> None:
    """Decode %7B/%7D back to braces in $ref values.
    FastStream encodes them in refs but keeps them raw in channel/component keys."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                node[key] = value.replace("%7B", "{").replace("%7D", "}")
            else:
                _decode_braced_refs(value)
    elif isinstance(node, list):
        for item in node:
            _decode_braced_refs(item)


def _rebuild_schemas_and_payloads(
    doc: dict[str, Any], groups: dict[tuple[str, str], _Group]
) -> None:
    """Regenerate components.schemas in one combined pass and repoint message payloads.
    Fixes same-named classes across modules that FastStream's per-channel pass conflates."""
    leaf_classes: list[Any] = []
    seen: set[int] = set()
    for group in groups.values():
        for t in sorted(group.types, key=_type_sort_key):
            if id(t) not in seen:
                seen.add(id(t))
                leaf_classes.append(t)

    if not leaf_classes:
        return

    ref_for, schemas = _combined_schemas(leaf_classes)
    doc.setdefault("components", {})["schemas"] = schemas

    for (template, direction), group in groups.items():
        channel = _find_channel(doc, template, direction)
        if channel is None:
            continue
        message = _find_message(doc, channel)
        if message is None:
            continue
        types = sorted(group.types, key=_type_sort_key)
        if len(types) == 1:
            message["payload"] = {"$ref": ref_for[id(types[0])]}
        else:
            original_title = message.get("payload", {}).get("title")
            payload: dict[str, Any] = {
                "anyOf": [{"$ref": ref_for[id(t)]} for t in types]
            }
            if original_title:
                payload["title"] = original_title
            message["payload"] = payload

        # A multi-type `{param}` group's message payload is the anyOf of every
        # branch, so validating a concrete topic against it can't catch an
        # out-of-bounds value (it still matches some branch). `x-{param}-schema`
        # pins each value to its own schema(s) as $refs, so zero-mqtt-graphql can
        # validate per topic, like thrs-api's per-field validation.
        if group.param_name and len(types) > 1:
            channel[f"x-{group.param_name}-schema"] = {
                value: _field_schema(sorted(vtypes, key=_type_sort_key), ref_for)
                for value, vtypes in sorted(group.value_to_types.items())
            }


def _field_schema(types: list[Any], ref_for: dict[int, str]) -> dict[str, Any]:
    """Schema for one `{param}` value: a single `$ref` if it has one payload
    type, else an `anyOf` of the refs. Looks up `ref_for` by object identity,
    same as the message payloads."""
    refs = [{"$ref": ref_for[id(t)]} for t in types]
    return refs[0] if len(refs) == 1 else {"anyOf": refs}


def _combined_schemas(leaf_classes: list[Any]) -> tuple[dict[int, str], dict[str, Any]]:
    if len(leaf_classes) == 1:
        (only,) = leaf_classes
        schema = only.model_json_schema(ref_template="#/components/schemas/{model}")
        defs = schema.pop("$defs", {})
        title = schema.get("title") or only.__name__
        schemas = {**defs, title: schema}
        return {id(only): f"#/components/schemas/{title}"}, schemas

    combined = reduce(or_, leaf_classes)
    schema = TypeAdapter(combined).json_schema(
        ref_template="#/components/schemas/{model}"
    )
    defs: dict[str, Any] = schema.get("$defs", {})
    members = schema.get("anyOf", [])
    if len(members) != len(leaf_classes):
        raise RuntimeError(
            f"Combined AsyncAPI schema generation produced {len(members)} union "
            f"members for {len(leaf_classes)} classes; pydantic's anyOf-ordering "
            "assumption this generator relies on no longer holds."
        )
    ref_for = {
        id(cls): member["$ref"]
        for cls, member in zip(leaf_classes, members, strict=True)
    }
    return ref_for, defs


def _find_channel(
    doc: dict[str, Any], template: str, direction: str
) -> dict[str, Any] | None:
    suffixes = (":Publisher",) if direction == "send" else (":Handler", ":Subscriber")
    for channel in doc.get("channels", {}).values():
        address = channel.get("address", "")
        if any(address == f"{template}{suffix}" for suffix in suffixes):
            return channel
    return None


def _find_message(
    doc: dict[str, Any], channel: dict[str, Any]
) -> dict[str, Any] | None:
    for message_ref in channel.get("messages", {}).values():
        key = message_ref.get("$ref", "").rsplit("/", 1)[-1]
        message = doc.get("components", {}).get("messages", {}).get(key)
        if message is not None:
            return message
    return None


def _direction_from_address(address: str) -> Literal["send", "receive"] | None:
    if address.endswith(":Publisher"):
        return "send"
    if address.endswith((":Handler", ":Subscriber")):
        return "receive"
    return None


def _apply_channel_metadata(
    doc: dict[str, Any], channel_metadata: dict[tuple[str, str], dict[str, Any]]
) -> None:
    """Inject parameters block, x-*-schema extensions, and MQTT wildcard topics for {param} channels.
    Keyed by (template, direction) because send/receive can share an address with different schemas."""
    for channel in doc.get("channels", {}).values():
        address = channel.get("address", "")
        if "{" not in address:
            continue
        direction = _direction_from_address(address)
        template = address.rsplit(":", 1)[0] if ":" in address else address
        metadata = channel_metadata.get((template, direction)) if direction else None
        if metadata:
            channel.update(metadata)
        bindings = channel.get("bindings", {}).get("mqtt")
        if bindings and "topic" in bindings:
            bindings["topic"] = re.sub(r"\{[^{}]+\}", "+", bindings["topic"])

# --- Per-module `{field}` group metadata (for zero-mqtt-graphql list queries) ---


def _strip_field_param(template: str) -> str:
    """Group identity for a `.../{field}` template: everything before the final
    `{field}` segment. Must match zero-mqtt-graphql's `group_identity()`
    (src/asyncapi.rs) exactly, or it won't merge the metadata file in."""
    prefix, _, param = template.rpartition("/")
    if param != "{field}":
        raise ValueError(f"expected a trailing {{field}} segment, got {template!r}")
    return prefix


def _module_metadata_entry(
    field_name: str,
    field: FieldInfo | ComputedFieldInfo,
    topic: str,
) -> dict[str, Any]:
    extra = field.json_schema_extra
    extra = extra if isinstance(extra, dict) else {}
    return {
        "topic": topic,
        "metadata": {
            "field": field_name,
            "yard_tag": extra.get("yard_tag") or None,
            "component_type": extra.get("component_type"),
            "valve_type": extra.get("valve_type"),
        },
    }


def _field_topics(
    fields: Mapping[str, FieldInfo | ComputedFieldInfo],
    topic_prefix: str,
    module_prefix: str,
) -> dict[str, str]:
    """Map each field name to its MQTT topic the same way
    ``PartialMqttMapping._topic`` does (src/thrs/orchestration/comms.py): a
    ``topic_override`` skips ``module_prefix``, otherwise the topic is
    ``{module_prefix}/{hyphenize(field_name)}``. Going forward (field -> topic)
    avoids reverse-parsing a slug back into a field name, which breaks when
    hyphenization isn't a plain underscore swap (both happen in DHW's
    sensor-values model: an override pointing elsewhere, and a compound word)."""
    from thrs.input_output.base import get_topic  # noqa: PLC0415
    from thrs.utils.string import hyphenize  # noqa: PLC0415

    return {
        name: (
            f"{topic_prefix}/"
            f"{get_topic(field) or f'{module_prefix}/{hyphenize(name)}'}"
        )
        for name, field in fields.items()
    }


def build_module_metadata(
    module_name: str,
    kind: Literal["sensors", "controller"],
) -> dict[str, Any]:
    """Identity metadata for one THRS module's `{field}` topic group.

    zero-mqtt-graphql only exposes a list query for a parametrized channel once
    a ``*-metadata.json`` file enumerates its concrete topics (see
    src/metadata.rs, and ``specs/power-tags-metadata.json`` for the same thing
    from zero-power-tags). Each module publishes two such ``{field}`` channels:
    raw sensor values (``{devices_prefix}/500000-thrs/{module}/{field}``, from
    the ``SensorValues`` model fields, ``kind="sensors"``) and, for modules with
    computed fields, the derived values (``{controller_prefix}/{module}/{field}``,
    from the same model's ``computed_field``s, ``kind="controller"``). The UI
    reads both (e.g. zero-ui's ``THRUSTERS_SENSOR_QUERY``) but can't query them
    on zero-mqtt-graphql without this file.

    Topics come from the real channel wiring (``_collect_registrations`` /
    ``_flatten`` / ``_group``, same as ``build_asyncapi``) so they can't drift,
    and each field's ``ComponentMeta``
    (``yard_tag``/``component_type``/``valve_type``) is read off the model for a
    bit more than the bare topic. The ``field`` attribute is the model's
    snake_case name, not the hyphenized slug, so it lines up with thrs-api's
    GraphQL field names when cross-checking.

    Raises ``ValueError`` for an unknown module, ``RuntimeError`` for
    ``kind="controller"`` on a module with no computed fields.
    """
    modules = all_module_descriptions()
    if module_name not in modules:
        raise ValueError(
            f"unknown THRS module {module_name!r}; known modules: "
            f"{sorted(modules)}"
        )
    sensor_values_cls = modules[module_name].sensor_values_cls

    if kind == "sensors":
        topic_prefix = DEFAULT_CONFIG.mqtt_devices_topic_prefix
        module_prefix = f"500000-thrs/{module_name}"
        template = f"{topic_prefix}/{module_prefix}/{{field}}"
        fields: Mapping[str, FieldInfo | ComputedFieldInfo] = (
            sensor_values_cls.model_fields
        )
    else:
        topic_prefix = DEFAULT_CONFIG.mqtt_controller_topic_prefix
        module_prefix = module_name
        template = f"{topic_prefix}/{module_prefix}/{{field}}"
        fields = sensor_values_cls.model_computed_fields

    if not fields:
        raise RuntimeError(
            f"Module {module_name!r} has no {kind} fields to enumerate "
            f"(kind='controller' only applies to modules with computed "
            "fields - see modules_with_computed_fields())."
        )

    all_field_topics = _field_topics(fields, topic_prefix, module_prefix)

    # A `topic_override` (see ComponentMeta) can put a field outside this
    # group's `{module_prefix}/{field}` path (e.g. thrusters'
    # `thrusters_thruster_aft` -> "dummy-pcs/thruster-aft-active", or some DC
    # fields -> "dummy-pms/..."). Those are their own concrete topics elsewhere,
    # already queryable without a metadata file, so drop them here.
    group_prefix = f"{topic_prefix}/{module_prefix}/"
    field_topics = {
        name: topic
        for name, topic in all_field_topics.items()
        if topic.startswith(group_prefix)
    }
    if not field_topics:
        raise RuntimeError(
            f"Every {kind} field of module {module_name!r} has a "
            "topic_override pointing outside this group - nothing to "
            "enumerate here (they're already queryable as concrete topics)."
        )

    # Sanity check: every remaining topic should show up in the registered
    # group for this template, so the metadata can't drift from what's
    # actually published.
    registrations = _collect_registrations()
    entries = _flatten(registrations)
    groups = _group(entries)
    topic_group = groups.get((template, "send"))
    if topic_group is None:
        raise RuntimeError(
            f"No published topic group found for template {template!r} "
            f"(module={module_name!r}, kind={kind!r})."
        )
    missing = set(field_topics.values()) - topic_group.example_topics
    if missing:
        raise RuntimeError(
            f"Computed topics for module {module_name!r} kind={kind!r} "
            f"don't match the registered channel wiring: {sorted(missing)}"
        )

    return {
        "group": _strip_field_param(template),
        "topics": [
            _module_metadata_entry(name, fields[name], topic)
            for name, topic in sorted(field_topics.items(), key=lambda kv: kv[1])
        ],
    }


def _view_gql_name(snake: str) -> str:
    """``snake_case`` -> ``lowerCamelCase``, the way Strawberry names fields for
    thrs-api (``use_pydantic_alias=False``): ``position_rel`` -> ``positionRel``."""
    head, *tail = snake.split("_")
    return head + "".join(word[:1].upper() + word[1:] for word in tail)


def _view_leaf_scalar(value: Any) -> str:
    """GraphQL scalar for a leaf, from its zeroed wire value (check ``bool``
    before ``int``, since ``bool`` subclasses ``int``)."""
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, int):
        return "Int"
    if isinstance(value, float):
        return "Float"
    return "String"


def build_module_view(module_name: str) -> dict[str, Any]:
    """The nested per-module view zero-mqtt-graphql uses to serve
    ``modules.<module>.sensorValues`` 1:1 with thrs-api (see
    ``zero-mqtt-graphql/src/modules_view.rs``).

    Where ``build_module_metadata`` covers one ``{field}`` group (and so leaves
    out ``topic_override`` fields), this lists every ``sensorValues`` field the
    UI reads, raw and computed, overrides included, since they all live under
    ``modules.<module>.sensorValues`` on thrs-api. Per field it emits the GraphQL
    name, the MQTT topic, and each ``{value, timestamp}`` leaf's GraphQL name and
    raw PascalCase wire key. Names come from the pydantic model (snake -> camel
    for GraphQL, the ``to_pascal`` alias for the wire key) so it can't drift from
    thrs-api's schema; leaf types are read off a zeroed instance.

    Computed fields (``model_computed_fields``) are published by THRS-control on
    ``{controller_prefix}/<module>/<field>`` and just relayed (not re-derived);
    they get ``"computed": true``.
    """
    from pydantic.alias_generators import to_pascal  # noqa: PLC0415

    from thrs.input_output.base import Stamped, ThrsValues  # noqa: PLC0415

    modules = all_module_descriptions()
    if module_name not in modules:
        raise ValueError(
            f"unknown THRS module {module_name!r}; known modules: {sorted(modules)}"
        )
    sensor_cls = modules[module_name].sensor_values_cls

    # A zeroed instance gives each leaf's scalar type (read off the live
    # `Stamped.value`, so it doesn't depend on the model's `alias_generator` -
    # SensorValues classes vary between to_snake and to_pascal). Computed props
    # are evaluated on the zeros; any that choke on zeros fall back to Float.
    model = sensor_cls.zero()

    raw_topics = _field_topics(
        sensor_cls.model_fields,
        DEFAULT_CONFIG.mqtt_devices_topic_prefix,
        f"500000-thrs/{module_name}",
    )
    computed_topics = (
        _field_topics(
            sensor_cls.model_computed_fields,
            DEFAULT_CONFIG.mqtt_controller_topic_prefix,
            module_name,
        )
        if sensor_cls.model_computed_fields
        else {}
    )

    def _component_cls(annotation: Any) -> type | None:
        inner = _strip_none(annotation)
        if isinstance(inner, type) and issubclass(inner, ThrsValues):
            return inner
        return None

    def _entry(name: str, annotation: Any, topic: str | None, computed: bool):
        component_cls = _component_cls(annotation)
        if component_cls is None or topic is None:
            return None
        try:
            component = getattr(model, name)
        except Exception:  # noqa: BLE001 - computed prop that chokes on zeros
            component = None
        leaves = []
        for leaf_snake, leaf_field in component_cls.model_fields.items():
            leaf_inner = _strip_none(leaf_field.annotation)
            if not (isinstance(leaf_inner, type) and issubclass(leaf_inner, Stamped)):
                continue
            raw = leaf_field.alias or to_pascal(leaf_snake)
            leaf_value = getattr(getattr(component, leaf_snake, None), "value", None)
            leaves.append(
                {
                    "gql": _view_gql_name(leaf_snake),
                    "raw": raw,
                    "type": _view_leaf_scalar(leaf_value),
                }
            )
        if not leaves:
            return None
        return {
            "gqlField": _view_gql_name(name),
            "topic": topic,
            "leaves": leaves,
            "computed": computed,
        }

    entries = [
        entry
        for name, field in sensor_cls.model_fields.items()
        if (entry := _entry(name, field.annotation, raw_topics.get(name), False))
    ]
    entries += [
        entry
        for name, cfield in sensor_cls.model_computed_fields.items()
        if (entry := _entry(name, cfield.return_type, computed_topics.get(name), True))
    ]
    entries.sort(key=lambda e: e["gqlField"])
    return {"module": module_name, "sensorValues": entries}


def modules_with_computed_fields() -> list[str]:
    """THRS modules whose sensor-values model has a ``computed_field``, i.e.
    those with a ``kind="controller"`` metadata group. The rest (currently pcm,
    consumers, adsorption, drives, dc) have nothing to enumerate for that kind."""
    return sorted(
        name
        for name, description in all_module_descriptions().items()
        if description.sensor_values_cls.model_computed_fields
    )
