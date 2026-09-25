use anyhow::Context;
use serde_json::{Map, Number, Value};

use crate::model::mutations::InvariantDef;
use crate::pyrepr::float_repr;
use crate::schema::Components;

pub const PYTHON_NAME_KEY: &str = "x-python-name";
pub const CLAMP_KEY: &str = "x-clamp";
pub const FIELD_RULES_KEY: &str = "x-field-rules";

/// A model's JSON Schema, validated the way the producer's pydantic model does
/// so rejections carry the same `ValidationError` text.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ModelSchema {
    pub title: String,
    /// Documentation link base appended to each error (`validationErrorUrl`).
    error_url: String,
    fields: Vec<FieldSchema>,
    invariants: Vec<InvariantDef>,
    rules: Vec<FieldRule>,
}

#[derive(Debug, Clone, PartialEq)]
struct FieldSchema {
    key: String,
    python_name: String,
    value: ValueSchema,
}

#[derive(Debug, Clone, PartialEq)]
enum ValueSchema {
    Number(NumberSchema),
    Tuple(TupleSchema),
    Model(Box<ModelSchema>),
    Nullable(Box<ValueSchema>),
    Boolean,
    /// Anything the bridge never writes invalidly (enums, bridge-stamped timestamps).
    Other,
}

#[derive(Debug, Clone, PartialEq, Default)]
struct NumberSchema {
    clamp: Option<Clamp>,
    /// `(kind, bound)` in the order pydantic checks them.
    bounds: Vec<(BoundKind, Number)>,
}

#[derive(Debug, Clone, Copy, PartialEq)]
enum BoundKind {
    Le,
    Lt,
    Ge,
    Gt,
}

impl BoundKind {
    fn violated(self, value: f64, bound: f64) -> bool {
        match self {
            BoundKind::Le => value > bound,
            BoundKind::Lt => value >= bound,
            BoundKind::Ge => value < bound,
            BoundKind::Gt => value <= bound,
        }
    }

    fn error(self, bound: &Number) -> (&'static str, String) {
        let bound = number_repr(bound);
        match self {
            BoundKind::Le => (
                "less_than_equal",
                format!("Input should be less than or equal to {bound}"),
            ),
            BoundKind::Lt => ("less_than", format!("Input should be less than {bound}")),
            BoundKind::Ge => (
                "greater_than_equal",
                format!("Input should be greater than or equal to {bound}"),
            ),
            BoundKind::Gt => (
                "greater_than",
                format!("Input should be greater than {bound}"),
            ),
        }
    }
}

/// `x-clamp`: values in `accept_below..=accept_above` are snapped into
/// `minimum..=maximum`; others are rejected with `error`.
#[derive(Debug, Clone, PartialEq, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
struct Clamp {
    minimum: Option<f64>,
    maximum: Option<f64>,
    accept_below: Option<f64>,
    accept_above: Option<f64>,
    error: String,
}

/// `x-field-rules`: a stamped number's `leaf` must stay within `minimum..=maximum`.
#[derive(Debug, Clone, PartialEq, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
struct FieldRule {
    field: String,
    leaf: String,
    minimum: Option<f64>,
    maximum: Option<f64>,
    error: String,
    input_repr: String,
    input_type: String,
}

#[derive(Debug, Clone, PartialEq)]
struct TupleSchema {
    items: Vec<ValueSchema>,
    max_items: Option<usize>,
}

/// One segment of an error location.
#[derive(Debug, Clone, PartialEq)]
enum Loc {
    Field(String),
    Index(usize),
}

/// One line of a `ValidationError`.
#[derive(Debug, Clone, PartialEq)]
struct LineError {
    loc: Vec<Loc>,
    kind: &'static str,
    message: String,
    input_value: String,
    input_type: String,
}

impl ModelSchema {
    /// Read a model's schema against its document's components.
    pub fn read(schema: &Value, components: Components<'_>) -> anyhow::Result<Self> {
        let resolved = components.deref(schema)?;
        let title = resolved
            .get("title")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_string();
        let mut fields = Vec::new();
        for (key, property) in components.properties(resolved)? {
            let python_name = property
                .get(PYTHON_NAME_KEY)
                .and_then(Value::as_str)
                .unwrap_or(&key)
                .to_string();
            let value = read_value(property, components)
                .with_context(|| format!("model '{title}' field '{key}'"))?;
            fields.push(FieldSchema {
                key,
                python_name,
                value,
            });
        }
        let rules = match resolved.get(FIELD_RULES_KEY) {
            Some(raw) => serde_json::from_value(raw.clone()).context(FIELD_RULES_KEY)?,
            None => Vec::new(),
        };
        Ok(Self {
            title,
            error_url: String::new(),
            fields,
            invariants: components.invariants(resolved)?,
            rules,
        })
    }

