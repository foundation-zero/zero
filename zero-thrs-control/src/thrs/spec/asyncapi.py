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
from enum import Enum
from functools import reduce
from operator import or_
from types import NoneType, UnionType
from typing import Any, Literal, Union, cast, get_args, get_origin

import annotated_types as at
from faststream.mqtt import MQTTBroker, QoS
from faststream.specification import AsyncAPI
from pydantic import BaseModel, ConfigDict, TypeAdapter
from pydantic.fields import ComputedFieldInfo, FieldInfo
from strawberry import UNSET
from strawberry.utils.str_converters import to_camel_case

from thrs.control.switching import AutomationMode, SwitchingControlMode
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


def _spec_config(
    devices_prefix: str | None = None,
    controller_prefix: str | None = None,
    simulator_prefix: str | None = None,
) -> Config:
    """``DEFAULT_CONFIG`` with the chosen MQTT topic prefixes baked in. Every
    generator wires the real ``*Channels`` classes with this config, so a chosen
    prefix lands in the emitted topics the same way it would at runtime; an
    omitted prefix keeps the historical (default) one."""
    overrides = {
        "mqtt_devices_topic_prefix": devices_prefix,
        "mqtt_controller_topic_prefix": controller_prefix,
        "mqtt_simulator_topic_prefix": simulator_prefix,
    }
    return DEFAULT_CONFIG.model_copy(
        update={key: value for key, value in overrides.items() if value}
    )


def _collect_registrations(config: Config = DEFAULT_CONFIG) -> list[_Registration]:
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
    # thrs-api subscribes to the simulation inputs/outputs topics with the
    # union of *every* simulation's model (see `thrs.graphql.strawberry`), not
    # just mode "thrs"'s: whichever simulation runs publishes its own class.
    # Describe the API side that way so the channel payload (and so
    # zero-mqtt-graphql's payload validation) accepts each of them.
    from thrs.graphql.simulation import io_mapping  # noqa: PLC0415

    SimulationApiChannels(
        connector,
        config,
        tuple(dict.fromkeys(inputs for inputs, _ in io_mapping.values())),
        tuple(dict.fromkeys(outputs for _, outputs in io_mapping.values())),
    )
    # The simulator side (`SimulationChannels` above) publishes the running
    # mode's own inputs/outputs classes; the spec is built from mode "thrs"
    # only, but every simulation can run. Declare each simulation's classes as
    # publishers of those topics too, so the channel payload is the anyOf of
    # all of them (what the wire can carry) rather than mode "thrs"'s alone.
    for inputs_cls, outputs_cls in io_mapping.values():
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
    is also what thrs-api reads. A send mapping only dumps the model it's
    given, so the declaration never mattered at runtime; describe the real
    wire shape for the spec (and zero-mqtt-graphql's payload validation)."""
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
    direction: Literal["send", "receive"]
    payload_type: Any
    retain: bool
    template: str
    param_name: str | None = None
    param_value: str | None = None


def _flatten(
    registrations: list[_Registration], config: Config = DEFAULT_CONFIG
) -> list[_Entry]:
    module_names = sorted(all_module_descriptions(), key=len, reverse=True)
    classify = _classifier(module_names, config)

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
    title: str = "THRS Control",
    version: str = "1.0.0",
    devices_prefix: str | None = None,
    controller_prefix: str | None = None,
) -> dict[str, Any]:
    """Build the AsyncAPI 3.0 doc from the real channel wiring in orchestration.comms.

    devices_prefix/controller_prefix bake a chosen MQTT topic prefix into the
    emitted channels (the channels are wired with a config carrying them, see
    ``_spec_config``), matching the flags on the module-view/metadata/mutation
    generators so the whole spec set targets one broker prefix consistently.
    Defaults reproduce the historical prefixes."""
    config = _spec_config(devices_prefix, controller_prefix)
    registrations = _collect_registrations(config)
    entries = _flatten(registrations, config)
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


def build_module_metadata(
    module_name: str,
    kind: Literal["sensors", "controller"],
    devices_prefix: str | None = None,
    controller_prefix: str | None = None,
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
            f"unknown THRS module {module_name!r}; known modules: {sorted(modules)}"
        )
    sensor_values_cls = modules[module_name].sensor_values_cls
    # The chosen prefixes go into the config the channels are wired with, so the
    # emitted topics and the sanity check below see the same ones.
    config = _spec_config(devices_prefix, controller_prefix)

    if kind == "sensors":
        topic_prefix = config.mqtt_devices_topic_prefix
        module_prefix = device_module_prefix(module_name)
        template = f"{topic_prefix}/{module_prefix}/{{field}}"
        fields: Mapping[str, FieldInfo | ComputedFieldInfo] = (
            sensor_values_cls.model_fields
        )
    else:
        topic_prefix = config.mqtt_controller_topic_prefix
        module_prefix = module_name
        template = f"{topic_prefix}/{module_prefix}/{{field}}"
        fields = sensor_values_cls.model_computed_fields

    if not fields:
        raise RuntimeError(
            f"Module {module_name!r} has no {kind} fields to enumerate "
            f"(kind='controller' only applies to modules with computed "
            "fields - see modules_with_computed_fields())."
        )

    all_field_topics = _field_topics(
        sensor_values_cls, topic_prefix, module_prefix, computed=kind != "sensors"
    )

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
    registrations = _collect_registrations(config)
    entries = _flatten(registrations, config)
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


def _wire_key(name: str, field: FieldInfo | ComputedFieldInfo) -> str:
    """The by-alias JSON key of a field, as its model's alias generator set it."""
    if field.alias is None:
        raise RuntimeError(f"field {name!r} has no alias; not a ThrsValues model?")
    return field.alias


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


