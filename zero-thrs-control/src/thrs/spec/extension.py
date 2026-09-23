"""The ``x-mqtt-graphql`` extension of the THRS document: the GraphQL side
of the contract, so zero-mqtt-graphql serves the same schema the API does.

The extension names only what the document's schemas cannot say - the query
fields and sections, which operation feeds which field, the GraphQL type
names, the mutations and how they are confirmed. Every field name, wire key,
scalar type, nullability, bound, enum member and default is read by the bridge
from the schemas the ``types`` pair each GraphQL type with. See
``zero-mqtt-graphql/README.md`` for the format.

Names follow ``thrs.spec.naming``, behaviour ``thrs.spec.contract``; the
models themselves come from the module descriptions, so a new field, module
or simulation is in the contract as soon as it exists.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Literal, Union, get_args, get_origin

from pydantic.fields import ComputedFieldInfo, FieldInfo

from thrs.control.switching import AutomationMode, SwitchingControlMode
from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions import (
    control,
    controllers,
    sensor,
    simulation,
    system,
)
from thrs.orchestration.comms import (
    SIMULATION_INPUTS_TOPIC,
    SIMULATION_OUTPUTS_TOPIC,
    device_module_prefix,
)
from thrs.orchestration.config import Config
from thrs.runtime.messages import SimulationStatusMessage
from thrs.spec import contract
from thrs.spec.asyncapi import (
    DEFAULT_CONFIG,
    Document,
    all_module_descriptions,
    build_document,
    field_topics,
    operation_key,
    simulation_io_classes,
    wire_key,
)
from thrs.spec.naming import (
    control_module_type_name,
    field_name,
    input_type_name,
    registered_model,
    switching_control_mode_type_name,
    type_name,
)
from thrs.spec.validators import validation_error_url

EXTENSION_KEY = "x-mqtt-graphql"
EXTENSION_VERSION = 2


def shared_definitions() -> tuple[type[ThrsValues], ...]:
    """Every shared component definition the API has a type for: the classes
    the definitions modules export. Their schemas are part of the document so
    a declared type can be served from them."""
    return tuple(
        getattr(module, name)
        for module in (sensor, control, controllers, simulation, system)
        for name in module.__all__
    )


def build_thrs_spec(
    config: Config = DEFAULT_CONFIG,
    *,
    title: str = "THRS Control",
    version: str = "1.0.0",
) -> dict[str, Any]:
    """The complete THRS contract: the channel document with the
    ``x-mqtt-graphql`` extension at its root."""
    document = build_document(
        config,
        title=title,
        version=version,
        extra_schema_classes=shared_definitions(),
    )
    return {**document.data, EXTENSION_KEY: build_extension(document)}


def build_extension(document: Document) -> dict[str, Any]:
    """The extension for ``document``: the ``modules`` view, the instances of
    every module's ``{field}`` channel, and the simulation lifecycle."""
    types = _Types(document)
    views = [_modules_view(document, types)]
    lifecycles = [_simulation_lifecycle(document, types)]
    metadata = [
        _instances(document, name, kind)
        for name, description in sorted(all_module_descriptions().items())
        for kind in ("sensors", "controller")
        if kind == "sensors" or description.sensor_values_cls.model_computed_fields
    ]
    return {
        "version": EXTENSION_VERSION,
        "validationErrorUrl": validation_error_url(),
        "types": types.declared(),
        "views": views,
        "metadata": metadata,
        "lifecycles": lifecycles,
    }


# --- Types -------------------------------------------------------------------


