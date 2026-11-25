//! Payload fields and field attributes from a message's JSON Schema.

use std::collections::{BTreeMap, BTreeSet};

use log::{info, warn};
use roas_asyncapi::common::reference::RefOr;
use serde_json::Value;

use super::roas::{
    Channel, Document, Items, Message, Schema, SchemaOrMultiFormat, SchemaType, SubSchema,
};
use super::unresolved_reason;
use crate::api_model::{EnumValue, FieldDef, FieldType, Payload};
use crate::naming::enum_value_name;

/// The payload of a channel's message, with what else is read from its
/// schema.
#[derive(Debug)]
pub(super) struct MessagePayload {
    pub(super) payload: Payload,
    /// JSON pointer to the payload schema in the document, which its
    /// validator is built from.
    pub(super) schema_ref: String,
    /// Attributes per payload field, from the schema's `x-*` extensions.
    pub(super) field_attributes: BTreeMap<String, BTreeMap<String, String>>,
}

/// The payload of the channel's first message; `None` when there is no
/// message, no payload, or the payload reference does not resolve.
///
/// Channels with multiple messages are not yet union-typed; only the first
/// message contributes a payload.
pub(super) fn message_payload(
    channel_ref: &str,
    channel: &Channel,
    doc: &Document,
) -> Option<MessagePayload> {
    let Some((message_ref, message)) = channel_messages(channel_ref, channel, doc)
        .into_iter()
        .next()
    else {
        info!("Channel {channel_ref} has no message");
        return None;
    };
    // The message payload may be inline or a `$ref` into components
    let Some(payload_ref) = &message.payload else {
        info!("Channel {channel_ref} message has no payload");
        return None;
    };

    let resolution = payload_ref.get_item(doc);
    let reason = unresolved_reason(&resolution);
    let Some(schema_or_multi) = resolution.found() else {
        info!("Channel {channel_ref} message payload reference {reason}");
        return None;
    };

    let schema_ref = payload_ref
        .resolved_ref(doc)
        .map_or_else(|| format!("{message_ref}/payload"), ToOwned::to_owned);
    Some(MessagePayload {
        payload: Payload {
            // Named after its schema component; an inline payload after its
            // full pointer.
            name: schema_ref
                .strip_prefix("#/components/schemas/")
                .unwrap_or(&schema_ref)
                .to_string(),
            fields: extract_fields_from_schema_or_multi(schema_or_multi, doc),
        },
        field_attributes: serde_json::to_value(schema_or_multi)
            .map(|schema| extensions_from_payload_schema(&schema))
            .unwrap_or_default(),
        schema_ref,
    })
}

/// All messages referenced by the channel, resolved against components.
pub(super) fn channel_messages<'a>(
    channel_ref: &str,
    channel: &'a Channel,
    doc: &'a Document,
) -> BTreeMap<String, &'a Message> {
    channel
        .messages
        .iter()
        .filter_map(|(message_key, message_ref)| {
            // Where a `$ref` chain ends, or the channel's own entry for an
            // inline message.
            let message = message_ref.get_item(doc).found()?;
            let pointer = message_ref.resolved_ref(doc).map_or_else(
                || {
                    let key = message_key.replace('~', "~0").replace('/', "~1");
                    format!("{channel_ref}/messages/{key}")
                },
                ToOwned::to_owned,
            );
            Some((pointer, message))
        })
        .collect()
}

/// Extension attributes per payload field, read from `x-*` schema
/// extensions: `properties.<name>.x-<key>` → `<key>`. Non-scalar extension
/// values are ignored.
fn extensions_from_payload_schema(
    payload_schema: &Value,
) -> BTreeMap<String, BTreeMap<String, String>> {
    let Some(properties) = payload_schema.get("properties").and_then(Value::as_object) else {
        return BTreeMap::new();
    };
    properties
        .iter()
        .filter_map(|(name, property)| {
            let extensions: BTreeMap<String, String> = property
                .as_object()?
                .iter()
                .filter_map(|(key, value)| {
                    let attribute = key.strip_prefix("x-")?;
                    let rendered = match value {
                        Value::String(string) => string.clone(),
                        Value::Number(number) => number.to_string(),
                        Value::Bool(boolean) => boolean.to_string(),
                        _ => return None,
                    };
                    Some((attribute.to_string(), rendered))
                })
                .collect();
            (!extensions.is_empty()).then_some((name.clone(), extensions))
        })
        .collect()
}