    /// The model with the documentation link base its errors carry.
    pub fn with_error_url(mut self, error_url: &str) -> Self {
        self.error_url = error_url.to_string();
        self
    }

    fn field(&self, key: &str) -> Option<&FieldSchema> {
        self.fields.iter().find(|f| f.key == key)
    }

    /// pydantic's `validate_assignment` of `value` to `key`: the coerced value or
    /// the `ValidationError` text.
    pub fn validate_assignment(
        &self,
        object: &Map<String, Value>,
        key: &str,
        value: Value,
    ) -> Result<Value, String> {
        let Some(field) = self.field(key) else {
            return Ok(value);
        };
        let mut errors = Vec::new();
        let loc = vec![Loc::Field(field.python_name.clone())];
        let value = validate_value(&field.value, value, &loc, &mut errors);
        if errors.is_empty() {
            self.check_field_rules(field, &value, &mut errors);
        }
        if errors.is_empty() {
            let mut modified = object.clone();
            modified.insert(key.to_string(), value.clone());
            self.check_invariants(&modified, &mut errors);
        }
        if errors.is_empty() {
            Ok(value)
        } else {
            Err(self.error_text(&errors))
        }
    }

    /// pydantic's model construction from `object`: the coerced object or the
    /// `ValidationError` text.
    pub fn validate_model(&self, object: Map<String, Value>) -> Result<Map<String, Value>, String> {
        let mut errors = Vec::new();
        let coerced = self.validate_fields(object, &[], &mut errors);
        if errors.is_empty() {
            self.check_invariants(&coerced, &mut errors);
        }
        if errors.is_empty() {
            Ok(coerced)
        } else {
            Err(self.error_text(&errors))
        }
    }

    fn validate_fields(
        &self,
        mut object: Map<String, Value>,
        loc: &[Loc],
        errors: &mut Vec<LineError>,
    ) -> Map<String, Value> {
        for field in &self.fields {
            let Some(value) = object.remove(&field.key) else {
                continue;
            };
            let mut field_loc = loc.to_vec();
            field_loc.push(Loc::Field(field.python_name.clone()));
            let before = errors.len();
            let value = validate_value(&field.value, value, &field_loc, errors);
            if errors.len() == before {
                self.check_field_rules_at(field, &value, &field_loc, errors);
            }
            object.insert(field.key.clone(), value);
        }
        // Keep the object's own key order for what is published.
        object
    }

    fn check_field_rules(&self, field: &FieldSchema, value: &Value, errors: &mut Vec<LineError>) {
        let loc = vec![Loc::Field(field.python_name.clone())];
        self.check_field_rules_at(field, value, &loc, errors);
    }

    fn check_field_rules_at(
        &self,
        field: &FieldSchema,
        value: &Value,
        loc: &[Loc],
        errors: &mut Vec<LineError>,
    ) {
        for rule in self.rules.iter().filter(|r| r.field == field.key) {
            let Some(leaf) = value.get(&rule.leaf).and_then(Value::as_f64) else {
                continue;
            };
            let below = rule.minimum.is_some_and(|m| leaf < m);
            let above = rule.maximum.is_some_and(|m| leaf > m);
            if !(below || above) {
                continue;
            }
            let timestamp = value
                .get("TimeStamp")
                .and_then(Value::as_str)
                .map(python_datetime_repr)
                .unwrap_or_default();
            let input_value = rule
                .input_repr
                .replace("{value}", &float_repr(leaf))
                .replace("{timestamp}", &timestamp);
            errors.push(LineError {
                loc: loc.to_vec(),
                kind: "value_error",
                message: format!("Value error, {}", rule.error),
                input_value: truncate_repr(&input_value),
                input_type: rule.input_type.clone(),
            });
        }
    }

    fn check_invariants(&self, object: &Map<String, Value>, errors: &mut Vec<LineError>) {
        if let Some(error) = self.invariants.iter().find_map(|i| i.violation(object)) {
            errors.push(LineError {
                loc: Vec::new(),
                kind: "value_error",
                message: format!("Value error, {error}"),
                input_value: truncate_repr(&self.repr(object)),
                input_type: self.title.clone(),
            });
        }
    }