@dataclass
class _Types:
    """The GraphQL object types the extension declares, each paired with the
    schema it is served from. A component is served as the type of its
    registered model (``PropulsionDrive`` as ``SimulationHeatSourceType``);
    where that differs from the component's own schema the field names the
    type explicitly."""

    document: Document
    _declared: dict[str, str] = field(default_factory=dict)

    def declare(self, cls: type[ThrsValues], schema_ref: str | None = None) -> str:
        """Declare the type of ``cls`` and return its name. ``schema_ref`` is
        the schema of ``cls`` itself, for a class the document only holds
        nested in another one."""
        model = registered_model(cls)
        name = type_name(cls)
        ref = (
            schema_ref
            if model is cls and schema_ref is not None
            else self.document.schema_ref(model)
        )
        if self._declared.setdefault(name, ref) != ref:
            raise RuntimeError(f"type {name!r} would be served from two schemas")
        return name

    def declare_nested(self, cls: type[ThrsValues], schema_ref: str) -> None:
        """Declare the type of a plain object and of every object it nests,
        following the document's own schema references."""
        self.declare(cls, schema_ref)
        for name, fld in cls.model_fields.items():
            nested = _component_cls(fld.annotation)
            if nested is not None:
                self.declare_nested(
                    nested, self.document.property_ref(schema_ref, wire_key(name, fld))
                )

    def field_type_override(
        self, cls: type[ThrsValues], schema_ref: str, found_from: str | None
    ) -> dict[str, str]:
        """``{"typeName": ...}`` when the bridge cannot find the component's
        type from the schema it reads it through (``found_from``: a property's
        schema, or the one payload of a topic - None when the topic carries
        several): the type is its base's, or the schema is ambiguous."""
        name = self.declare(cls, schema_ref)
        if registered_model(cls) is cls and found_from == schema_ref:
            return {}
        return {"typeName": name}

    def declared(self) -> dict[str, dict[str, Any]]:
        return {
            name: {"schema": {"$ref": ref}}
            for name, ref in sorted(self._declared.items())
        }


def _component_cls(annotation: Any) -> type[ThrsValues] | None:
    inner = _bare_type(annotation)
    if isinstance(inner, type) and issubclass(inner, ThrsValues):
        return inner
    return None


def component_class(annotation: Any) -> type[ThrsValues]:
    """The component model a field annotation holds (optional or annotated
    wrappers stripped); an error for a field that is no component."""
    component = _component_cls(annotation)
    if component is None:
        raise TypeError(f"{annotation!r} is not a component model")
    return component


def _bare_type(annotation: Any) -> Any:
    """Peel ``X | None`` and ``Annotated[X, ...]`` wrappers, in any nesting
    order, down to the bare type."""
    base = annotation
    while True:
        stripped = base
        if get_origin(stripped) in (UnionType, Union):
            args = [a for a in get_args(stripped) if a is not NoneType]
            stripped = args[0] if len(args) == 1 else stripped
        if getattr(stripped, "__metadata__", None) is not None:  # Annotated[T, ...]
            stripped = stripped.__args__[0]
        if stripped is base:
            return base
        base = stripped


# --- The `modules` view ------------------------------------------------------


def _modules_view(document: Document, types: _Types) -> dict[str, Any]:
    return {
        "gql": contract.MODULES_QUERY_FIELD,
        "typeName": contract.MODULES_TYPE_NAME,
        "members": [
            _member(document, types, name) for name in sorted(all_module_descriptions())
        ],
    }


def _member(document: Document, types: _Types, module_name: str) -> dict[str, Any]:
    """One module: its read sections and its mutations."""
    description = all_module_descriptions()[module_name]
    config = document.config

    def controller(kind: str) -> dict[str, Any]:
        return document.operation_ref(
            f"{config.mqtt_controller_topic_prefix}/{module_name}/{kind}", "send"
        )

    sections = [
        _sensor_values_section(document, types, module_name),
        _control_values_section(document, types, module_name),
        _object_section(
            document,
            types,
            contract.PARAMETERS_SECTION,
            description.parameters_cls,
            controller("parameters"),
        ),
        _object_section(
            document,
            types,
            contract.CONTROLLER_STATE_SECTION,
            description.controller_state_cls,
            controller("controller-state"),
        ),
        _control_mode_section(document, types, module_name),
    ]
    return {
        "gql": field_name(module_name),
        "typeName": control_module_type_name(
            description.sensor_values_cls,
            description.control_values_cls,
            description.parameters_cls,
            description.control_mode_cls,
            description.controller_state_cls,
        ),
        "sections": sections,
        "mutations": _member_mutations(document, types, module_name),
    }


