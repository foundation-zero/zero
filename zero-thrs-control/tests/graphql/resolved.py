"""The THRS contract, resolved the way zero-mqtt-graphql resolves it.

The ``x-mqtt-graphql`` extension names GraphQL types and binds them to
operations; what a type's fields *are* comes from the document's schemas
(``zero-mqtt-graphql/src/extension``). The cross-API suites need that
resolved shape - every leaf with its GraphQL name, wire key, scalar type and
enum members, every mutation with its input fields and bounds - to build
queries, seeds and expectations for both APIs without typing any of it by
hand. This module is an independent reading of the same document, in Python,
so the suites also check the bridge's reading against it.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any

from thrs.orchestration.config import Config
from thrs.spec import build_thrs_spec
from thrs.spec.asyncapi import operation_topic
from thrs.spec.extension import EXTENSION_KEY

SCHEMA_REF_PREFIX = "#/components/schemas/"


def field_name(key: str) -> str:
    """The bridge's GraphQL name for a wire key (``naming.rs::field_name``):
    lowerCamelCase with the key's internal capitals kept."""
    words = [w for w in key.replace("-", "_").split("_") if w]
    if not words:
        return ""
    head, *rest = words
    return head[0].lower() + head[1:] + "".join(w[0].upper() + w[1:] for w in rest)


@dataclass(frozen=True)
class Property:
    kind: str  # "stamped" | "scalar" | "object"
    type: str | None = None
    optional: bool = False
    enum_type: str | None = None
    enum_values: dict[str, str] | None = None
    ref: str | None = None
    default: Any = None
    bounds: dict[str, float] | None = None


