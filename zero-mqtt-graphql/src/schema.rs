use std::collections::BTreeMap;

use anyhow::Context;
use serde::Deserialize;
use serde_json::Value;

use crate::model::mutations::{Bounds, DerivedFieldDef, InvariantDef};

/// Enum member names, aligned with `enum` (the OpenAPI vendor convention).
pub const ENUM_NAMES_KEY: &str = "x-enum-varnames";
pub const INVARIANTS_KEY: &str = "x-invariants";
pub const DERIVED_KEY: &str = "x-derived";

/// `#/components/schemas/<name>` -> `<name>`.
pub fn schema_ref_name(reference: &str) -> Option<&str> {
    reference.strip_prefix("#/components/schemas/")
}

/// A payload schema's `$ref` target, or `None` when it is inline.
pub fn schema_ref(schema: &Value) -> Option<&str> {
    schema.get("$ref").and_then(Value::as_str)
}

/// Resolves `$ref`s against one document's `components`.
#[derive(Debug, Clone, Copy)]
pub struct Components<'a> {
    components: Option<&'a Value>,
}

impl<'a> Components<'a> {
    pub fn new(components: Option<&'a Value>) -> Self {
        Self { components }
    }

    /// Follow a `$ref` once; an inline schema is returned as-is.
    pub fn deref<'s>(&self, schema: &'s Value) -> anyhow::Result<&'s Value>
    where
        'a: 's,
    {
        let Some(reference) = schema_ref(schema) else {
            return Ok(schema);
        };
        let name = schema_ref_name(reference)
            .with_context(|| format!("unsupported schema reference '{reference}'"))?;
        self.components
            .and_then(|c| c.get("schemas"))
            .and_then(|s| s.get(name))
            .with_context(|| format!("schema reference '{reference}' does not resolve"))
    }

    /// The properties of an object schema (after `$ref`), in document order.
    pub fn properties<'s>(&self, schema: &'s Value) -> anyhow::Result<Vec<(String, &'s Value)>>
    where
        'a: 's,
    {
        let schema = self.deref(schema)?;
        Ok(schema
            .get("properties")
            .and_then(Value::as_object)
            .map(|p| p.iter().map(|(k, v)| (k.clone(), v)).collect())
            .unwrap_or_default())
    }

    /// The non-null subschema of a property and whether it is nullable.
    fn unwrap_nullable<'s>(&self, schema: &'s Value) -> (&'s Value, bool)
    where
        'a: 's,
    {
        let Some(any_of) = schema.get("anyOf").and_then(Value::as_array) else {
            return (schema, false);
        };
        let is_null = |s: &Value| s.get("type").and_then(Value::as_str) == Some("null");
        let nullable = any_of.iter().any(is_null);
        let others: Vec<&Value> = any_of.iter().filter(|s| !is_null(s)).collect();
        match others.as_slice() {
            [only] => (only, nullable),
            _ => (schema, nullable),
        }
    }

    /// Classify one property of an object schema.
    pub fn property<'s>(&self, schema: &'s Value) -> anyhow::Result<Property>
    where
        'a: 's,
    {
        let (inner, nullable) = self.unwrap_nullable(schema);
        let resolved = self.deref(inner)?;
        let default = schema.get("default").cloned();
        if let Some(value) = stamped_value(resolved) {
            let (value, value_nullable) = self.unwrap_nullable(value);
            let value = self.deref(value)?;
            return Ok(Property::Stamped(StampedLeaf {
                r#type: scalar_type(value)
                    .with_context(|| format!("unsupported stamped value schema {value}"))?,
                r#enum: enum_of(value)?,
                optional: nullable || value_nullable,
                default,
            }));
        }
        if let Some(r#type) = scalar_type(resolved) {
            return Ok(Property::Scalar(ScalarField {
                r#type,
                r#enum: enum_of(resolved)?,
                optional: nullable,
                bounds: bounds_of(resolved),
                default,
            }));
        }
        if resolved.get("properties").is_some() {
            return Ok(Property::Object(ObjectField {
                reference: schema_ref(inner).map(str::to_string),
                title: resolved
                    .get("title")
                    .and_then(Value::as_str)
                    .map(str::to_string),
                optional: nullable,
            }));
        }
        anyhow::bail!("unsupported property schema {schema}")
    }

    /// The `x-invariants` a schema declares.
    pub fn invariants(&self, schema: &Value) -> anyhow::Result<Vec<InvariantDef>> {
        self.extension(schema, INVARIANTS_KEY)
    }

    /// The `x-derived` fields a schema declares.
    pub fn derived(&self, schema: &Value) -> anyhow::Result<Vec<DerivedFieldDef>> {
        self.extension(schema, DERIVED_KEY)
    }

    fn extension<T: for<'de> Deserialize<'de>>(
        &self,
        schema: &Value,
        key: &str,
    ) -> anyhow::Result<Vec<T>> {
        let schema = self.deref(schema)?;
        match schema.get(key) {
            Some(raw) => serde_json::from_value(raw.clone()).with_context(|| key.to_string()),
            None => Ok(Vec::new()),
        }
    }
}