def _sensor_values_section(
    document: Document, types: _Types, module_name: str
) -> dict[str, Any]:
    """``sensorValues``: one field per sensor component, raw fields off the
    devices prefix and computed ones off the controller prefix."""
    config = document.config
    description = all_module_descriptions()[module_name]
    sensor_cls = description.sensor_values_cls
    raw_topics = field_topics(
        sensor_cls, config.mqtt_devices_topic_prefix, device_module_prefix(module_name)
    )
    computed_topics = field_topics(
        sensor_cls, config.mqtt_controller_topic_prefix, module_name, computed=True
    )

    def entry(
        name: str, annotation: Any, topic: str | None, computed: bool
    ) -> dict[str, Any] | None:
        component_cls = _component_cls(annotation)
        if component_cls is None or topic is None:
            return None
        if not _stamped_leaves(registered_model(component_cls)):
            return None
        component_ref = document.schema_ref(component_cls)
        return {
            "gql": field_name(name),
            "operation": document.operation_ref(topic, "send"),
            **types.field_type_override(
                component_cls, component_ref, document.payload_ref(topic, "send")
            ),
            "computed": computed,
        }

    all_entries = [
        (name, e)
        for name, fld in sensor_cls.model_fields.items()
        if (e := entry(name, fld.annotation, raw_topics.get(name), False))
    ] + [
        (name, e)
        for name, cfield in sensor_cls.model_computed_fields.items()
        if (e := entry(name, cfield.return_type, computed_topics.get(name), True))
    ]
    # Two snake_case fields can collapse to one camelCase name
    # (`pvt_flow_main_string1_2` / `pvt_flow_main_string12`); the API keeps the
    # one defined last, so only that one is a field. Dedup across raw and
    # computed fields together — a computed field can collide with a raw one.
    last_index = {e["gql"]: i for i, (_, e) in enumerate(all_entries)}
    entries = [e for i, (_, e) in enumerate(all_entries) if i == last_index[e["gql"]]]
    entries.sort(key=lambda e: e["gql"])
    return {
        "kind": "stampedFields",
        "gql": field_name(contract.SENSOR_VALUES_SECTION),
        "typeName": type_name(sensor_cls),
        "fields": entries,
    }


def _control_values_section(
    document: Document, types: _Types, module_name: str
) -> dict[str, Any]:
    """``controlValues``: the API's *actuated* control values, each component
    read off its own device topic with the device's (``CC_*``) wire keys."""
    config = document.config
    description = all_module_descriptions()[module_name]
    section_cls = description.control_values_cls
    section_ref = document.schema_ref(section_cls)
    topics = field_topics(
        section_cls, config.mqtt_devices_topic_prefix, device_module_prefix(module_name)
    )
    fields: list[dict[str, Any]] = []
    for name, fld in section_cls.model_fields.items():
        component_cls = _component_cls(fld.annotation)
        if component_cls is None:
            continue
        key = wire_key(name, fld)
        component_ref = document.property_ref(section_ref, key)
        spec: dict[str, Any] = {
            "key": key,
            "operation": document.operation_ref(topics[name], "send"),
            **types.field_type_override(
                component_cls, component_ref, document.payload_ref(topics[name], "send")
            ),
        }
        actuated_keys = _actuated_wire_keys(component_cls)
        wire_keys = {
            wire_key(leaf, leaf_fld): actuated
            for leaf, leaf_fld in component_cls.model_fields.items()
            if (actuated := actuated_keys.get(leaf))
            and actuated != wire_key(leaf, leaf_fld)
        }
        if wire_keys:
            spec["wireKeys"] = wire_keys
        fields.append(spec)
    return {
        "kind": "object",
        "gql": field_name(contract.CONTROL_VALUES_SECTION),
        "typeName": types.declare(section_cls),
        "fields": fields,
    }


def _object_section(
    document: Document,
    types: _Types,
    section: str,
    section_cls: type[ThrsValues],
    operation: dict[str, Any] | None,
) -> dict[str, Any]:
    """A whole-object section (one topic carrying the object), or the shape
    of a relayed object when ``operation`` is None. Every nested component's
    type is declared; a component served as its base's type says so."""
    section_ref = document.schema_ref(section_cls)
    fields: list[dict[str, Any]] = []
    for name, fld in section_cls.model_fields.items():
        component_cls = _component_cls(fld.annotation)
        if component_cls is None:
            continue
        key = wire_key(name, fld)
        component_ref = document.property_ref(section_ref, key)
        override = types.field_type_override(
            component_cls, component_ref, component_ref
        )
        if override:
            fields.append({"key": key, **override})
    spec: dict[str, Any] = {
        "kind": "object",
        "gql": field_name(section),
        "typeName": types.declare(section_cls),
    }
    if operation is not None:
        spec["operation"] = operation
    if fields:
        spec["fields"] = fields
    return spec