def _flat_graphql_type(annotation: Any) -> str | None:
    """GraphQL type for a plain (non-Stamped) field: a scalar (Float/Int/Boolean)
    or a collection (tuple/list -> [Float!]/[Int!]/[Boolean!]). None for
    anything else. Shared by the module-view object sections and the
    parameter-mutation return object so both describe a parameters field the
    same way."""
    base = _bare_type(annotation)
    origin = get_origin(base)
    if origin in (list, tuple):
        args = [_bare_type(a) for a in get_args(base) if a is not Ellipsis]
        inner = args[0] if args else float
        scalar = "Int" if inner is int else "Boolean" if inner is bool else "Float"
        return f"[{scalar}!]"
    if base is bool:
        return "Boolean"
    if base is int:
        return "Int"
    if base is float:
        return "Float"
    return None


def _bare_type(annotation: Any) -> Any:
    """Peel Optional[...] and Annotated[..., meta] wrappers, in any nesting
    order, down to the bare type (OptionalSeconds is
    Annotated[float | None, ...]; a unit is Annotated[float, Field(...)]; a
    leaf may be Stamped[X] | None)."""
    base = annotation
    while True:
        stripped = _strip_none(base)
        if getattr(stripped, "__metadata__", None) is not None:  # Annotated[T, ...]
            stripped = stripped.__args__[0]
        if stripped is base:
            return base
        base = stripped


def _is_optional(annotation: Any) -> bool:
    """Whether the annotation admits None at any wrapper level (X | None,
    Annotated[X | None, ...], Stamped[X | None])."""
    base = annotation
    while True:
        if _is_union(base) and NoneType in get_args(base):
            return True
        if getattr(base, "__metadata__", None) is not None:
            base = base.__args__[0]
            continue
        return False


def _leaf_type_from_annotation(annotation: Any) -> str:
    """GraphQL type for a Stamped[X] leaf read off its declared type: a scalar,
    or [Float!] for a tuple leaf (a PID controller-state's tuning/components).
    Declared types are what thrs-api's Strawberry conversion uses, so this -
    not the zeroed instance - is authoritative: a computed leaf whose value is
    None on zeros (Stamped[OptionalCelsius]) is a nullable Float, not a
    String."""
    inner = _bare_type(annotation)
    value_field = (
        getattr(inner, "model_fields", {}).get("value")
        if isinstance(inner, type)
        else None
    )
    if value_field is None:
        return "String"
    return _flat_graphql_type(value_field.annotation) or "String"


def _leaf_value_optional(annotation: Any) -> bool:
    """Whether a Stamped[X] leaf's value is nullable in thrs-api's schema
    (Stamped[X | None] or the leaf field itself optional)."""
    if _is_optional(annotation):
        return True
    inner = _bare_type(annotation)
    value_field = (
        getattr(inner, "model_fields", {}).get("value")
        if isinstance(inner, type)
        else None
    )
    return value_field is not None and _is_optional(value_field.annotation)


def _strawberry_type(cls: type) -> Any:
    """thrs-api's Strawberry type for a pydantic model: the one
    ``pydantic_to_strawberry_type`` recorded for it, else what
    ``strawberry.experimental.pydantic.type`` set on the model itself. An
    unregistered subclass inherits its base's (PropulsionDrive ->
    SimulationHeatSourceType), which is exactly what thrs-api serves for it."""
    import thrs.graphql.strawberry  # noqa: F401, PLC0415 - registers the types
    from thrs.graphql.helpers import pydantic_to_strawberry_class_map  # noqa: PLC0415

    return pydantic_to_strawberry_class_map.get(cls) or cast(Any, cls)._strawberry_type


def _gql_type_name(cls: type) -> str:
    return _strawberry_type(cls).__strawberry_definition__.name


def _query_field_type_names(*path: str) -> dict[str, str]:
    """Walk thrs-api's *built* GraphQL schema from ``Query`` along ``path`` and
    return ``{field: named type}`` of the object reached - the exact names
    Strawberry gave a generic specialisation (``...ControlModule``,
    ``...SwitchingControlModeType``), which no class carries by itself."""
    from graphql import get_named_type  # noqa: PLC0415

    from thrs.graphql.strawberry import schema  # noqa: PLC0415

    node = schema._schema.query_type
    for name in path:
        node = get_named_type(cast(Any, node).fields[name].type)
    return {
        name: get_named_type(field.type).name
        for name, field in cast(Any, node).fields.items()
    }


def _gql_model(cls: type) -> type[ThrsValues]:
    """The pydantic model thrs-api's type for ``cls`` was generated from (its
    registered base when ``cls`` itself isn't registered)."""
    return getattr(_strawberry_type(cls), "_pydantic_type", cls)


def _leaf_enum(annotation: Any) -> type[Enum] | None:
    """The Enum a Stamped[Enum] leaf wraps, or None. thrs-api (Strawberry)
    serializes such a leaf as the enum member name (ControlMode.LOCAL ->
    "LOCAL"), while the wire carries the enum value (0); zero-mqtt-graphql
    needs the value->name map to match.

    pydantic materializes Stamped[ControlMode] into a concrete subclass, so
    get_args on it is empty; the wrapped type is the annotation of the
    subclass's own value field instead."""
    inner = _bare_type(annotation)
    if not isinstance(inner, type):
        return None
    value_field = getattr(inner, "model_fields", {}).get("value")
    if value_field is None:
        return None
    enum_cls = _bare_type(value_field.annotation)
    if isinstance(enum_cls, type) and issubclass(enum_cls, Enum):
        return enum_cls
    return None


def _component_cls(annotation: Any) -> type | None:
    inner = _bare_type(annotation)
    if isinstance(inner, type) and issubclass(inner, ThrsValues):
        return inner
    return None