    /// pydantic's model `repr`: `Title(field=value, ...)`.
    fn repr(&self, object: &Map<String, Value>) -> String {
        let fields: Vec<String> = self
            .fields
            .iter()
            .map(|f| {
                let value = object.get(&f.key).unwrap_or(&Value::Null);
                format!("{}={}", f.python_name, value_repr(&f.value, value))
            })
            .collect();
        format!("{}({})", self.title, fields.join(", "))
    }

    /// The `ValidationError` text for `errors`.
    fn error_text(&self, errors: &[LineError]) -> String {
        let plural = if errors.len() == 1 { "" } else { "s" };
        let mut lines = vec![format!(
            "{} validation error{plural} for {}",
            errors.len(),
            self.title
        )];
        for error in errors {
            if !error.loc.is_empty() {
                lines.push(
                    error
                        .loc
                        .iter()
                        .map(|segment| match segment {
                            Loc::Field(name) => name.clone(),
                            Loc::Index(i) => i.to_string(),
                        })
                        .collect::<Vec<_>>()
                        .join("."),
                );
            }
            lines.push(format!(
                "  {} [type={}, input_value={}, input_type={}]",
                error.message, error.kind, error.input_value, error.input_type
            ));
            lines.push(format!(
                "    For further information visit {}{}",
                self.error_url, error.kind
            ));
        }
        lines.join("\n")
    }
}

fn read_value(schema: &Value, components: Components<'_>) -> anyhow::Result<ValueSchema> {
    if let Some(any_of) = schema.get("anyOf").and_then(Value::as_array) {
        let is_null = |s: &Value| s.get("type").and_then(Value::as_str) == Some("null");
        let others: Vec<&Value> = any_of.iter().filter(|s| !is_null(s)).collect();
        if let [only] = others.as_slice() {
            let inner = read_value(only, components)?;
            return Ok(if any_of.iter().any(is_null) {
                ValueSchema::Nullable(Box::new(inner))
            } else {
                inner
            });
        }
        return Ok(ValueSchema::Other);
    }
    let resolved = components.deref(schema)?;
    if resolved.get("enum").is_some() {
        return Ok(ValueSchema::Other);
    }
    if resolved.get("properties").is_some() {
        return Ok(ValueSchema::Model(Box::new(ModelSchema::read(
            schema, components,
        )?)));
    }
    match resolved.get("type").and_then(Value::as_str) {
        Some("number") | Some("integer") => {
            let mut number = NumberSchema::default();
            // A clamp may sit on the property or on the schema it references.
            let clamp = schema.get(CLAMP_KEY).or_else(|| resolved.get(CLAMP_KEY));
            if let Some(clamp) = clamp {
                number.clamp = Some(serde_json::from_value(clamp.clone()).context(CLAMP_KEY)?);
            }
            for (kind, keys) in [
                (BoundKind::Le, ["le", "maximum"]),
                (BoundKind::Lt, ["lt", "exclusiveMaximum"]),
                (BoundKind::Ge, ["ge", "minimum"]),
                (BoundKind::Gt, ["gt", "exclusiveMinimum"]),
            ] {
                for key in keys {
                    let bound = schema
                        .get(key)
                        .or_else(|| resolved.get(key))
                        .and_then(Value::as_number);
                    if let Some(bound) = bound {
                        number.bounds.push((kind, bound.clone()));
                    }
                }
            }
            Ok(ValueSchema::Number(number))
        }
        Some("boolean") => Ok(ValueSchema::Boolean),
        Some("array") if resolved.get("prefixItems").is_some() => {
            let items = resolved
                .get("prefixItems")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .map(|item| read_value(item, components))
                .collect::<anyhow::Result<Vec<_>>>()?;
            Ok(ValueSchema::Tuple(TupleSchema {
                items,
                max_items: resolved
                    .get("maxItems")
                    .and_then(Value::as_u64)
                    .map(|n| n as usize),
            }))
        }
        _ => Ok(ValueSchema::Other),
    }
}