def _control_mode_section(
    document: Document, types: _Types, module_name: str
) -> dict[str, Any]:
    """``controlMode``: the switching control mode object on the
    ``control-mode`` topic, ``{"AutomaticMode": <mode> | null}``, exposed as
    ``automatic`` (the mode is not null) plus ``automaticMode`` (the module's
    plain mode model)."""
    config = document.config
    description = all_module_descriptions()[module_name]
    mode_cls = description.control_mode_cls
    switching_cls = SwitchingControlMode[mode_cls]  # type: ignore[misc]
    switching_ref = document.schema_ref(switching_cls)
    automatic_key = wire_key(
        contract.AUTOMATIC_MODE_FIELD,
        SwitchingControlMode.model_fields[contract.AUTOMATIC_MODE_FIELD],
    )
    types.declare_nested(mode_cls, document.property_ref(switching_ref, automatic_key))
    return {
        "kind": "switch",
        "gql": field_name(contract.CONTROL_MODE_SECTION),
        "typeName": switching_control_mode_type_name(
            description.sensor_values_cls,
            description.control_values_cls,
            description.parameters_cls,
            description.control_mode_cls,
            description.controller_state_cls,
        ),
        "operation": document.operation_ref(
            f"{config.mqtt_controller_topic_prefix}/{module_name}/control-mode", "send"
        ),
        "key": automatic_key,
        "flagField": field_name(contract.AUTOMATIC_FLAG_FIELD),
        "objectField": field_name(contract.AUTOMATIC_MODE_FIELD),
        "objectTypeName": type_name(mode_cls),
    }


def _stamped_leaves(component_cls: type[ThrsValues]) -> list[str]:
    """The names of a component's ``Stamped`` fields."""
    return [
        name
        for name, fld in component_cls.model_fields.items()
        if (inner := _bare_type(fld.annotation)) is not None
        and isinstance(inner, type)
        and issubclass(inner, Stamped)
    ]


def _actuated_wire_keys(component_cls: type[ThrsValues]) -> dict[str, str]:
    """Field name -> the wire key of that field in an *actuated* (AMCS)
    payload, where ``Pump``/``Valve`` rename their keys (``Dutypoint`` ->
    ``CC_DutyPoint``). Read off the model's own serializer by giving each
    leaf a distinct timestamp and pairing the emitted keys back by it."""
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
    for i, name in enumerate(_stamped_leaves(component_cls)):
        fld = component_cls.model_fields[name]
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


def _leaf_enum(annotation: Any) -> type[Enum] | None:
    """The Enum a Stamped[Enum] leaf wraps, or None."""
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


# --- Mutations -----------------------------------------------------------------


def _member_mutations(
    document: Document, types: _Types, module_name: str
) -> list[dict[str, Any]]:
    """Every mutation of one module:

    * ``setField`` per parameter: overwrite it in the parameters object and
      republish that to the set topic; returns the ``parameters`` section.
    * ``setFlag``: publish a fresh ``AutomationMode`` object; returns Boolean.
    * ``setComponent`` per control component: restamp an unstamped input into
      the manual-values object and republish it; returns ``controlValues``."""
    description = all_module_descriptions()[module_name]
    config = document.config
    prefix = config.mqtt_controller_topic_prefix
    suffix = config.mqtt_controller_topic_suffix

    def state_of(kind: str) -> dict[str, Any]:
        """The controller's `send` operation of one of its objects."""
        return document.operation_ref(f"{prefix}/{module_name}/{kind}", "send")

    def target_of(kind: str) -> dict[str, Any]:
        """The controller's `receive` operation of one of its objects: the set
        topic."""
        state = f"{prefix}/{module_name}/{kind}"
        return document.operation_ref(
            f"{state}/{suffix}" if suffix else state, "receive"
        )

    mutations: list[dict[str, Any]] = []

    params_state, params_target = state_of("parameters"), target_of("parameters")
    for name, fld in description.parameters_cls.model_fields.items():
        mutations.append(
            {
                "gql": field_name(
                    contract.PARAMETER_MUTATION_NAME.format(
                        module=module_name, field=name
                    )
                ),
                "kind": "setField",
                "argName": field_name(contract.VALUE_ARGUMENT),
                "key": wire_key(name, fld),
                "state": params_state,
                "target": params_target,
                "returns": field_name(contract.PARAMETERS_SECTION),
                "missingError": contract.NO_PARAMETERS_ERROR,
                "confirm": _confirm(contract.PARAMETERS_TIMEOUT_ERROR),
            }
        )

    automation_target = target_of("automation-mode")
    control_mode_state = state_of("control-mode")
    mutations.append(
        {
            "gql": field_name(
                contract.AUTOMATION_MODE_MUTATION_NAME.format(module=module_name)
            ),
            "kind": "setFlag",
            "argName": field_name(contract.AUTOMATIC_ARGUMENT),
            "key": wire_key("mode", AutomationMode.model_fields["mode"]),
            "trueValue": AutomationMode.for_automatic(True).mode,
            "falseValue": AutomationMode.for_automatic(False).mode,
            "target": automation_target,
            "confirm": {
                "operation": control_mode_state,
                "key": wire_key(
                    contract.AUTOMATIC_MODE_FIELD,
                    SwitchingControlMode.model_fields[contract.AUTOMATIC_MODE_FIELD],
                ),
                "presence": True,
                **_confirm(contract.AUTOMATION_MODE_TIMEOUT_ERROR),
            },
        }
    )

    cv_state, cv_target = state_of("manual-values"), target_of("manual-values")
    mutations += _component_mutations(
        description.control_values_cls,
        lambda name: contract.CONTROL_MUTATION_NAME.format(
            module=module_name, field=name
        ),
        state=cv_state,
        target=cv_target,
        returns=contract.CONTROL_VALUES_SECTION,
        missing_error=contract.NO_CONTROL_VALUES_ERROR,
        timeout_error=contract.CONTROL_VALUES_TIMEOUT_ERROR,
    )
    mutations.sort(key=lambda m: m["gql"])
    return mutations