def _leaves(component_cls: type) -> list[LeafSpec]:
    """The {value, timestamp} leaves of a Stamped-leaf component
    (a sensor field, or a controlValues/controllerState sub-object), each
    with its GraphQL name, PascalCase wire key, scalar type, and (for enum
    leaves) the wire-value -> member-name map."""
    leaves: list[LeafSpec] = []
    for leaf_snake, leaf_field in component_cls.model_fields.items():
        leaf_inner = _bare_type(leaf_field.annotation)
        if not (isinstance(leaf_inner, type) and issubclass(leaf_inner, Stamped)):
            continue
        raw = _wire_key(leaf_snake, leaf_field)
        enum_cls = _leaf_enum(leaf_field.annotation)
        # A leaf with a default (`Pump.control_mode = Stamped(value=None,
        # timestamp=epoch)`) is served by thrs-api with that default when the
        # payload lacks it; ship the wire-shaped default so mqtt-graphql does too.
        default = (
            leaf_field.default.model_dump(mode="json", by_alias=True)
            if isinstance(leaf_field.default, Stamped)
            else None
        )
        # `optional`: the leaf's value is nullable in thrs-api's schema
        # (`Stamped[X | None]`, or an optional leaf field); a required
        # scalar input for the matching mutation is non-null otherwise.
        optional = _leaf_value_optional(leaf_field.annotation)
        if enum_cls is not None:
            # Output the member name (thrs-api's shape: a GraphQL enum named
            # after the Python Enum class, e.g. `ControlMode`); ship the
            # wire-value -> name map so mqtt-graphql can translate. Keys are
            # stringified enum values (int `0` on the wire -> key "0").
            leaves.append(
                LeafSpec(
                    gql=to_camel_case(leaf_snake),
                    raw=raw,
                    type="String",
                    enum_type=enum_cls.__name__,
                    enum_values={str(member.value): member.name for member in enum_cls},
                    optional=optional,
                    default=default,
                )
            )
        else:
            leaves.append(
                LeafSpec(
                    gql=to_camel_case(leaf_snake),
                    raw=raw,
                    # Declared type (authoritative, matches Strawberry): a
                    # scalar or `[Float!]` for a tuple leaf.
                    type=_leaf_type_from_annotation(leaf_field.annotation),
                    optional=optional,
                    default=default,
                )
            )
    return leaves


def _actuated_wire_keys(component_cls: type) -> dict[str, str]:
    """Field name -> the by-alias wire key thrs-api reads for that field when
    the payload is an *actuated* (AMCS/device) message. `Pump` and `Valve`
    rename their keys in that context (`Dutypoint` -> `CC_DutyPoint`,
    `Setpoint` -> `CC_Setpoint`, ...; see their `_read_actuated`
    validators); every other component keeps its plain aliases. Derived
    empirically: serialize an instance with the actuated context after giving
    each leaf a distinct timestamp, then pair each emitted key back to its
    field by that timestamp - so it can't drift from the model's own
    serializer, whatever renames it applies."""
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    from thrs.input_output.definitions.wire_context import (  # noqa: PLC0415
        AMCS_RECEIVE_CONTEXT,
    )

    # Build without validation (`model_construct`): a component's own
    # validators may reject zeros (Pump dutypoint < 0.1), and only the
    # serializer's key mapping matters here. Enum leaves get a member (the
    # actuated serializer drops a None value, e.g. Pump.control_mode).
    base = datetime(2000, 1, 1, tzinfo=UTC)
    stamps: dict[str, str] = {}
    values: dict[str, Any] = {}
    for i, (name, fld) in enumerate(component_cls.model_fields.items()):
        inner = _bare_type(fld.annotation)
        if not (isinstance(inner, type) and issubclass(inner, Stamped)):
            continue
        enum_cls = _leaf_enum(fld.annotation)
        value: Any = next(iter(enum_cls)).value if enum_cls is not None else 0.0
        timestamp = base + timedelta(seconds=i + 1)
        values[name] = Stamped.model_construct(value=value, timestamp=timestamp)
        stamps[timestamp.isoformat().replace("+00:00", "Z")] = name
    inst = component_cls.model_construct(**values)
    with warnings.catch_warnings():
        # Unvalidated placeholder values (a float in a bool leaf) trip
        # pydantic's serializer warnings; only the emitted keys matter.
        warnings.simplefilter("ignore")
        data = inst.model_dump(mode="json", by_alias=True, context=AMCS_RECEIVE_CONTEXT)
    keys: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, dict) and (
            name := stamps.get(str(value.get("TimeStamp")))
        ):
            keys[name] = key
    return keys


def _partial_section(
    section_cls: type, devices_prefix: str, module_name: str
) -> ObjectSectionSpec:
    """A read section assembled from one device topic per component - thrs-api's
    `controlValues`, the actuated control values (a partial mapping on the
    devices prefix with the actuated wire context), not the manual-values
    object. Each component is read off its own topic (the same device topic
    the sensor component of that name uses) with the actuated wire keys.
    thrs-api serves the section only once every component's payload
    validates, so a section field lists per leaf whether it is required for
    that."""
    topics = _field_topics(
        section_cls, devices_prefix, device_module_prefix(module_name)
    )
    fields: list[ObjectFieldSpec] = []
    for name, field in section_cls.model_fields.items():
        component_cls = _component_cls(field.annotation)
        topic = topics.get(name)
        if component_cls is None or topic is None:
            continue
        output_cls = _gql_model(component_cls)
        actuated = _actuated_wire_keys(component_cls)
        leaves: list[LeafSpec] = []
        for leaf in _leaves(output_cls):
            leaf_snake = next(
                (n for n in output_cls.model_fields if to_camel_case(n) == leaf.gql),
                None,
            )
            actuated_raw = actuated.get(leaf_snake) if leaf_snake else None
            # Keep the plain alias as `raw` (the shared component type reads
            # that) and carry the actuated key separately: mqtt-graphql reads
            # the device payload through `actuatedRaw` and re-keys it to `raw`.
            if actuated_raw and actuated_raw != leaf.raw:
                leaves.append(leaf.model_copy(update={"actuated_raw": actuated_raw}))
            else:
                leaves.append(leaf)
        if leaves:
            fields.append(
                ObjectFieldSpec(
                    gql_field=to_camel_case(name),
                    key=_wire_key(name, field),
                    topic=topic,
                    type_name=_gql_type_name(output_cls),
                    leaves=leaves,
                )
            )
    fields.sort(key=lambda f: f.gql_field)
    return ObjectSectionSpec(
        topic="", type_name=_gql_type_name(section_cls), fields=fields
    )