class ResolvedSpec:
    """A document plus its extension, with the extension's types read against
    the document's schemas."""

    def __init__(self, config: Config) -> None:
        self.spec = build_thrs_spec(config)
        self.extension = self.spec[EXTENSION_KEY]
        self.schemas = self.spec["components"]["schemas"]
        self.type_refs = {
            name: entry["schema"]["$ref"]
            for name, entry in self.extension["types"].items()
        }
        self.type_by_ref = {ref: name for name, ref in self.type_refs.items()}

    # --- Schemas ---------------------------------------------------------

    def topic(self, ref: dict[str, Any]) -> str:
        return operation_topic(ref, self.spec)

    def deref(self, schema: dict[str, Any]) -> dict[str, Any]:
        ref = schema.get("$ref")
        if ref is None:
            return schema
        return self.schemas[ref.removeprefix(SCHEMA_REF_PREFIX)]

    @staticmethod
    def _unwrap_nullable(schema: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        any_of = schema.get("anyOf")
        if not any_of:
            return schema, False
        others = [s for s in any_of if s.get("type") != "null"]
        nullable = len(others) != len(any_of)
        return (others[0] if len(others) == 1 else schema), nullable

    def property(self, schema: dict[str, Any]) -> Property:
        inner, nullable = self._unwrap_nullable(schema)
        resolved = self.deref(inner)
        default = schema.get("default")
        properties = resolved.get("properties")
        if properties is not None and set(properties) == {"Value", "TimeStamp"}:
            value, value_nullable = self._unwrap_nullable(properties["Value"])
            value = self.deref(value)
            enum = self._enum(value)
            return Property(
                "stamped",
                type=self._scalar(value),
                optional=nullable or value_nullable,
                enum_type=enum[0] if enum else None,
                enum_values=enum[1] if enum else None,
                default=default,
            )
        scalar = self._scalar(resolved)
        if scalar is not None:
            enum = self._enum(resolved)
            return Property(
                "scalar",
                type=scalar,
                optional=nullable,
                enum_type=enum[0] if enum else None,
                enum_values=enum[1] if enum else None,
                default=default,
                bounds=self._bounds(resolved),
            )
        if properties is not None:
            return Property("object", optional=nullable, ref=inner.get("$ref"))
        raise ValueError(f"unsupported property schema {schema}")

    @staticmethod
    def _scalar(schema: dict[str, Any]) -> str | None:
        if "x-enum-varnames" in schema:
            return "String"
        match schema.get("type"):
            case "number":
                return "Float"
            case "integer":
                return "Int"
            case "boolean":
                return "Boolean"
            case "string":
                return "DateTime" if schema.get("format") == "date-time" else "String"
            case "array":
                item = (schema.get("prefixItems") or [schema.get("items")])[0]
                inner = ResolvedSpec._scalar(item) if item else None
                return f"[{inner}!]" if inner else None
        return None

    @staticmethod
    def _enum(schema: dict[str, Any]) -> tuple[str, dict[str, str]] | None:
        names = schema.get("x-enum-varnames")
        if names is None:
            return None
        values = [v if isinstance(v, str) else str(v) for v in schema["enum"]]
        return schema["title"], dict(zip(values, names, strict=True))

    @staticmethod
    def _bounds(schema: dict[str, Any]) -> dict[str, float] | None:
        bounds = {
            key: schema[name]
            for key, name in (
                ("min", "minimum"),
                ("max", "maximum"),
                ("exclusiveMin", "exclusiveMinimum"),
                ("exclusiveMax", "exclusiveMaximum"),
            )
            if name in schema
        }
        return bounds or None

    # --- Types -----------------------------------------------------------

    def properties(self, type_name: str) -> list[tuple[str, Property]]:
        schema = self.deref({"$ref": self.type_refs[type_name]})
        return [
            (key, self.property(s)) for key, s in schema.get("properties", {}).items()
        ]

    def leaves(
        self, type_name: str, wire_keys: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """The stamped leaves of a component type, in the resolved shape the suites
        consume (``gql``, ``key``, ``type``, ``optional``, ``enumType``,
        ``enumValues``, ``actuatedKey``, ``default``)."""
        out = []
        for key, prop in self.properties(type_name):
            if prop.kind != "stamped":
                continue
            leaf: dict[str, Any] = {
                "gql": field_name(key),
                "key": key,
                "type": prop.type,
                "optional": prop.optional,
            }
            if prop.enum_type:
                leaf["enumType"] = prop.enum_type
                leaf["enumValues"] = prop.enum_values
            if wire_keys and key in wire_keys:
                leaf["actuatedKey"] = wire_keys[key]
            if prop.default is not None:
                leaf["default"] = prop.default
            out.append(leaf)
        return out

    def type_for_ref(self, ref: str | None) -> str | None:
        return self.type_by_ref.get(ref) if ref else None

    def _component_type(self, spec: dict[str, Any], prop: Property, key: str) -> str:
        name = spec.get("typeName") or self.type_for_ref(prop.ref)
        if name is None:
            raise KeyError(f"no declared type is served from {prop.ref} ({key})")
        return name

    # --- Sections, members, mutations ------------------------------------

    def object_section(self, section: dict[str, Any]) -> dict[str, Any]:
        """An ``object`` section with its fields resolved, as the bridge serves them."""
        specs = {f["key"]: f for f in section.get("fields", [])}
        fields = []
        for key, prop in self.properties(section["typeName"]):
            spec = specs.get(key, {})
            gql = spec.get("gql") or field_name(key)
            if prop.kind == "scalar":
                fields.append(
                    {
                        "gql": gql,
                        "key": key,
                        "type": prop.type,
                        "optional": prop.optional,
                    }
                )
                continue
            type_name = self._component_type(spec, prop, key)
            leaves = self.leaves(type_name, spec.get("wireKeys"))
            if not leaves:
                continue
            field: dict[str, Any] = {
                "gql": gql,
                "key": key,
                "typeName": type_name,
                "optional": prop.optional,
                "leaves": leaves,
            }
            if "operation" in spec:
                field["operation"] = spec["operation"]
            fields.append(field)
        fields.sort(key=lambda f: f["gql"])
        return {**section, "fields": fields}

    def stamped_section(self, section: dict[str, Any]) -> dict[str, Any]:
        fields = []
        for spec in section["fields"]:
            type_name = spec.get("typeName") or self.type_for_ref(
                self._pinned_ref(spec["operation"])
            )
            assert type_name, spec
            fields.append(
                {**spec, "typeName": type_name, "leaves": self.leaves(type_name)}
            )
        return {**section, "fields": fields}

    def _pinned_ref(self, ref: dict[str, Any]) -> str | None:
        operation = self.spec["operations"][ref["operation"]]
        channel_key = operation["channel"]["$ref"].rsplit("/", 1)[-1]
        message_key = operation["messages"][0]["$ref"].rsplit("/", 1)[-1]
        message = self.spec["channels"][channel_key]["messages"][message_key]
        schema = message["payload"]
        for param, value in ref.get("parameters", {}).items():
            schema = message[f"x-{param}-schema"][value]
        return schema.get("$ref")

    def switch_section(self, section: dict[str, Any]) -> dict[str, Any]:
        return {**section, "object": self.plain_object(section["objectTypeName"])}

    def plain_object(self, type_name: str) -> dict[str, Any]:
        fields = []
        for key, prop in self.properties(type_name):
            field: dict[str, Any] = {
                "gql": field_name(key),
                "key": key,
                "optional": prop.optional,
            }
            if prop.kind == "object":
                field["object"] = self.plain_object(self._component_type({}, prop, key))
            else:
                field["type"] = prop.type
            fields.append(field)
        return {"typeName": type_name, "fields": fields}

    def section(self, section: dict[str, Any]) -> dict[str, Any]:
        match section["kind"]:
            case "stampedFields":
                return self.stamped_section(section)
            case "object":
                return self.object_section(section)
            case "switch":
                return self.switch_section(section)
        raise ValueError(section["kind"])

    def mutation(
        self, mutation: dict[str, Any], sections: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """A mutation with what the bridge derives from the section it returns
        (``sections``: the member's resolved ``object`` sections by GraphQL
        name): ``argType``/``bounds``/``invariants`` (setField),
        ``component``/``inputFields``/``derived`` (setComponent)."""
        resolved = dict(mutation)
        if mutation["kind"] == "setFlag":
            resolved["argType"] = "Boolean"
            return resolved
        section = sections[mutation["returns"]]
        state_schema = self.deref({"$ref": self.type_refs[section["typeName"]]})
        key = mutation["key"]
        prop = self.property(state_schema["properties"][key])
        if mutation["kind"] == "setField":
            resolved["argType"] = prop.type
            if prop.bounds:
                resolved["bounds"] = prop.bounds
            resolved["invariants"] = state_schema.get("x-invariants", [])
        else:
            # The component as the returned section serves it.
            component_field = next(
                (f for f in section["fields"] if f["key"] == key), None
            )
            assert component_field is not None, (
                f"setComponent {mutation['gql']!r}: key {key!r} is not a field of "
                f"returned section {mutation['returns']!r} "
                f"(the section dropped it, e.g. a component with no stamped leaves)"
            )
            resolved["component"] = component_field["gql"]
            component = self.deref({"$ref": prop.ref})
            leaves = [
                (k, self.property(s))
                for k, s in component["properties"].items()
                if self.property(s).kind == "stamped"
            ]
            resolved["inputFields"] = [
                {
                    "gql": field_name(k),
                    "key": k,
                    "type": p.type,
                    "required": not p.optional,
                    **(
                        {"enumType": p.enum_type, "enumValues": p.enum_values}
                        if p.enum_type
                        else {}
                    ),
                }
                for k, p in leaves
            ]
            resolved["derived"] = state_schema.get("x-derived", [])
        return resolved

    def member(self, member: dict[str, Any]) -> dict[str, Any]:
        sections = [self.section(s) for s in member["sections"]]
        objects = {s["gql"]: s for s in sections if s["kind"] == "object"}
        return {
            **member,
            "sections": sections,
            "mutations": [self.mutation(m, objects) for m in member["mutations"]],
        }

    @cached_property
    def members(self) -> dict[str, dict[str, Any]]:
        """The ``modules`` view's members by GraphQL name, resolved."""
        return {m["gql"]: self.member(m) for m in self.extension["views"][0]["members"]}

    @cached_property
    def lifecycle(self) -> dict[str, Any]:
        """The simulation lifecycle, resolved: status field types, directive
        arguments, member sections and mutations."""
        lifecycle = self.extension["lifecycles"][0]
        status_ref = self._pinned_ref(lifecycle["status"]["operation"])
        status_schema = self.deref({"$ref": status_ref}) if status_ref else {}
        status_fields = [
            {
                "gql": f.get("gql") or field_name(f["key"]),
                "key": f["key"],
                "type": self.property(status_schema["properties"][f["key"]]).type,
            }
            for f in lifecycle["status"]["fields"]
        ]
        directives = []
        for d in lifecycle["directives"]:
            resolved = dict(d)
            if "key" in d:
                message_ref = self._pinned_ref(d["target"])
                message = self.deref({"$ref": message_ref}) if message_ref else {}
                prop = self.property(message["properties"][d["key"]])
                resolved["argName"] = d.get("argName") or field_name(d["key"])
                resolved["argType"] = prop.type
                resolved["argRequired"] = prop.default is None and not prop.optional
                resolved["default"] = prop.default
                if prop.bounds:
                    resolved["bounds"] = prop.bounds
            directives.append(resolved)
        members = []
        for member in lifecycle["members"]:
            sections = [self.object_section(s) for s in member["sections"]]
            objects = {s["gql"]: s for s in sections}
            members.append(
                {
                    **member,
                    "sections": sections,
                    "mutations": [
                        self.mutation(m, objects) for m in member["mutations"]
                    ],
                }
            )
        return {
            **lifecycle,
            "status": {**lifecycle["status"], "fields": status_fields},
            "directives": directives,
            "members": members,
        }


def section_of(member: dict[str, Any], gql: str) -> dict[str, Any]:
    """One named section of a resolved view or lifecycle member."""
    return next(s for s in member["sections"] if s["gql"] == gql)