fn extract_fields_from_schema_or_multi(
    schema_or_multi: &SchemaOrMultiFormat,
    doc: &Document,
) -> BTreeMap<String, FieldDef> {
    match schema_or_multi {
        SchemaOrMultiFormat::Schema(schema) => extract_fields_from_schema(schema, doc),
        SchemaOrMultiFormat::MultiFormat(mf) => {
            // Try to deserialize the raw schema value as a Schema
            if let Ok(schema) = serde_json::from_value::<Schema>(mf.schema.clone()) {
                extract_fields_from_schema(&schema, doc)
            } else {
                info!("Payload schema has no fields");
                BTreeMap::new()
            }
        }
        SchemaOrMultiFormat::Bool(_) => {
            info!("Payload schema has no fields");
            BTreeMap::new()
        }
    }
}

/// The fields of an object schema, non-null when `required` and without a
/// `null` arm.
fn extract_fields_from_schema(schema: &Schema, doc: &Document) -> BTreeMap<String, FieldDef> {
    // Fields colliding after lowerCamel sanitization are kept here; building
    // the schema then stops at the duplicate field.
    schema
        .properties
        .iter()
        .filter_map(|(name, subschema)| {
            let field = field_def_for_subschema(name.clone(), subschema, doc)?;
            let non_null = field.non_null && schema.required.contains(name);
            Some((name.clone(), FieldDef { non_null, ..field }))
        })
        .collect()
}

/// Derive a field from a (possibly `$ref`'d) subschema, non-null when it
/// has no `null` arm. A `$ref`'d one is named after the last segment of the
/// reference it resolved at.
fn field_def_for_subschema(name: String, sub: &SubSchema, doc: &Document) -> Option<FieldDef> {
    let SubSchema::Schema(entry) = sub else {
        return None;
    };
    let resolution = entry.get_item(doc);
    let reason = unresolved_reason(&resolution);
    let Some(schema) = resolution.found() else {
        warn!(
            "Schema reference {:?} of {name} {reason}",
            entry.reference().map(|r| r.reference.as_str()),
        );
        return None;
    };
    let name = entry
        .resolved_ref(doc)
        .and_then(|r| r.rsplit('/').next())
        .map_or(name, ToOwned::to_owned);
    def_from_schema(name, schema, doc)
}

fn def_from_schema(name: String, schema: &Schema, doc: &Document) -> Option<FieldDef> {
    if let Some(schema_type) = &schema.schema_type {
        return match schema_type {
            SchemaType::Single(t) => {
                field_type_for_json_type(name, t, schema, doc).map(FieldDef::non_null)
            }
            SchemaType::Multiple(types) => one_type(types.iter().enumerate().map(|(index, t)| {
                field_type_for_json_type(format!("{name}{index}"), t, schema, doc)
                    .map(FieldDef::non_null)
            })),
        };
    }

    // Named constants without a `type`: an enum of whatever their values
    // are, nullable when one of them is `null`.
    if let Some(constants) = named_constants(schema) {
        let mut values = constants
            .iter()
            .map(|(raw, _)| raw)
            .filter(|raw| !raw.is_null());
        let plain = if values.clone().all(|raw| raw.is_string()) {
            FieldType::String
        } else if values.all(|raw| raw.is_i64()) {
            FieldType::Int
        } else {
            FieldType::Json
        };
        return Some(FieldDef {
            non_null: constants.iter().all(|(raw, _)| !raw.is_null()),
            field_type: enum_field_type(name, schema, plain),
        });
    }
    // A union, nullable when one of its arms is `null`.
    for arms in [&schema.any_of, &schema.one_of].into_iter().flatten() {
        let fields = arms
            .iter()
            .enumerate()
            .map(|(index, sub)| field_def_for_subschema(format!("{name}{index}"), sub, doc));
        if let Some(field) = one_type(fields) {
            return Some(field);
        }
    }
    // An intersection, such as pydantic wrapping a single `$ref`: the type
    // of its first typed arm, non-null when any typed arm rules out `null`.
    if let Some(all_of) = &schema.all_of {
        let arms: Vec<FieldDef> = all_of
            .iter()
            .enumerate()
            .filter_map(|(index, sub)| field_def_for_subschema(format!("{name}{index}"), sub, doc))
            .collect();
        let non_null = arms.iter().any(|arm| arm.non_null);
        if let Some(first) = arms.into_iter().next() {
            return Some(FieldDef { non_null, ..first });
        }
    }

    None
}