def _object_section(section_cls: type, topic: str) -> ObjectSectionSpec:
    """One whole-object read section (controlValues/parameters/
    controllerState). Each is published as a single PascalCase JSON object on
    `topic`; per field we emit its GraphQL name and by-alias wire key, plus
    either a scalar `type` (flat parameters) or Stamped `leaves` (component
    fields). Empty `zero()` gives leaf scalar types without needing live
    data (the object may be absent on MQTT, in which case the whole section
    resolves null - matching thrs-api)."""
    fields: list[ObjectFieldSpec] = []
    for name, field in section_cls.model_fields.items():
        key = _wire_key(name, field)
        component_cls = _component_cls(field.annotation)
        if component_cls is not None:
            output_cls = _gql_model(component_cls)
            leaves = _leaves(output_cls)
            if leaves:
                fields.append(
                    ObjectFieldSpec(
                        gql_field=to_camel_case(name),
                        key=key,
                        type_name=_gql_type_name(output_cls),
                        leaves=leaves,
                    )
                )
        else:
            flat = _flat_graphql_type(field.annotation)
            if flat is not None:
                fields.append(
                    ObjectFieldSpec(
                        gql_field=to_camel_case(name),
                        key=key,
                        type=flat,
                        optional=_is_optional(field.annotation),
                    )
                )
    fields.sort(key=lambda f: f.gql_field)
    return ObjectSectionSpec(
        topic=topic, type_name=_gql_type_name(section_cls), fields=fields
    )


def build_module_view(
    module_name: str,
    devices_prefix: str | None = None,
    controller_prefix: str | None = None,
) -> dict[str, Any]:
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

    # Bake the given prefixes into the emitted topics, so aggregate-specs.sh can
    # target whatever prefix the live broker uses.
    config = _spec_config(devices_prefix, controller_prefix)
    devices_prefix = config.mqtt_devices_topic_prefix
    controller_prefix = config.mqtt_controller_topic_prefix

    modules = all_module_descriptions()
    if module_name not in modules:
        raise ValueError(
            f"unknown THRS module {module_name!r}; known modules: {sorted(modules)}"
        )
    sensor_cls = modules[module_name].sensor_values_cls

    raw_topics = _field_topics(
        sensor_cls, devices_prefix, device_module_prefix(module_name)
    )
    computed_topics = _field_topics(
        sensor_cls, controller_prefix, module_name, computed=True
    )

    def _entry(
        name: str, annotation: Any, topic: str | None, computed: bool
    ) -> ModuleFieldSpec | None:
        component_cls = _component_cls(annotation)
        if component_cls is None or topic is None:
            return None
        output_cls = _gql_model(component_cls)
        leaves = _leaves(output_cls)
        if not leaves:
            return None
        return ModuleFieldSpec(
            gql_field=to_camel_case(name),
            topic=topic,
            type_name=_gql_type_name(output_cls),
            leaves=leaves,
            computed=computed,
        )

    raw_entries = [
        (name, entry)
        for name, field in sensor_cls.model_fields.items()
        if (entry := _entry(name, field.annotation, raw_topics.get(name), False))
    ]

    # Two distinct snake_case model fields can collapse to the same camelCase
    # GraphQL name (`pvt_flow_main_string1_2` and `pvt_flow_main_string12` both
    # -> `pvtFlowMainString12`). Strawberry (thrs-api) silently keeps the field
    # defined *last*, so its schema serves only that one; reproduce that here so
    # the view matches thrs-api. The shadowed earlier field(s) are still real
    # sensors that computed recompute needs as inputs, so keep them in the view
    # under their unambiguous snake name and flag them `inputOnly` - mqtt-graphql
    # reads their topic for recompute but does not register a query field for
    # them (and the parity suite skips them, since thrs-api has no such field).
    from collections import Counter  # noqa: PLC0415

    camel_counts = Counter(e.gql_field for _, e in raw_entries)
    last_index = {e.gql_field: i for i, (_, e) in enumerate(raw_entries)}
    entries: list[ModuleFieldSpec] = []
    for i, (name, entry) in enumerate(raw_entries):
        gql = entry.gql_field
        shadowed = camel_counts[gql] > 1 and i != last_index[gql]
        entries.append(
            entry.model_copy(update={"gql_field": name, "input_only": True})
            if shadowed
            else entry
        )

    entries += [
        entry
        for name, cfield in sensor_cls.model_computed_fields.items()
        if (entry := _entry(name, cfield.return_type, computed_topics.get(name), True))
    ]
    entries.sort(key=lambda e: e.gql_field)

    # The other three read sections the UI queries next to sensorValues
    # (`modules.<mod>.{controlValues,parameters,controllerState}`, see
    # zero-ui thrsim `*_CONTROL_QUERY`/`*_PARAMETERS_QUERY`/`*_CONTROLLER_STATE_QUERY`).
    # parameters/controllerState are each one whole object published on a single
    # controller topic (thrs-api's ControlApiChannels `parameters`/
    # `controller-state` listeners); mqtt-graphql reads that object from the
    # cache and pulls each field out by its by-alias (PascalCase) wire key.
    # Fields are either a plain scalar/collection (parameters) or a Stamped-leaf
    # component (controllerState), same leaf shape as sensorValues. controlValues
    # is per-component off the device topics (see `_partial_section`).
    desc = modules[module_name]
    # thrs-api's names for the `modules` object, this module's object and its
    # sections, read off the built schema (`Query.modules.<module>.*`).
    module_field = to_camel_case(module_name)
    module_types = _query_field_type_names("modules", module_field)
    return ModuleViewSpec(
        module=module_name,
        modules_type_name=_query_field_type_names()["modules"],
        type_name=_query_field_type_names("modules")[module_field],
        sensor_values_type_name=module_types["sensorValues"],
        sensor_values=entries,
        # controlValues is thrs-api's *actuated* control values: per component
        # off its device topic with the actuated (`CC_*`) wire keys - not the
        # manual-values object (which is what the control mutations modify).
        control_values=_partial_section(
            desc.control_values_cls, devices_prefix, module_name
        ),
        parameters=_object_section(
            desc.parameters_cls, f"{controller_prefix}/{module_name}/parameters"
        ),
        controller_state=_object_section(
            desc.controller_state_cls,
            f"{controller_prefix}/{module_name}/controller-state",
        ),
        # The switching control mode (thrs-api `controlMode { automatic
        # automaticMode { ... } }`, zero-ui `CONTROL_QUERY`): one whole
        # `SwitchingControlMode[M]` object on the `control-mode` topic,
        # `{"AutomaticMode": <M> | null}`. `automatic` is derived (`AutomaticMode`
        # is not null); `automaticMode` is the module's plain (unstamped) mode
        # model - flat strings, or nested groups (pvt/dc) - named after its
        # pydantic class + `Type` like Strawberry does (`ThrustersControlModeType`).
        control_mode=ControlModeSpec(
            topic=f"{controller_prefix}/{module_name}/control-mode",
            type_name=module_types["controlMode"],
            key=_wire_key(
                "automatic_mode", SwitchingControlMode.model_fields["automatic_mode"]
            ),
            automatic_mode=_plain_object(desc.control_mode_cls),
        ),
    ).dump()