/// Validate (and coerce) one value, collecting pydantic's line errors.
fn validate_value(
    schema: &ValueSchema,
    value: Value,
    loc: &[Loc],
    errors: &mut Vec<LineError>,
) -> Value {
    match schema {
        ValueSchema::Nullable(_) if value.is_null() => value,
        ValueSchema::Nullable(inner) => validate_value(inner, value, loc, errors),
        ValueSchema::Number(number) => {
            let Some(x) = value.as_f64() else {
                return value;
            };
            // Only a snapped number is rewritten.
            match validate_number(number, x, loc, errors) {
                Some(coerced) if coerced != x => Value::from(coerced),
                _ => value,
            }
        }
        ValueSchema::Tuple(tuple) => {
            let Value::Array(items) = &value else {
                return value;
            };
            let input_value = truncate_repr(&list_repr(items));
            if let Some(max) = tuple.max_items {
                if items.len() > max {
                    errors.push(LineError {
                        loc: loc.to_vec(),
                        kind: "too_long",
                        message: format!(
                            "Tuple should have at most {max} items after validation, not {}",
                            items.len()
                        ),
                        input_value,
                        input_type: "list".into(),
                    });
                    return value;
                }
            }
            let mut coerced = Vec::with_capacity(tuple.items.len());
            for (index, item_schema) in tuple.items.iter().enumerate() {
                let mut item_loc = loc.to_vec();
                item_loc.push(Loc::Index(index));
                match items.get(index) {
                    Some(item) => {
                        coerced.push(validate_value(item_schema, item.clone(), &item_loc, errors))
                    }
                    None => errors.push(LineError {
                        loc: item_loc,
                        kind: "missing",
                        message: "Field required".into(),
                        input_value: input_value.clone(),
                        input_type: "list".into(),
                    }),
                }
            }
            Value::Array(coerced)
        }
        ValueSchema::Model(model) => match value {
            Value::Object(map) => Value::Object(model.validate_fields(map, loc, errors)),
            other => other,
        },
        ValueSchema::Boolean | ValueSchema::Other => value,
    }
}

/// A number through its clamp, then its bounds; `None` when rejected.
fn validate_number(
    number: &NumberSchema,
    mut x: f64,
    loc: &[Loc],
    errors: &mut Vec<LineError>,
) -> Option<f64> {
    if let Some(clamp) = &number.clamp {
        let rejected =
            clamp.accept_below.is_some_and(|b| x < b) || clamp.accept_above.is_some_and(|a| x > a);
        if rejected {
            errors.push(LineError {
                loc: loc.to_vec(),
                kind: "value_error",
                message: format!(
                    "Value error, {}",
                    clamp.error.replace("{value}", &float_repr(x))
                ),
                input_value: truncate_repr(&float_repr(x)),
                input_type: "float".into(),
            });
            return None;
        }
        if let Some(min) = clamp.minimum.filter(|m| x < *m) {
            x = min;
        }
        if let Some(max) = clamp.maximum.filter(|m| x > *m) {
            x = max;
        }
    }
    for (kind, bound) in &number.bounds {
        if kind.violated(x, bound.as_f64().unwrap_or(f64::NAN)) {
            let (kind, message) = kind.error(bound);
            errors.push(LineError {
                loc: loc.to_vec(),
                kind,
                message,
                input_value: truncate_repr(&float_repr(x)),
                input_type: "float".into(),
            });
            return None;
        }
    }
    Some(x)
}

/// Python's `repr` of a number as pydantic holds it: an integer bound stays
/// an `int`, anything else is a `float`.
fn number_repr(n: &Number) -> String {
    match n.as_i64() {
        Some(i) => i.to_string(),
        None => float_repr(n.as_f64().unwrap_or(f64::NAN)),
    }
}

/// Python's `repr` of a list of floats (a GraphQL `[Float!]` argument).
fn list_repr(items: &[Value]) -> String {
    let parts: Vec<String> = items
        .iter()
        .map(|v| v.as_f64().map(float_repr).unwrap_or_else(|| v.to_string()))
        .collect();
    format!("[{}]", parts.join(", "))
}