/// The field of a union of `arms`, of which `None` are `null` or untyped
/// arms: the type they all share, or any JSON when they differ, so the
/// JSON Schema decides which values are valid. Non-null only when every arm
/// is, as an untyped arm allows `null` too. `None` when no arm has a type.
fn one_type(arms: impl Iterator<Item = Option<FieldDef>>) -> Option<FieldDef> {
    let arms: Vec<Option<FieldDef>> = arms.collect();
    let non_null = arms
        .iter()
        .all(|arm| arm.as_ref().is_some_and(|arm| arm.non_null));
    let mut types = arms.into_iter().flatten().map(|arm| arm.field_type);
    let first = types.next()?;
    let field_type = if types.all(|t| t == first) {
        first
    } else {
        FieldType::Json
    };
    Some(FieldDef {
        field_type,
        non_null,
    })
}

fn field_type_for_json_type(
    name: String,
    t: &str,
    schema: &Schema,
    doc: &Document,
) -> Option<FieldType> {
    match t {
        "object" => {
            let fields = extract_fields_from_schema(schema, doc);
            (!fields.is_empty()).then(|| FieldType::Object(name, Box::new(fields)))
        }
        "array" => Some(array_field_type(name, schema, doc)),
        "number" if schema.format.as_deref() == Some("float") => Some(FieldType::Float32),
        "number" => Some(FieldType::Float),
        "integer" => Some(enum_field_type(name, schema, FieldType::Int)),
        "boolean" => Some(FieldType::Boolean),
        "string" => Some(string_field_type(name, schema)),
        _ => None,
    }
}

/// A date or time when the string has a date or time `format`, otherwise an
/// enum or a plain string (see [`enum_field_type`]).
fn string_field_type(name: String, schema: &Schema) -> FieldType {
    match schema.format.as_deref() {
        Some("date-time") => return FieldType::DateTime,
        Some("date") => return FieldType::Date,
        Some("time") => return FieldType::Time,
        Some("duration") => return FieldType::Duration,
        _ => {}
    }
    enum_field_type(name, schema, FieldType::String)
}

/// An enum when the schema has a fixed set of values that each have their
/// own GraphQL name, otherwise `plain`. The values and their names come from
/// [`named_constants`] when the schema has them, otherwise from `enum`,
/// where only strings name themselves, so an integer `enum` stays `plain`.
/// A `null` value is no enum value: it makes the field nullable instead.
fn enum_field_type(name: String, schema: &Schema, plain: FieldType) -> FieldType {
    let constants = named_constants(schema);
    let candidates: Vec<(&Value, Option<&str>)> = match (&constants, &schema.enum_values) {
        (Some(constants), _) => constants
            .iter()
            .map(|&(raw, title)| (raw, Some(title)))
            .filter(|(raw, _)| !raw.is_null())
            .collect(),
        (None, Some(raw_values)) => raw_values
            .iter()
            .filter(|raw| !raw.is_null())
            .map(|raw| (raw, raw.as_str()))
            .collect(),
        (None, None) => return plain,
    };
    let values: Option<Vec<EnumValue>> = candidates
        .iter()
        .map(|&(raw, source)| {
            (raw.is_string() || raw.is_i64()).then_some(())?;
            Some(EnumValue {
                name: enum_value_name(source?)?,
                raw: raw.clone(),
            })
        })
        .collect();
    let distinct = |values: &[EnumValue]| {
        let names: BTreeSet<&str> = values.iter().map(|value| value.name.as_str()).collect();
        !values.is_empty() && names.len() == values.len()
    };
    match values {
        Some(values) if distinct(&values) => FieldType::Enum(name, values),
        // An integer `enum` has no names, so it is a plain integer.
        None if constants.is_none() && plain == FieldType::Int => plain,
        _ => {
            let raw: Vec<&Value> = candidates.iter().map(|&(raw, _)| raw).collect();
            warn!(
                "Enum {name} {raw:?} has values without a distinct GraphQL name, using {plain:?}"
            );
            plain
        }
    }
}