def _plain_object(cls: type) -> PlainObjectSpec:
    """A plain (non-Stamped) pydantic model as a GraphQL object description:
    thrs-api's Strawberry type name (`<Class>Type`) and, per field, its GraphQL
    name, by-alias wire key, and either a scalar `type` or a nested `object`.
    Used for the control-mode models. A model without fields gets no fields
    (thrs-api renders it with an `Empty: Void` placeholder; mqtt-graphql does
    the same)."""
    fields: list[PlainFieldSpec] = []
    for name, fld in cls.model_fields.items():
        key = _wire_key(name, fld)
        base = _bare_type(fld.annotation)
        if isinstance(base, type) and issubclass(base, ThrsValues):
            fields.append(
                PlainFieldSpec(
                    gql_field=to_camel_case(name),
                    key=key,
                    optional=_is_optional(fld.annotation),
                    object=_plain_object(base),
                )
            )
        else:
            fields.append(
                PlainFieldSpec(
                    gql_field=to_camel_case(name),
                    key=key,
                    optional=_is_optional(fld.annotation),
                    type=_flat_graphql_type(fld.annotation) or "String",
                )
            )
    return PlainObjectSpec(type_name=_gql_type_name(cls), fields=fields)


def _scalar_bounds(fld: Any) -> BoundsSpec | None:
    """The single-field numeric bounds a parameter's unit type carries (Celsius
    is Field(ge=-273.15), Degree ge=0, le=360, ...), so mqtt-graphql can reject
    an out-of-range value the way thrs-api's validate_assignment does. pydantic
    surfaces Field(ge=...) as annotated_types markers in fld.metadata. This
    covers only per-field bounds, not the cross-field invariants some
    parameter models enforce in a model_validator (e.g. thrusters' recovery >
    warmup): those are per-module domain logic, still enforced by the control
    loop that consumes the published object, and are not reproduced here."""
    bounds: dict[str, float] = {}
    for marker in getattr(fld, "metadata", []):
        if isinstance(marker, at.Ge):
            bounds["min"] = marker.ge  # type: ignore[assignment]
        elif isinstance(marker, at.Gt):
            bounds["exclusive_min"] = marker.gt  # type: ignore[assignment]
        elif isinstance(marker, at.Le):
            bounds["max"] = marker.le  # type: ignore[assignment]
        elif isinstance(marker, at.Lt):
            bounds["exclusive_max"] = marker.lt  # type: ignore[assignment]
    return BoundsSpec(**bounds) if bounds else None


def _input_type_name(component_annotation: Any) -> str:
    """thrs-api's name for a component's unstamped mutation input type
    (``PumpInputType``, shared across modules and control/simulation
    mutations); zero-ui hard-codes these as GraphQL variable types."""
    from thrs.graphql.helpers import ensure_input_type  # noqa: PLC0415

    input_type = ensure_input_type(_bare_type(component_annotation), unstamp=True)
    return input_type.__strawberry_definition__.name


def _input_fields(leaves: list[LeafSpec]) -> list[InputFieldSpec]:
    """The unstamped input fields of a component mutation, one per Stamped leaf
    (thrs-api's UnstampedInput.generate_for_model): arg name, wire key, type,
    enum info, and whether the field is required (non-null) - a leaf with an
    optional value or a default is nullable in the input too."""
    return [
        InputFieldSpec(
            arg_name=leaf.gql,
            wire_key=leaf.raw,
            type=leaf.type,
            required=not leaf.optional,
            enum_type=leaf.enum_type,
            enum_values=leaf.enum_values,
        )
        for leaf in leaves
    ]


class _Spec(BaseModel):
    """A spec object as zero-mqtt-graphql reads it: camelCase keys, a None
    field left out. Every JSON key mqtt-graphql's Rust structs deserialize is
    an attribute name here (converted by ``alias_generator``), not a
    hand-typed string, so it can't drift from what's actually emitted."""

    model_config = ConfigDict(alias_generator=to_camel_case, populate_by_name=True)

    def dump(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)


class BoundsSpec(_Spec):
    """Single-field numeric bounds (mirrors mutations_view.rs ``Bounds``)."""

    min: float | None = None
    max: float | None = None
    exclusive_min: float | None = None
    exclusive_max: float | None = None


class LeafSpec(_Spec):
    """One ``{value, timestamp}`` leaf (mirrors modules_view.rs ``ModuleLeafDef``)."""

    gql: str
    raw: str
    type: str
    optional: bool = False
    enum_type: str | None = None
    enum_values: dict[str, str] | None = None
    actuated_raw: str | None = None
    default: dict[str, Any] | None = None