/// Python's `repr` of a field value as the pydantic model holds it.
fn value_repr(schema: &ValueSchema, value: &Value) -> String {
    match (schema, value) {
        (_, Value::Null) => "None".into(),
        (ValueSchema::Nullable(inner), v) => value_repr(inner, v),
        (ValueSchema::Number(_), v) => v.as_f64().map(float_repr).unwrap_or_else(|| v.to_string()),
        (ValueSchema::Tuple(tuple), Value::Array(items)) => {
            let parts: Vec<String> = items
                .iter()
                .enumerate()
                .map(|(i, item)| match tuple.items.get(i) {
                    Some(item_schema) => value_repr(item_schema, item),
                    None => item.to_string(),
                })
                .collect();
            if parts.len() == 1 {
                format!("({},)", parts[0])
            } else {
                format!("({})", parts.join(", "))
            }
        }
        (ValueSchema::Model(model), Value::Object(map)) => model.repr(map),
        (_, Value::Bool(b)) => if *b { "True" } else { "False" }.into(),
        (_, Value::String(s)) => crate::pyrepr::str_repr(s),
        (_, Value::Number(n)) => number_repr(n),
        (_, other) => other.to_string(),
    }
}

/// pydantic-core's truncation of a long input: first 25 and last 24 chars.
fn truncate_repr(repr: &str) -> String {
    let chars: Vec<char> = repr.chars().collect();
    if chars.len() <= 50 {
        return repr.to_string();
    }
    let head: String = chars[..25].iter().collect();
    let tail: String = chars[chars.len() - 24..].iter().collect();
    format!("{head}...{tail}")
}

