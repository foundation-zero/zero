//! Payload fields and field attributes from a message's JSON Schema.

use std::collections::BTreeMap;

use log::{info, warn};
use roas_asyncapi::common::reference::RefOr;
use serde_json::Value;

use super::refs::{resolve_message, resolve_payload_schema, resolve_ref_to_entry};
use super::roas::{Channel, Document, Message, Schema, SchemaOrMultiFormat, SchemaType, SubSchema};
use crate::api_model::{FieldType, Payload};

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

    let Some((pointer, schema_or_multi)) = resolve_payload_schema(payload_ref, doc) else {
        info!("Channel {channel_ref} message payload reference does not resolve");
        return None;
    };

    let schema_ref = pointer.unwrap_or(format!("{message_ref}/payload"));
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
            let (resolved, message) = resolve_message(message_ref, doc)?;
            let pointer = resolved.unwrap_or_else(|| {
                let key = message_key.replace('~', "~0").replace('/', "~1");
                format!("{channel_ref}/messages/{key}")
            });
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
) -> BTreeMap<String, FieldType> {
    let schema_entries = doc
        .components
        .as_ref()
        .map(|componentens| &componentens.schemas);

    match schema_or_multi {
        SchemaOrMultiFormat::Schema(schema) => extract_fields_from_schema(schema, schema_entries),
        SchemaOrMultiFormat::MultiFormat(mf) => {
            // Try to deserialize the raw schema value as a Schema
            if let Ok(schema) = serde_json::from_value::<Schema>(mf.schema.clone()) {
                extract_fields_from_schema(&schema, schema_entries)
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

fn extract_fields_from_schema(
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> BTreeMap<String, FieldType> {
    // Fields colliding after lowerCamel sanitization are kept here; building
    // the schema then stops at the duplicate field.
    schema
        .properties
        .iter()
        .filter_map(|(name, subschema)| {
            let field_type = field_type_for_subschema(name.clone(), subschema, schema_entries)?;

            Some((name.clone(), field_type))
        })
        .collect()
}

/// Derive a field type from a (possibly `$ref`'d) subschema.
fn field_type_for_subschema(
    name: String,
    sub: &SubSchema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    match sub {
        SubSchema::Bool(_) => None,
        SubSchema::Schema(boxed) => match boxed.as_ref() {
            RefOr::Item(schema) => type_from_schema(name, schema, schema_entries),
            RefOr::Reference(r) => {
                let Some((reference, resolved)) =
                    resolve_ref_to_entry(r, None, schema_entries, vec![])
                else {
                    warn!("Cannot resolve reference {r:?} while determining payload type");
                    return None;
                };
                let name = reference
                    .and_then(|r| r.rsplit('/').next().map(ToOwned::to_owned))
                    .unwrap_or(name);

                match resolved {
                    SchemaOrMultiFormat::Schema(s) => type_from_schema(name, s, schema_entries),
                    SchemaOrMultiFormat::MultiFormat(mf) => {
                        let schema: Schema = serde_json::from_value(mf.schema.clone()).ok()?;
                        type_from_schema(name, &schema, schema_entries)
                    }
                    SchemaOrMultiFormat::Bool(_) => None,
                }
            }
        },
    }
}

fn type_from_schema(
    name: String,
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    if let Some(schema_type) = &schema.schema_type {
        return match schema_type {
            SchemaType::Single(t) => field_type_for_json_type(name, t, schema, schema_entries),
            SchemaType::Multiple(types) => {
                for (index, t) in types.iter().enumerate() {
                    if t == "null" {
                        continue;
                    }
                    if let Some(field_type) = field_type_for_json_type(
                        format!("{name}{index}"),
                        t,
                        schema,
                        schema_entries,
                    ) {
                        // TODO: properly handle unions here
                        return Some(field_type);
                    }
                }
                None
            }
        };
    }

    // Handle nullable via anyOf / oneOf / allOf
    if let Some(any_of) = &schema.any_of {
        for (index, sub) in any_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }
    if let Some(one_of) = &schema.one_of {
        for (index, sub) in one_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }
    if let Some(all_of) = &schema.all_of {
        for (index, sub) in all_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }

    None
}

fn field_type_for_json_type(
    name: String,
    t: &str,
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    match t {
        "object" => {
            let fields = extract_fields_from_schema(schema, schema_entries);
            (!fields.is_empty()).then(|| FieldType::Object(name, Box::new(fields)))
        }
        "number" => Some(FieldType::Float),
        "integer" => Some(FieldType::Int),
        "boolean" => Some(FieldType::Boolean),
        "string" => Some(FieldType::String),
        _ => None,
    }
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

    #[test_log::test]
    fn test_extract_scalar_fields() {
        let props = BTreeMap::from([
            ("celsius".to_string(), json!({"type": "number"})),
            ("sensor_id".to_string(), json!({"type": "integer"})),
            ("ok".to_string(), json!({"type": "boolean"})),
            ("label".to_string(), json!({"type": "string"})),
            (
                "nested".to_string(),
                json!({"type": "object", "properties": {"x": {"type": "number"}}}),
            ),
            ("reffed".to_string(), json!({"$ref": "#/components/nested"})),
            ("items".to_string(), json!({"type": "array"})),
        ]);
        let schema = schema_with_properties(props);
        let schema_entries = BTreeMap::from([(
            "nested".to_string(),
            RefOr::Item(
                serde_json::from_value::<SchemaOrMultiFormat>(
                    json!({"type": "object", "properties": {"x": {"type": "number"}}}),
                )
                .unwrap(),
            ),
        )]);

        let fields = extract_fields_from_schema(&schema, Some(&schema_entries));
        assert_eq!(fields.len(), 6);
        // BTreeMap ordering, so sorted by key
        let get = |name: &str| fields.get(name).unwrap();
        assert_eq!(get("celsius"), &FieldType::Float);
        assert_eq!(get("sensor_id"), &FieldType::Int);
        assert_eq!(get("ok"), &FieldType::Boolean);
        assert_eq!(get("label"), &FieldType::String);
        assert_eq!(
            get("nested"),
            &FieldType::Object(
                "nested".to_string(),
                Box::new(BTreeMap::from([("x".to_string(), FieldType::Float); 1]))
            )
        );
        assert_eq!(
            get("reffed"),
            &FieldType::Object(
                "nested".to_string(),
                Box::new(BTreeMap::from([("x".to_string(), FieldType::Float); 1]))
            )
        );
    }

    #[test_log::test]
    fn test_empty_properties_returns_empty_fields() {
        let schema = Schema::default();
        let fields = extract_fields_from_schema(&schema, None);
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
    fn test_nullable_anyof_field() {
        let props = BTreeMap::from([(
            "current_a".to_string(),
            json!({"anyOf": [{"type": "number"}, {"type": "null"}]}),
        )]);
        let schema = schema_with_properties(props);
        let fields = extract_fields_from_schema(&schema, None);
        assert_eq!(fields.len(), 1);
        assert_eq!(fields.get("current_a"), Some(&FieldType::Float));
    }
}