class ObjectFieldSpec(_Spec):
    """One field of a read section: a flat scalar or a Stamped-leaf component
    (mirrors modules_view.rs ``ObjectFieldDef``)."""

    gql_field: str
    key: str
    type: str | None = None
    type_name: str | None = None
    optional: bool = False
    topic: str | None = None
    leaves: list[LeafSpec] = []


class ObjectSectionSpec(_Spec):
    """A whole read section (mirrors modules_view.rs ``ObjectSectionDef``)."""

    topic: str = ""
    type_name: str
    fields: list[ObjectFieldSpec] = []


class ModuleFieldSpec(_Spec):
    """One ``sensorValues`` field (mirrors modules_view.rs ``ModuleFieldDef``)."""

    gql_field: str
    topic: str
    leaves: list[LeafSpec] = []
    type_name: str
    computed: bool = False
    input_only: bool = False


class InputFieldSpec(_Spec):
    """One unstamped input field of a composite mutation (mirrors
    mutations_view.rs ``InputFieldDef``)."""

    arg_name: str
    wire_key: str
    type: str
    required: bool
    enum_type: str | None = None
    enum_values: dict[str, str] | None = None


class PlainFieldSpec(_Spec):
    """One field of a plain (non-Stamped) object (mirrors modules_view.rs
    ``PlainFieldDef``)."""

    gql_field: str
    key: str
    type: str | None = None
    object: PlainObjectSpec | None = None
    optional: bool = False


class PlainObjectSpec(_Spec):
    """A plain pydantic model as a GraphQL object (mirrors modules_view.rs
    ``PlainObjectDef``)."""

    type_name: str
    fields: list[PlainFieldSpec] = []


PlainFieldSpec.model_rebuild()


class ControlModeSpec(_Spec):
    """The switching control-mode section (mirrors modules_view.rs
    ``ControlModeDef``)."""

    topic: str
    type_name: str
    key: str
    automatic_mode: PlainObjectSpec


class MutationSpec(_Spec):
    """One thrs-api mutation and the MQTT read-modify-publish it stands for
    (see ``mutations_view.rs``)."""

    gql_name: str
    kind: Literal["parameter", "automationMode", "control", "simulation"]
    arg_type: str | None = None
    arg_name: str
    payload_key: str
    component_gql_field: str | None = None
    input_type_name: str | None = None
    input_fields: list[InputFieldSpec] | None = None
    true_value: str | None = None
    false_value: str | None = None
    state_topic: str
    set_topic: str
    bounds: BoundsSpec | None = None
    missing_error: str | None = None


class DirectiveSpec(_Spec):
    """One simulation directive mutation (see ``simulation_view.rs``)."""

    gql_name: str
    topic: str
    arg_name: str | None = None
    payload_key: str | None = None
    arg_required: bool | None = None
    default: float | None = None
    bounds: BoundsSpec | None = None
    allowed_from: list[str]
    expect_status: str
    precondition_error: str
    missing_error: str


class ModuleViewSpec(_Spec):
    """A module-view spec file (mirrors modules_view.rs ``ModuleView``)."""

    module: str
    modules_type_name: str
    type_name: str
    sensor_values_type_name: str
    sensor_values: list[ModuleFieldSpec] = []
    control_values: ObjectSectionSpec
    parameters: ObjectSectionSpec
    controller_state: ObjectSectionSpec
    control_mode: ControlModeSpec


class ModuleMutationsSpec(_Spec):
    """A mutations spec file (mirrors mutations_view.rs ``ModuleMutations``)."""

    module: str
    mutations: list[MutationSpec] = []
    parameters_object: ObjectSectionSpec
    control_values_object: ObjectSectionSpec


class StatusKeysSpec(_Spec):
    """By-alias keys read off the simulation status object (mirrors
    simulation_view.rs ``StatusKeys``)."""

    status: str
    time: str


class SimulationDefSpec(_Spec):
    """One simulation's inputs/outputs/mutations (mirrors simulation_view.rs
    ``SimulationDef``)."""

    name: str
    inputs: ObjectSectionSpec
    outputs: ObjectSectionSpec
    mutations: list[MutationSpec] = []


class SimulationViewSpec(_Spec):
    """The simulation spec file (mirrors simulation_view.rs ``SimulationView``)."""

    state_type_name: str
    status_topic: str
    status_keys: StatusKeysSpec
    inputs_topic: str
    outputs_topic: str
    inputs_set_topic: str
    inputs_union_type: str
    outputs_union_type: str
    directives: list[DirectiveSpec] = []
    wait_timeout_s: float
    simulations: list[SimulationDefSpec] = []


def _thrs_api_mutation(python_name: str) -> Any:
    """thrs-api's registered Strawberry field for one of its mutations."""
    from thrs.graphql.strawberry import Mutation  # noqa: PLC0415

    for field in cast(Any, Mutation).__strawberry_definition__.fields:
        if field.python_name == python_name:
            return field
    raise RuntimeError(f"thrs-api has no mutation {python_name!r}")


def _gql_name(field_or_argument: Any) -> str:
    """The name thrs-api's schema gives a field or argument."""
    from thrs.graphql.strawberry import schema  # noqa: PLC0415

    return schema.config.name_converter.get_graphql_name(field_or_argument)


def _single_argument(field: Any) -> Any:
    if len(field.arguments) != 1:
        raise RuntimeError(
            f"mutation {field.python_name!r} has {len(field.arguments)} arguments"
        )
    return field.arguments[0]