/// Python's `repr` of a UTC `datetime` for an RFC 3339 timestamp.
fn python_datetime_repr(timestamp: &str) -> String {
    let Ok(time) = humantime::parse_rfc3339_weak(timestamp) else {
        return String::new();
    };
    let formatted = humantime::format_rfc3339_micros(time).to_string();
    // YYYY-MM-DDTHH:MM:SS.ffffffZ
    let number = |range: std::ops::Range<usize>| -> u32 {
        formatted
            .get(range)
            .and_then(|s| s.parse().ok())
            .unwrap_or(0)
    };
    let (year, month, day) = (number(0..4), number(5..7), number(8..10));
    let (hour, minute, second, micro) = (
        number(11..13),
        number(14..16),
        number(17..19),
        number(20..26),
    );
    let mut parts = vec![
        year.to_string(),
        month.to_string(),
        day.to_string(),
        hour.to_string(),
        minute.to_string(),
    ];
    if second != 0 || micro != 0 {
        parts.push(second.to_string());
    }
    if micro != 0 {
        parts.push(micro.to_string());
    }
    format!(
        "datetime.datetime({}, tzinfo=datetime.timezone.utc)",
        parts.join(", ")
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    const URL: &str = "https://errors.pydantic.dev/2.13/v/";

    fn components() -> Value {
        json!({"schemas": {
            "Parameters": {"title": "ThrustersParameters", "type": "object", "properties": {
                "MaximumSupplyTemperature": {"type": "number", "minimum": -273.15, "x-python-name": "maximum_supply_temperature"},
                "CoolingTemperature": {"type": "number", "minimum": -273.15, "x-python-name": "cooling_temperature"},
                "WarmupTemperature": {"type": "number", "minimum": -273.15, "x-python-name": "warmup_temperature"},
                "PumpTuning": {"type": "array", "maxItems": 3, "minItems": 3,
                    "prefixItems": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                    "x-python-name": "pump_tuning"},
                "FwdTemperatureTuning": {"type": "array", "maxItems": 3, "minItems": 3,
                    "prefixItems": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                    "x-python-name": "fwd_temperature_tuning"}},
                "x-invariants": [{"lhs": "WarmupTemperature", "op": "ge", "rhs": "CoolingTemperature",
                    "error": "Warmup temperature must be greater than cooling temperature"}]},
            "StampedRatio": {"title": "Stamped[Ratio]", "type": "object", "properties": {
                "Value": {"type": "number", "x-python-name": "value", "x-clamp": {
                    "minimum": 0.0, "maximum": 1.0, "acceptBelow": -9.999999999999999e-05,
                    "acceptAbove": 1.0000999999999998, "error": "Value {value} is outside bounds."}},
                "TimeStamp": {"type": "string", "format": "date-time", "x-python-name": "timestamp"}}},
            "Pump": {"title": "Pump", "type": "object", "properties": {
                "Dutypoint": {"$ref": "#/components/schemas/StampedRatio", "x-python-name": "dutypoint"}},
                "x-field-rules": [{"field": "Dutypoint", "leaf": "Value", "minimum": 0.1,
                    "error": "Pump dutypoint cannot be set < 0.1",
                    "inputRepr": "Stamped(value={value}, timestamp={timestamp})", "inputType": "Stamped"}]},
        }})
    }

    fn model(name: &str) -> ModelSchema {
        let components = components();
        ModelSchema::read(
            &json!({"$ref": format!("#/components/schemas/{name}")}),
            Components::new(Some(&components)),
        )
        .unwrap()
        .with_error_url(URL)
    }

    fn parameters() -> Map<String, Value> {
        json!({"MaximumSupplyTemperature": 75.0, "CoolingTemperature": 38.0, "WarmupTemperature": 60.0,
               "PumpTuning": [0.01, 0.001, 0.0], "FwdTemperatureTuning": [-0.01, -0.001, 0]})
        .as_object()
        .unwrap()
        .clone()
    }

    #[test]
    fn test_bound_violation_reads_like_pydantic() {
        let error = model("Parameters")
            .validate_assignment(&parameters(), "CoolingTemperature", json!(-300.0))
            .unwrap_err();
        assert_eq!(
            error,
            "1 validation error for ThrustersParameters\ncooling_temperature\n  Input should be greater than or equal to -273.15 [type=greater_than_equal, input_value=-300.0, input_type=float]\n    For further information visit https://errors.pydantic.dev/2.13/v/greater_than_equal"
        );
    }

    #[test]
    fn test_tuple_length_errors_read_like_pydantic() {
        let m = model("Parameters");
        let short = m
            .validate_assignment(&parameters(), "PumpTuning", json!([1.0]))
            .unwrap_err();
        assert!(short.starts_with("2 validation errors for ThrustersParameters\npump_tuning.1\n  Field required [type=missing, input_value=[1.0], input_type=list]"), "{short}");
        let long = m
            .validate_assignment(&parameters(), "PumpTuning", json!([1.0, 2.0, 3.0, 4.0]))
            .unwrap_err();
        assert!(long.contains("Tuple should have at most 3 items after validation, not 4 [type=too_long, input_value=[1.0, 2.0, 3.0, 4.0], input_type=list]"), "{long}");
    }

    #[test]
    fn test_invariant_violation_renders_the_truncated_model_repr() {
        let error = model("Parameters")
            .validate_assignment(&parameters(), "WarmupTemperature", json!(1.0))
            .unwrap_err();
        assert_eq!(
            error,
            "1 validation error for ThrustersParameters\n  Value error, Warmup temperature must be greater than cooling temperature [type=value_error, input_value=ThrustersParameters(maxim...ng=(-0.01, -0.001, 0.0)), input_type=ThrustersParameters]\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error"
        );
    }

    #[test]
    fn test_clamp_snaps_close_values_and_rejects_far_ones() {
        let pump = model("Pump");
        let stamped = |v: f64| {
            json!({"Dutypoint": {"Value": v, "TimeStamp": "2026-01-02T03:04:05.678901Z"}})
                .as_object()
                .unwrap()
                .clone()
        };
        let snapped = pump.validate_model(stamped(1.00005)).unwrap();
        assert_eq!(snapped["Dutypoint"]["Value"], json!(1.0));
        let error = pump.validate_model(stamped(5.0)).unwrap_err();
        assert!(error.starts_with("1 validation error for Pump\ndutypoint.value\n  Value error, Value 5.0 is outside bounds. [type=value_error, input_value=5.0, input_type=float]"), "{error}");
    }

    #[test]
    fn test_field_rule_rejects_with_the_stamped_input_repr() {
        let pump = model("Pump");
        let object =
            json!({"Dutypoint": {"Value": 0.05, "TimeStamp": "2026-01-02T03:04:05.678901Z"}})
                .as_object()
                .unwrap()
                .clone();
        assert_eq!(
            pump.validate_model(object).unwrap_err(),
            "1 validation error for Pump\ndutypoint\n  Value error, Pump dutypoint cannot be set < 0.1 [type=value_error, input_value=Stamped(value=0.05, times...=datetime.timezone.utc)), input_type=Stamped]\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error"
        );
    }

    #[test]
    fn test_python_datetime_repr_drops_zero_parts() {
        assert_eq!(
            python_datetime_repr("2026-01-02T03:04:05.678901Z"),
            "datetime.datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=datetime.timezone.utc)"
        );
        assert_eq!(
            python_datetime_repr("2026-01-02T03:04:00Z"),
            "datetime.datetime(2026, 1, 2, 3, 4, tzinfo=datetime.timezone.utc)"
        );
    }
}