/// The values of a schema written as named constants, the standard JSON
/// Schema way to name enum values: a `oneOf` whose every arm is a `const`
/// with a `title`, as in `{"oneOf": [{"const": 1, "title": "CONSTANT_SPEED"},
/// …]}`. `None` for any other schema.
fn named_constants(schema: &Schema) -> Option<Vec<(&Value, &str)>> {
    schema
        .one_of
        .as_ref()?
        .iter()
        .map(|arm| match arm {
            SubSchema::Schema(boxed) => match boxed.as_ref() {
                RefOr::Item(arm) => Some((arm.const_value.as_ref()?, arm.title.as_deref()?)),
                RefOr::Reference(_) => None,
            },
            SubSchema::Bool(_) => None,
        })
        .collect()
}

/// A list when every element has the same known type, otherwise any JSON.
/// Its elements are non-null unless their schema has a `null` arm.
/// The element type is unknown for a tuple, as draft-07 allows extra items
/// of any type, and for `prefixItems` (JSON Schema 2020-12), which the
/// draft-07 parser drops.
fn array_field_type(name: String, schema: &Schema, doc: &Document) -> FieldType {
    let element = match &schema.items {
        Some(Items::Single(item)) => field_def_for_subschema(name, item, doc),
        Some(Items::Tuple(_)) | None => None,
    };
    element.map_or(FieldType::Json, |element| {
        FieldType::List(Box::new(element))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn schema_with_properties(props: BTreeMap<String, Value>) -> Schema {
        let mut properties = BTreeMap::new();
        for (k, v) in props {
            let sub: SubSchema = serde_json::from_value(v).unwrap();
            properties.insert(k, sub);
        }
        Schema {
            properties,
            ..Default::default()
        }
    }

    /// A document whose schema components are `schemas`.
    fn document(schemas: &Value) -> Document {
        serde_json::from_value(json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "components": {"schemas": schemas}
        }))
        .unwrap()
    }

    #[test_log::test]
    fn test_extract_scalar_fields() {
        let props = BTreeMap::from([
            ("celsius".to_string(), json!({"type": "number"})),
            (
                "dutypoint".to_string(),
                json!({"type": "number", "format": "float"}),
            ),
            (
                "ratio".to_string(),
                json!({"type": "number", "format": "double"}),
            ),
            ("sensor_id".to_string(), json!({"type": "integer"})),
            ("ok".to_string(), json!({"type": "boolean"})),
            ("label".to_string(), json!({"type": "string"})),
            (
                "stamp".to_string(),
                json!({"type": "string", "format": "date-time"}),
            ),
            (
                "day".to_string(),
                json!({"type": "string", "format": "date"}),
            ),
            (
                "start".to_string(),
                json!({"type": "string", "format": "time"}),
            ),
            (
                "step".to_string(),
                json!({"type": "string", "format": "duration"}),
            ),
            (
                "email".to_string(),
                json!({"type": "string", "format": "email"}),
            ),
            (
                "nested".to_string(),
                json!({"type": "object", "properties": {"x": {"type": "number"}}}),
            ),
            (
                "reffed".to_string(),
                json!({"$ref": "#/components/schemas/nested"}),
            ),
            ("items".to_string(), json!({"type": "array"})),
        ]);
        let schema = schema_with_properties(props);
        let doc = document(&json!({
            "nested": {"type": "object", "properties": {"x": {"type": "number"}}}
        }));

        let fields = extract_fields_from_schema(&schema, &doc);
        assert_eq!(fields.len(), 14);
        // BTreeMap ordering, so sorted by key
        let get = |name: &str| &fields[name].field_type;
        // An array without a declared element type is any JSON.
        assert_eq!(get("items"), &FieldType::Json);
        assert_eq!(get("celsius"), &FieldType::Float);
        assert_eq!(get("dutypoint"), &FieldType::Float32);
        // Other formats stay plain numbers.
        assert_eq!(get("ratio"), &FieldType::Float);
        assert_eq!(get("sensor_id"), &FieldType::Int);
        assert_eq!(get("ok"), &FieldType::Boolean);
        assert_eq!(get("label"), &FieldType::String);
        assert_eq!(get("stamp"), &FieldType::DateTime);
        assert_eq!(get("day"), &FieldType::Date);
        assert_eq!(get("start"), &FieldType::Time);
        assert_eq!(get("step"), &FieldType::Duration);
        // Other formats stay plain strings.
        assert_eq!(get("email"), &FieldType::String);
        let x = || BTreeMap::from([("x".to_string(), FieldDef::nullable(FieldType::Float))]);
        assert_eq!(
            get("nested"),
            &FieldType::Object("nested".to_string(), Box::new(x()))
        );
        assert_eq!(
            get("reffed"),
            &FieldType::Object("nested".to_string(), Box::new(x()))
        );
    }

    #[test_log::test]
    fn test_array_types() {
        let props = BTreeMap::from([
            (
                "modules".to_string(),
                json!({"type": "array", "items": {"type": "string"}}),
            ),
            (
                "same".to_string(),
                json!({"type": "array", "items": [{"type": "number"}, {"type": "number"}]}),
            ),
            (
                "mixed".to_string(),
                json!({"type": "array", "items": [{"type": "number"}, {"type": "string"}]}),
            ),
            (
                "tuning".to_string(),
                json!({"type": "array", "prefixItems": [{"type": "number"}, {"type": "number"}]}),
            ),
        ]);

        let fields =
            extract_fields_from_schema(&schema_with_properties(props), &document(&json!({})));

        let list = |element| FieldType::List(Box::new(FieldDef::non_null(element)));
        assert_eq!(fields["modules"].field_type, list(FieldType::String));
        // A tuple allows extra items of any type (draft-07 `additionalItems`).
        assert_eq!(fields["same"].field_type, FieldType::Json);
        assert_eq!(fields["mixed"].field_type, FieldType::Json);
        // The draft-07 parser drops `prefixItems`, so the element type is unknown.
        assert_eq!(fields["tuning"].field_type, FieldType::Json);
    }

    #[test_log::test]
    fn test_union_types_have_one_type_or_are_json() {
        let number_or_string = json!([{"type": "number"}, {"type": "string"}]);
        let props = BTreeMap::from([
            (
                "optional".to_string(),
                json!({"anyOf": [{"type": "number"}, {"type": "null"}]}),
            ),
            ("nullable".to_string(), json!({"type": ["number", "null"]})),
            ("any_of".to_string(), json!({"anyOf": number_or_string})),
            ("one_of".to_string(), json!({"oneOf": number_or_string})),
            ("types".to_string(), json!({"type": ["number", "string"]})),
            (
                "items".to_string(),
                json!({"type": "array", "items": {"anyOf": number_or_string}}),
            ),
        ]);

        let fields =
            extract_fields_from_schema(&schema_with_properties(props), &document(&json!({})));

        let field_type = |name: &str| &fields[name].field_type;
        assert_eq!(field_type("optional"), &FieldType::Float);
        assert_eq!(field_type("nullable"), &FieldType::Float);
        assert_eq!(field_type("any_of"), &FieldType::Json);
        assert_eq!(field_type("one_of"), &FieldType::Json);
        assert_eq!(field_type("types"), &FieldType::Json);
        // Each element is a number or a string: any JSON, not `Float`.
        assert_eq!(
            field_type("items"),
            &FieldType::List(Box::new(FieldDef::non_null(FieldType::Json)))
        );
    }

    #[test_log::test]
    fn test_enum_types() {
        let props = BTreeMap::from([
            (
                "state".to_string(),
                json!({"type": "string", "enum": ["in use", "standby"]}),
            ),
            (
                "pump_mode".to_string(),
                json!({"type": "integer", "enum": [1, 3, 4]}),
            ),
            (
                "clash".to_string(),
                json!({"type": "string", "enum": ["a b", "a_b"]}),
            ),
            (
                "named_pump_mode".to_string(),
                json!({
                    "type": "integer",
                    "oneOf": [
                        {"const": 1, "title": "CONSTANT_SPEED"},
                        {"const": 3, "title": "constant pressure"}
                    ]
                }),
            ),
            (
                "named_state".to_string(),
                json!({
                    "type": "string",
                    "oneOf": [{"const": "in use", "title": "OCCUPIED"}]
                }),
            ),
            (
                "untyped_named_mode".to_string(),
                json!({"oneOf": [{"const": 1, "title": "ONE"}, {"const": 2, "title": "TWO"}]}),
            ),
            (
                "untitled".to_string(),
                json!({
                    "type": "integer",
                    "oneOf": [{"const": 1, "title": "ONE"}, {"const": 3}]
                }),
            ),
        ]);

        let fields: BTreeMap<String, FieldType> =
            extract_fields_from_schema(&schema_with_properties(props), &document(&json!({})))
                .into_iter()
                .map(|(name, field)| (name, field.field_type))
                .collect();

        let value = |name: &str, raw: Value| EnumValue {
            name: name.to_string(),
            raw,
        };
        assert_eq!(
            fields["state"],
            FieldType::Enum(
                "state".to_string(),
                vec![
                    value("IN_USE", json!("in use")),
                    value("STANDBY", json!("standby"))
                ]
            )
        );
        // Integer values without names have no names to use.
        assert_eq!(fields["pump_mode"], FieldType::Int);
        // Both values would be named `A_B`.
        assert_eq!(fields["clash"], FieldType::String);
        // Named values take those names, made valid GraphQL names.
        assert_eq!(
            fields["named_pump_mode"],
            FieldType::Enum(
                "named_pump_mode".to_string(),
                vec![
                    value("CONSTANT_SPEED", json!(1)),
                    value("CONSTANT_PRESSURE", json!(3))
                ]
            )
        );
        assert_eq!(
            fields["named_state"],
            FieldType::Enum(
                "named_state".to_string(),
                vec![value("OCCUPIED", json!("in use"))]
            )
        );
        // Named constants need no `type`.
        assert_eq!(
            fields["untyped_named_mode"],
            FieldType::Enum(
                "untyped_named_mode".to_string(),
                vec![value("ONE", json!(1)), value("TWO", json!(2))]
            )
        );
        // A constant without a title is no named constant.
        assert_eq!(fields["untitled"], FieldType::Int);
    }

    #[test_log::test]
    fn test_empty_properties_returns_empty_fields() {
        let schema = Schema::default();
        let fields = extract_fields_from_schema(&schema, &document(&json!({})));
        assert_eq!(fields.len(), 0);
    }

    #[test_log::test]
    fn test_extensions_from_payload_schema() {
        let schema = json!({
            "type": "object",
            "properties": {
                "current_a": {"type": "number", "x-unit": "A", "x-display-name": "Current A"},
                "active_power_total": {"type": "number", "x-unit": "W"},
                "power_factor_a": {"type": "number"},
                "ignored": {"type": "number", "x-nested": {"deep": true}}
            }
        });
        let extensions = extensions_from_payload_schema(&schema);
        assert_eq!(
            extensions
                .get("current_a")
                .map(|e| e.get("unit").map(String::as_str)),
            Some(Some("A"))
        );
        assert_eq!(
            extensions
                .get("current_a")
                .map(|e| e.get("display-name").map(String::as_str)),
            Some(Some("Current A"))
        );
        assert_eq!(
            extensions
                .get("active_power_total")
                .map(|e| e.get("unit").map(String::as_str)),
            Some(Some("W"))
        );
        assert!(!extensions.contains_key("power_factor_a"));
        // Non-scalar extension values are ignored, leaving no entry at all.
        assert!(!extensions.contains_key("ignored"));
    }

    #[test_log::test]
    fn test_null_value_makes_an_enum_nullable_not_json() {
        let props = BTreeMap::from([
            (
                "named".to_string(),
                json!({"oneOf": [{"const": 1, "title": "ONE"}, {"const": null, "title": "NONE"}]}),
            ),
            (
                "listed".to_string(),
                json!({"type": ["string", "null"], "enum": ["auto", null]}),
            ),
        ]);
        let schema = Schema {
            required: vec!["named".to_string(), "listed".to_string()],
            ..schema_with_properties(props)
        };

        let fields = extract_fields_from_schema(&schema, &document(&json!({})));

        let value = |name: &str, raw: Value| EnumValue {
            name: name.to_string(),
            raw,
        };
        assert_eq!(
            fields["named"],
            FieldDef::nullable(FieldType::Enum(
                "named".to_string(),
                vec![value("ONE", json!(1))]
            ))
        );
        assert_eq!(
            fields["listed"],
            FieldDef::nullable(FieldType::Enum(
                "listed0".to_string(),
                vec![value("AUTO", json!("auto"))]
            ))
        );
    }

    #[test_log::test]
    fn test_non_null_when_required_without_null_arm() {
        let props = BTreeMap::from([
            ("on".to_string(), json!({"type": "boolean"})),
            (
                "setpoint".to_string(),
                json!({"anyOf": [{"type": "number"}, {"type": "null"}]}),
            ),
            ("heading".to_string(), json!({"type": ["number", "null"]})),
            ("note".to_string(), json!({"type": "string"})),
            (
                "untyped_arm".to_string(),
                json!({"anyOf": [{"type": "number"}, {}]}),
            ),
            (
                "mode".to_string(),
                json!({"allOf": [{"$ref": "#/components/schemas/mode"}]}),
            ),
            (
                "nullable_then_number".to_string(),
                json!({"allOf": [{"type": ["number", "null"]}, {"type": "number"}]}),
            ),
            (
                "number_then_nullable".to_string(),
                json!({"allOf": [{"type": "number"}, {"type": ["number", "null"]}]}),
            ),
            (
                "nullable_all_of".to_string(),
                json!({"allOf": [{"type": ["number", "null"]}, {}]}),
            ),
            (
                "alarms".to_string(),
                json!({"type": "array", "items": {"$ref": "#/components/schemas/alarm"}}),
            ),
            (
                "readings".to_string(),
                json!({"type": "array", "items": {"type": ["number", "null"]}}),
            ),
        ]);
        let required = [
            "on",
            "setpoint",
            "heading",
            "untyped_arm",
            "mode",
            "nullable_then_number",
            "number_then_nullable",
            "nullable_all_of",
            "alarms",
            "readings",
        ];
        let schema = Schema {
            required: required.map(String::from).to_vec(),
            ..schema_with_properties(props)
        };
        let doc = document(&json!({
            "mode": {"type": "string", "enum": ["auto", "manual"]},
            "alarm": {
                "type": "object",
                "properties": {"code": {"type": "integer"}, "text": {"type": "string"}},
                "required": ["code"]
            }
        }));

        let fields = extract_fields_from_schema(&schema, &doc);

        let non_null = |name: &str| fields[name].non_null;
        assert!(non_null("on"));
        // Required, but the Spec allows `null`.
        assert!(!non_null("setpoint"));
        assert!(!non_null("heading"));
        // An untyped arm allows `null` too.
        assert!(!non_null("untyped_arm"));
        // Not required, so it may be left out.
        assert!(!non_null("note"));
        assert!(non_null("mode"));
        // An intersection is non-null when any arm rules out `null`, in
        // either order.
        assert!(non_null("nullable_then_number"));
        assert!(non_null("number_then_nullable"));
        assert!(!non_null("nullable_all_of"));
        assert!(non_null("alarms"));
        assert_eq!(
            fields["alarms"].field_type,
            FieldType::List(Box::new(FieldDef::non_null(FieldType::Object(
                "alarm".to_string(),
                Box::new(BTreeMap::from([
                    ("code".to_string(), FieldDef::non_null(FieldType::Int)),
                    ("text".to_string(), FieldDef::nullable(FieldType::String)),
                ]))
            ))))
        );
        assert!(non_null("readings"));
        assert_eq!(
            fields["readings"].field_type,
            FieldType::List(Box::new(FieldDef::nullable(FieldType::Float)))
        );
    }
}