def build_module_mutations(
    module_name: str,
    controller_prefix: str | None = None,
) -> dict[str, Any]:
    """The write-path contract zero-mqtt-graphql needs to serve thrs-api's
    mutations 1:1. Per module it lists every mutation thrs-api exposes for it,
    each with the GraphQL name Strawberry exposes, its argument, the by-alias
    payload key to write, and the state/set MQTT topics:

    * ``parameter`` (add_parameter_mutations -> ControlMessaging.set_parameter ->
      ControlApiChannels.send_parameters): reads the current parameters from
      {controller_prefix}/{module}/parameters, overwrites one field (a scalar or
      a PID tuning tuple, ``[Float!]``) and republishes the whole object to
      .../parameters/set. Single-field bounds travel along (``bounds``).
    * ``automationMode`` (set_automation_mode): publishes a fresh
      ``AutomationMode`` object to .../automation-mode/set.
    * ``control`` (set_manual_control): restamps an unstamped component input
      into the manual-values object and republishes it to .../manual-values/set.

    The parameters / control-values objects the mutations return are the same
    types the read sections serve, so they are emitted alongside."""
    from thrs.graphql.base import (  # noqa: PLC0415
        AUTOMATION_MODE_MUTATION_NAME,
        CONTROL_MUTATION_NAME,
        PARAMETER_MUTATION_NAME,
    )
    from thrs.graphql.messaging import (  # noqa: PLC0415
        NO_CONTROL_VALUES_ERROR,
        NO_PARAMETERS_ERROR,
    )

    modules = all_module_descriptions()
    if module_name not in modules:
        raise ValueError(
            f"unknown THRS module {module_name!r}; known modules: {sorted(modules)}"
        )
    params_cls = modules[module_name].parameters_cls

    config = _spec_config(controller_prefix=controller_prefix)
    prefix = config.mqtt_controller_topic_prefix
    suffix = config.mqtt_controller_topic_suffix

    def _topics(kind: str) -> tuple[str, str]:
        """(state topic, set topic) of one controller object of this module."""
        state = f"{prefix}/{module_name}/{kind}"
        return state, f"{state}/{suffix}" if suffix else state

    state_topic, set_topic = _topics("parameters")

    mutations: list[MutationSpec] = []
    for name, fld in params_cls.model_fields.items():
        # Strawberry's arg scalar: float -> Float, int -> Int, bool -> Boolean,
        # a PID tuple[float, float, float] -> [Float!] (a non-null list arg).
        arg_type = _flat_graphql_type(fld.annotation)
        if arg_type is None:
            continue
        field = _thrs_api_mutation(
            PARAMETER_MUTATION_NAME.format(module=module_name, field=name)
        )
        mutations.append(
            MutationSpec(
                gql_name=_gql_name(field),
                kind="parameter",
                arg_type=arg_type,
                arg_name=_gql_name(_single_argument(field)),
                payload_key=_wire_key(name, fld),
                state_topic=state_topic,
                set_topic=set_topic,
                bounds=_scalar_bounds(fld),
                missing_error=NO_PARAMETERS_ERROR,
            )
        )

    # Automation-mode mutation (thrs-api's set_automation_mode): publishes a
    # whole AutomationMode object - {"Mode": "automatic"|"manual"} - to
    # {controller}/{module}/automation-mode/set. Returns Boolean like thrs-api.
    # The automatic Boolean arg maps to the mode string, so the resolver needs
    # the two literal values here.
    am_state, am_set = _topics("automation-mode")
    am_field = _thrs_api_mutation(
        AUTOMATION_MODE_MUTATION_NAME.format(module=module_name)
    )
    am_argument = _single_argument(am_field)
    mutations.append(
        MutationSpec(
            gql_name=_gql_name(am_field),
            kind="automationMode",
            arg_type=_flat_graphql_type(am_argument.type),
            arg_name=_gql_name(am_argument),
            payload_key=_wire_key("mode", AutomationMode.model_fields["mode"]),
            true_value=AutomationMode.for_automatic(True).mode,
            false_value=AutomationMode.for_automatic(False).mode,
            state_topic=am_state,
            set_topic=am_set,
        )
    )

    # Control-value (manual-values) mutations: each control component
    # (a Pump/Valve/...) is set by an unstamped input - one arg per stamped
    # leaf (dutypoint, on, controlMode, setpoint, ...) - which the server
    # restamps with now() and writes as {WireKey: {Value, TimeStamp}} into the
    # whole manual-values object, republished to .../manual-values/set. The
    # component's key + leaves (incl. enum value->name maps) come from the same
    # section builder the module view uses, so the two can't drift.
    control_values_cls = modules[module_name].control_values_cls
    # The manual-values object (plain aliases; what set_manual_control reads,
    # modifies, republishes and returns) - distinct from the actuated
    # controlValues read section, though both are the same GraphQL type.
    cv_state, cv_set = _topics("manual-values")
    manual_values = _object_section(control_values_cls, cv_state)
    cv_by_gql = {f.gql_field: f for f in manual_values.fields}
    for name, cfield in control_values_cls.model_fields.items():
        vf = cv_by_gql.get(to_camel_case(name))
        if vf is None or not vf.leaves:
            continue
        field = _thrs_api_mutation(
            CONTROL_MUTATION_NAME.format(module=module_name, field=name)
        )
        mutations.append(
            MutationSpec(
                gql_name=_gql_name(field),
                kind="control",
                arg_name=_gql_name(_single_argument(field)),
                payload_key=vf.key,
                component_gql_field=vf.gql_field,
                input_type_name=_input_type_name(cfield.annotation),
                input_fields=_input_fields(_leaves(_bare_type(cfield.annotation))),
                state_topic=cv_state,
                set_topic=cv_set,
                missing_error=NO_CONTROL_VALUES_ERROR,
            )
        )

    mutations.sort(key=lambda m: m.gql_name)

    # The parameters object each `parameter` mutation returns (thrs-api returns
    # the whole `Parameters` model - the *same* GraphQL type the read section
    # serves, `ThrustersParametersType`), and likewise the ControlValues object a
    # `control` mutation returns. Both are the module-view section builder's
    # output (same type name + fields), so mqtt-graphql registers one type for
    # read and write.
    return ModuleMutationsSpec(
        module=module_name,
        mutations=mutations,
        parameters_object=_object_section(params_cls, state_topic),
        control_values_object=manual_values,
    ).dump()