def _component_mutations(
    object_cls: type[ThrsValues],
    python_name: Any,
    *,
    state: dict[str, Any],
    target: dict[str, Any],
    returns: str,
    missing_error: str,
    timeout_error: str,
) -> list[dict[str, Any]]:
    """One ``setComponent`` mutation per stamped component of a whole object."""
    return [
        {
            "gql": field_name(python_name(name)),
            "kind": "setComponent",
            "argName": field_name(contract.VALUE_ARGUMENT),
            "key": wire_key(name, fld),
            "inputTypeName": input_type_name(component_cls),
            "state": state,
            "target": target,
            "returns": field_name(returns),
            "missingError": missing_error,
            "confirm": _confirm(timeout_error),
        }
        for name, fld in object_cls.model_fields.items()
        if (component_cls := _component_cls(fld.annotation)) is not None
        and _stamped_leaves(component_cls)
    ]


def _confirm(timeout_error: str) -> dict[str, Any]:
    return {"timeoutS": contract.WAIT_TIMEOUT, "timeoutError": timeout_error}


# --- The simulation lifecycle ---------------------------------------------------


def _simulation_lifecycle(document: Document, types: _Types) -> dict[str, Any]:
    """The simulation: the retained status object, the inputs and outputs
    relays (a union over every simulation's model, resolved by field keys),
    the play/pause/step directives and the per-simulation input mutations."""
    config = document.config
    prefix = config.mqtt_simulator_topic_prefix
    suffix = config.mqtt_simulator_topic_suffix
    inputs_topic = f"{prefix}/{SIMULATION_INPUTS_TOPIC}"
    inputs_state = document.operation_ref(inputs_topic, "send")
    inputs_target = document.operation_ref(
        f"{inputs_topic}/{suffix}" if suffix else inputs_topic, "receive"
    )

    members = []
    for mode, (inputs_cls, outputs_cls) in simulation_io_classes().items():
        members.append(
            {
                "name": field_name(mode),
                "sections": [
                    _object_section(
                        document, types, contract.INPUTS_SECTION, inputs_cls, None
                    ),
                    _object_section(
                        document, types, contract.OUTPUTS_SECTION, outputs_cls, None
                    ),
                ],
                "mutations": _component_mutations(
                    inputs_cls,
                    lambda name, mode=mode: (
                        contract.SIMULATION_INPUT_MUTATION_NAME.format(
                            mode=mode, field=name
                        )
                    ),
                    state=inputs_state,
                    target=inputs_target,
                    returns=contract.INPUTS_SECTION,
                    missing_error=contract.NO_SIMULATION_INPUTS_ERROR,
                    timeout_error=contract.SIMULATION_INPUTS_TIMEOUT_ERROR,
                ),
            }
        )

    def directive(spec: contract.SimulationDirective) -> dict[str, Any]:
        message = spec.message
        entry: dict[str, Any] = {
            "gql": field_name(
                contract.SIMULATION_DIRECTIVE_MUTATION_NAME.format(
                    directive=message.subscribe_topic()
                )
            ),
            "target": document.operation_ref(
                f"{prefix}/{message.subscribe_topic()}", "receive"
            ),
        }
        # The argument is the message's single field, when it has one.
        arguments = list(message.model_fields.items())
        if len(arguments) > 1:
            raise RuntimeError(f"{message.__name__} has more than one field")
        if arguments:
            ((name, fld),) = arguments
            entry["key"] = wire_key(name, fld)
        entry.update(
            {
                "allowedFrom": list(spec.allowed_from),
                "expectStatus": spec.expect_status,
                "preconditionError": spec.precondition_error,
                "missingError": spec.missing_error,
            }
        )
        return entry

    status_fields = SimulationStatusMessage.model_fields
    return {
        "gql": contract.SIMULATION_QUERY_FIELD,
        "stateTypeName": contract.SIMULATION_STATE_TYPE_NAME,
        "status": {
            "operation": document.operation_ref(
                f"{prefix}/{SimulationStatusMessage.subscribe_topic()}", "send"
            ),
            "key": wire_key("status", status_fields["status"]),
            "fields": [
                {"key": wire_key("status", status_fields["status"])},
                {
                    "key": wire_key(
                        "simulation_time", status_fields["simulation_time"]
                    ),
                    "gql": contract.TIME_FIELD,
                },
            ],
        },
        "objects": [
            {
                "gql": field_name(contract.INPUTS_SECTION),
                "operation": inputs_state,
                "unionType": contract.SIMULATION_INPUTS_UNION,
                "memberSection": field_name(contract.INPUTS_SECTION),
            },
            {
                "gql": field_name(contract.OUTPUTS_SECTION),
                "operation": document.operation_ref(
                    f"{prefix}/{SIMULATION_OUTPUTS_TOPIC}", "send"
                ),
                "unionType": contract.SIMULATION_OUTPUTS_UNION,
                "memberSection": field_name(contract.OUTPUTS_SECTION),
            },
        ],
        "directives": [directive(d) for d in contract.SIMULATION_DIRECTIVES],
        "waitTimeoutS": contract.WAIT_TIMEOUT,
        "members": members,
    }


