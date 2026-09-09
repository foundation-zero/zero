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
    value_to_type_names: dict[str, set[str]] = dataclass_field(
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
            group.value_to_type_names[entry.param_value].add(
                getattr(entry.payload_type, "__name__", str(entry.payload_type))
            )
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
            metadata: dict[str, Any] = {
                "parameters": {group.param_name: {"enum": sorted(group.param_values)}}
            }
            if len(types) > 1:
                metadata[f"x-{group.param_name}-schema"] = {
                    value: sorted(names)
                    for value, names in sorted(group.value_to_type_names.items())
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