def build_simulation_view(simulator_prefix: str | None = None) -> dict[str, Any]:
    """The simulation contract zero-mqtt-graphql needs to serve thrs-api's
    simulation query (status, time, inputs, outputs), the play/pause/step
    directives, and the per-simulation input mutations 1:1.

    Mirrors thrs-api's simulation and directive channels/messaging: everything
    is an MQTT relay on the simulator prefix. status is the retained
    simulation status message; inputs/outputs are one whole object each whose
    concrete type is whichever simulation's model validates it (a pydantic
    union - resolved here by matching the object's keys against each
    simulation's field keys); a directive publishes its message and waits up
    to waitTimeoutS for the status to change; an input mutation restamps an
    unstamped component into the cached inputs object and republishes it to
    the inputs set topic."""
    from thrs.graphql.base import (  # noqa: PLC0415
        SIMULATION_DIRECTIVE_MUTATION_NAME,
        SIMULATION_DIRECTIVE_RESOLVERS,
        SIMULATION_INPUT_MUTATION_NAME,
    )
    from thrs.graphql.messaging import (  # noqa: PLC0415
        NO_SIMULATION_INPUTS_ERROR,
        WAIT_TIMEOUT,
        SimulationDirective,
    )
    from thrs.graphql.simulation import (  # noqa: PLC0415
        SimulationInputsType,
        SimulationOutputsType,
        io_mapping,
    )
    from thrs.graphql.strawberry import SimulationState  # noqa: PLC0415
    from thrs.runtime.messages import SimulationStatusMessage  # noqa: PLC0415

    config = _spec_config(simulator_prefix=simulator_prefix)
    prefix = config.mqtt_simulator_topic_prefix
    suffix = config.mqtt_simulator_topic_suffix
    inputs_topic = f"{prefix}/{SIMULATION_INPUTS_TOPIC}"

    simulations: list[SimulationDefSpec] = []
    for mode, (inputs_cls, outputs_cls) in io_mapping.items():
        inputs = _object_section(inputs_cls, "")
        by_gql = {f.gql_field: f for f in inputs.fields}
        mutations: list[MutationSpec] = []
        for name, fld in inputs_cls.model_fields.items():
            vf = by_gql.get(to_camel_case(name))
            if vf is None or not vf.leaves:
                continue
            field = _thrs_api_mutation(
                SIMULATION_INPUT_MUTATION_NAME.format(mode=mode, field=name)
            )
            mutations.append(
                MutationSpec(
                    gql_name=_gql_name(field),
                    kind="simulation",
                    arg_name=_gql_name(_single_argument(field)),
                    payload_key=vf.key,
                    component_gql_field=vf.gql_field,
                    input_type_name=_input_type_name(fld.annotation),
                    input_fields=_input_fields(_leaves(_bare_type(fld.annotation))),
                    state_topic=inputs_topic,
                    set_topic=f"{inputs_topic}/{suffix}" if suffix else inputs_topic,
                    missing_error=NO_SIMULATION_INPUTS_ERROR,
                )
            )
        simulations.append(
            SimulationDefSpec(
                name=to_camel_case(mode),
                inputs=inputs,
                outputs=_object_section(outputs_cls, ""),
                mutations=mutations,
            )
        )

    def _directive(directive: SimulationDirective) -> DirectiveSpec:
        message = directive.message
        field = _thrs_api_mutation(
            SIMULATION_DIRECTIVE_MUTATION_NAME.format(
                directive=message.subscribe_topic()
            )
        )
        argument = _single_argument(field) if field.arguments else None
        # thrs-api's argument is the message's single field:
        # simulation_play(playback_rate=1.0) publishes PlayMessage.playback_rate.
        by_argument: dict[str, Any] = {}
        if argument is not None:
            fld = message.model_fields[argument.python_name]
            by_argument = {
                "arg_name": _gql_name(argument),
                "payload_key": _wire_key(argument.python_name, fld),
                "arg_required": argument.default is UNSET,
                "default": None if argument.default is UNSET else argument.default,
                "bounds": _scalar_bounds(fld),
            }
        return DirectiveSpec(
            gql_name=_gql_name(field),
            topic=f"{prefix}/{message.subscribe_topic()}",
            **by_argument,
            allowed_from=list(directive.allowed_from),
            expect_status=directive.expect_status,
            precondition_error=directive.precondition_error,
            missing_error=directive.missing_error,
        )

    status_fields = SimulationStatusMessage.model_fields
    return SimulationViewSpec(
        state_type_name=cast(Any, SimulationState).__strawberry_definition__.name,
        status_topic=f"{prefix}/{SimulationStatusMessage.subscribe_topic()}",
        status_keys=StatusKeysSpec(
            status=_wire_key("status", status_fields["status"]),
            time=_wire_key("simulation_time", status_fields["simulation_time"]),
        ),
        inputs_topic=inputs_topic,
        outputs_topic=f"{prefix}/{SIMULATION_OUTPUTS_TOPIC}",
        inputs_set_topic=f"{inputs_topic}/{suffix}" if suffix else inputs_topic,
        inputs_union_type=SimulationInputsType.graphql_name,
        outputs_union_type=SimulationOutputsType.graphql_name,
        directives=[_directive(d) for d in SIMULATION_DIRECTIVE_RESOLVERS],
        wait_timeout_s=WAIT_TIMEOUT,
        simulations=simulations,
    ).dump()


def modules_with_computed_fields() -> list[str]:
    """THRS modules whose sensor-values model has a ``computed_field``, i.e.
    those with a ``kind="controller"`` metadata group. The rest (currently pcm,
    consumers, adsorption, drives, dc) have nothing to enumerate for that kind."""
    return sorted(
        name
        for name, description in all_module_descriptions().items()
        if description.sensor_values_cls.model_computed_fields
    )