/// What one property of a payload object is.
#[derive(Debug, Clone, PartialEq)]
pub enum Property {
    /// A `{Value, TimeStamp}` envelope around a scalar.
    Stamped(StampedLeaf),
    /// A bare scalar (or a list of scalars).
    Scalar(ScalarField),
    /// A nested object, named by its `$ref` (or its `title` when inline).
    Object(ObjectField),
}

#[derive(Debug, Clone, PartialEq)]
pub struct StampedLeaf {
    pub r#type: String,
    pub r#enum: Option<EnumDef>,
    pub optional: bool,
    /// The property's wire-shaped default (`{"Value": ..., "TimeStamp": ...}`).
    pub default: Option<Value>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ScalarField {
    pub r#type: String,
    pub r#enum: Option<EnumDef>,
    pub optional: bool,
    pub bounds: Option<Bounds>,
    pub default: Option<Value>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ObjectField {
    pub reference: Option<String>,
    pub title: Option<String>,
    pub optional: bool,
}

/// An enum schema: its GraphQL type name (the schema `title`) and the wire
/// value -> member name map.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EnumDef {
    pub name: String,
    pub values: BTreeMap<String, String>,
}

/// The `Value` subschema of a `{Value, TimeStamp}` envelope, if `schema` is one.
fn stamped_value(schema: &Value) -> Option<&Value> {
    let properties = schema.get("properties")?.as_object()?;
    if properties.len() != 2 || !properties.contains_key("TimeStamp") {
        return None;
    }
    properties.get("Value")
}

/// The GraphQL scalar for a JSON Schema scalar (or list); enums map to `String`.
pub fn scalar_type(schema: &Value) -> Option<String> {
    if schema.get(ENUM_NAMES_KEY).is_some() {
        return Some("String".to_string());
    }
    match schema.get("type").and_then(Value::as_str)? {
        "number" => Some("Float".to_string()),
        "integer" => Some("Int".to_string()),
        "boolean" => Some("Boolean".to_string()),
        "string" if schema.get("format").and_then(Value::as_str) == Some("date-time") => {
            Some("DateTime".to_string())
        }
        "string" => Some("String".to_string()),
        "array" => {
            let item = schema
                .get("prefixItems")
                .and_then(Value::as_array)
                .and_then(|items| items.first())
                .or_else(|| schema.get("items"))?;
            let inner = scalar_type(item)?;
            Some(format!("[{inner}!]"))
        }
        _ => None,
    }
}

/// The GraphQL enum a schema declares via `title` and `x-enum-varnames`;
/// `None` for plain-string enums, which are served as-is.
pub fn enum_of(schema: &Value) -> anyhow::Result<Option<EnumDef>> {
    let (Some(values), Some(names)) = (
        schema.get("enum").and_then(Value::as_array),
        schema.get(ENUM_NAMES_KEY).and_then(Value::as_array),
    ) else {
        return Ok(None);
    };
    let name = schema
        .get("title")
        .and_then(Value::as_str)
        .context("enum schema has no title")?;
    if names.len() != values.len() {
        anyhow::bail!(
            "enum '{name}' has {} values but {} {ENUM_NAMES_KEY}",
            values.len(),
            names.len()
        );
    }
    let values = values
        .iter()
        .zip(names)
        .map(|(value, member)| {
            let member = member
                .as_str()
                .with_context(|| format!("enum '{name}': member name {member} is not a string"))?;
            Ok((wire_key_of(value), member.to_string()))
        })
        .collect::<anyhow::Result<BTreeMap<_, _>>>()?;
    Ok(Some(EnumDef {
        name: name.to_string(),
        values,
    }))
}

/// The map key for a wire enum value (`0` -> `"0"`).
fn wire_key_of(value: &Value) -> String {
    match value {
        Value::String(s) => s.clone(),
        other => other.to_string(),
    }
}

/// The numeric bounds a scalar schema carries, if any.
pub fn bounds_of(schema: &Value) -> Option<Bounds> {
    let number = |key: &str| schema.get(key).and_then(Value::as_f64);
    let bounds = Bounds {
        min: number("minimum"),
        max: number("maximum"),
        exclusive_min: number("exclusiveMinimum"),
        exclusive_max: number("exclusiveMaximum"),
    };
    (bounds != Bounds::default()).then_some(bounds)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn components() -> Value {
        json!({"schemas": {
            "Mode": {"title": "Mode", "type": "integer", "enum": [0, 1],
                     "x-enum-varnames": ["OFF", "ON"]},
            "StampedFloat": {"type": "object", "title": "Stamped[float]",
                "properties": {"Value": {"type": "number", "minimum": 0},
                               "TimeStamp": {"type": "string", "format": "date-time"}},
                "required": ["Value", "TimeStamp"]},
            "StampedMode": {"type": "object",
                "properties": {"Value": {"anyOf": [{"$ref": "#/components/schemas/Mode"}, {"type": "null"}]},
                               "TimeStamp": {"type": "string"}}},
            "Pump": {"type": "object", "title": "Pump",
                "properties": {
                    "Dutypoint": {"$ref": "#/components/schemas/StampedFloat"},
                    "ControlMode": {"$ref": "#/components/schemas/StampedMode",
                                    "default": {"Value": null, "TimeStamp": "1970-01-01T00:00:00Z"}}}},
            "Values": {"type": "object", "title": "Values",
                "properties": {
                    "Pump": {"$ref": "#/components/schemas/Pump"},
                    "Spare": {"anyOf": [{"$ref": "#/components/schemas/Pump"}, {"type": "null"}]},
                    "Tuning": {"type": "array", "prefixItems": [{"type": "number"}], "default": [1.0]},
                    "Level": {"anyOf": [{"type": "number", "maximum": 1}, {"type": "null"}]}},
                "x-invariants": [{"lhs": "A", "op": "lt", "rhs": "B", "error": "A before B"}]}
        }})
    }

    #[test]
    fn test_classifies_every_property_kind() {
        let components = components();
        let c = Components::new(Some(&components));
        let values = json!({"$ref": "#/components/schemas/Values"});
        let properties = c.properties(&values).unwrap();
        let by_key: BTreeMap<String, Property> = properties
            .into_iter()
            .map(|(k, s)| (k, c.property(s).unwrap()))
            .collect();

        assert_eq!(
            by_key["Pump"],
            Property::Object(ObjectField {
                reference: Some("#/components/schemas/Pump".into()),
                title: Some("Pump".into()),
                optional: false
            })
        );
        assert!(matches!(&by_key["Spare"], Property::Object(o) if o.optional));
        assert_eq!(
            by_key["Tuning"],
            Property::Scalar(ScalarField {
                r#type: "[Float!]".into(),
                r#enum: None,
                optional: false,
                bounds: None,
                default: Some(json!([1.0]))
            })
        );
        assert_eq!(
            by_key["Level"],
            Property::Scalar(ScalarField {
                r#type: "Float".into(),
                r#enum: None,
                optional: true,
                bounds: Some(Bounds {
                    max: Some(1.0),
                    ..Bounds::default()
                }),
                default: None
            })
        );

        let pump = json!({"$ref": "#/components/schemas/Pump"});
        let leaves: BTreeMap<String, Property> = c
            .properties(&pump)
            .unwrap()
            .into_iter()
            .map(|(k, s)| (k, c.property(s).unwrap()))
            .collect();
        assert_eq!(
            leaves["Dutypoint"],
            Property::Stamped(StampedLeaf {
                r#type: "Float".into(),
                r#enum: None,
                optional: false,
                default: None
            })
        );
        assert_eq!(
            leaves["ControlMode"],
            Property::Stamped(StampedLeaf {
                r#type: "String".into(),
                r#enum: Some(EnumDef {
                    name: "Mode".into(),
                    values: BTreeMap::from([("0".into(), "OFF".into()), ("1".into(), "ON".into())])
                }),
                optional: true,
                default: Some(json!({"Value": null, "TimeStamp": "1970-01-01T00:00:00Z"}))
            })
        );
        assert_eq!(c.invariants(&values).unwrap().len(), 1);
        assert!(c.derived(&values).unwrap().is_empty());
    }

    #[test]
    fn test_enum_without_names_is_a_plain_string_and_dangling_ref_an_error() {
        let components = json!({"schemas": {
            "E": {"title": "E", "type": "string", "enum": ["a", "b"]},
            "F": {"title": "F", "enum": [1, 2], "x-enum-varnames": ["ONE"]}}});
        let c = Components::new(Some(&components));
        let plain = c
            .property(&json!({"$ref": "#/components/schemas/E"}))
            .unwrap();
        assert!(matches!(
            plain,
            Property::Scalar(ScalarField { r#enum: None, .. })
        ));
        let err = c
            .property(&json!({"$ref": "#/components/schemas/F"}))
            .unwrap_err();
        assert!(format!("{err:#}").contains(ENUM_NAMES_KEY), "{err:#}");
        let err = c
            .deref(&json!({"$ref": "#/components/schemas/Nope"}))
            .unwrap_err();
        assert!(format!("{err:#}").contains("does not resolve"), "{err:#}");
    }
}