# --- Instances of the `{field}` channels ------------------------------------------


def _instances(
    document: Document, module_name: str, kind: Literal["sensors", "controller"]
) -> dict[str, Any]:
    """Identity metadata of one module's ``{field}`` channel: the instances of
    its parameter (``sensors``: the ``SensorValues`` fields on the devices
    prefix; ``controller``: its ``computed_field``s on the controller prefix)
    with their ``ComponentMeta`` attributes, so the bridge can serve a list
    query over them."""
    config = document.config
    sensor_values_cls = all_module_descriptions()[module_name].sensor_values_cls
    if kind == "sensors":
        topic_prefix = config.mqtt_devices_topic_prefix
        module_prefix = device_module_prefix(module_name)
        fields: dict[str, FieldInfo | ComputedFieldInfo] = dict(
            sensor_values_cls.model_fields
        )
    else:
        topic_prefix = config.mqtt_controller_topic_prefix
        module_prefix = module_name
        fields = dict(sensor_values_cls.model_computed_fields)
    template = f"{topic_prefix}/{module_prefix}/{{field}}"

    # A `topic_override` (see ComponentMeta) can put a field outside this
    # group's `{module_prefix}/{field}` path (thrusters'
    # `thrusters_thruster_aft` -> "dummy-pcs/thruster-aft-active"). Those are
    # their own concrete topics elsewhere, already queryable on their own.
    group_prefix = f"{topic_prefix}/{module_prefix}/"
    topics = {
        name: topic
        for name, topic in field_topics(
            sensor_values_cls, topic_prefix, module_prefix, computed=kind != "sensors"
        ).items()
        if topic.startswith(group_prefix)
    }
    group = document.groups.get((template, "send"))
    if group is None or not topics:
        raise RuntimeError(f"module {module_name!r} publishes no {kind} fields")
    if missing := set(topics.values()) - group.example_topics:
        raise RuntimeError(
            f"{kind} topics of module {module_name!r} are not in the channel "
            f"wiring: {sorted(missing)}"
        )

    def attributes(name: str) -> dict[str, Any]:
        extra = fields[name].json_schema_extra
        extra = extra if isinstance(extra, dict) else {}
        return {
            "field": name,
            "yard_tag": extra.get("yard_tag") or None,
            "component_type": extra.get("component_type"),
            "valve_type": extra.get("valve_type"),
        }

    return {
        "operation": operation_key(template, "send"),
        "instances": {
            topic.rsplit("/", 1)[1]: attributes(name)
            for name, topic in sorted(topics.items(), key=lambda kv: kv[1])
        },
    }
