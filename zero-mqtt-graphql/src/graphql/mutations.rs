use std::collections::BTreeMap;
use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::time::Duration;

use anyhow::{Context, bail};
use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{
    Field, FieldFuture, FieldValue, InputObject, InputValue, Type, TypeRef,
};
use async_graphql::indexmap::IndexMap;
use jsonschema::Validator;
use log::{info, warn};
use serde_json::{Map, Value as JsonValue};
use tokio::sync::broadcast::{Receiver, error::RecvError};
use tokio::time::Instant;

use crate::api_model::{Direction, FieldType, GraphqlPath, TopicDef};
use crate::cache::TopicCache;
use crate::graphql::{JSON_SCALAR, Leaf, json_to_graphql_value, payload_type_name};
use crate::naming::sanitize_to_graphql_name;

/// A boxed future returned by [`Publisher::publish`].
pub type PublishFuture<'a> = Pin<Box<dyn Future<Output = anyhow::Result<()>> + Send + 'a>>;

/// Publishes Mutation inputs to MQTT.
pub trait Publisher: Send + Sync {
    /// Publish `payload` on `topic` with QoS 1 and no retain.
    fn publish(&self, topic: String, payload: Vec<u8>) -> PublishFuture<'_>;
}

/// What the Mutation tree needs at runtime.
#[derive(Clone)]
pub struct Mutations {
    pub publisher: Arc<dyn Publisher>,
    /// How long a Mutation with a State topic waits for it to show the input.
    pub timeout: Duration,
}

/// The Mutation field that sets `topic` at `path`, if it can be set, plus
/// the input types it takes. The field takes `input` and returns the value
/// of `topic` when it is a State topic, or `Boolean!` when it is an
/// unpaired Receive topic. A payload without fields is a signal, such as a
/// pause: the field takes no input, publishes `{}` and returns `Boolean!`,
/// as there is nothing to confirm. Type names are prefixed with `spec`.
pub(super) fn mutation_leaf(
    spec: &str,
    segment: &str,
    path: &GraphqlPath,
    topic: &TopicDef,
    cache: &Arc<TopicCache>,
    mutations: &Mutations,
) -> Leaf {
    let Some(setter) = &topic.setter else {
        return Leaf::default();
    };
    info!("Building mutation for topic {}", setter.topic);
    if setter.payload.name.is_empty() {
        warn!(
            "Topic {} would create an invalid input type, ignoring",
            setter.topic
        );
        return Leaf::default();
    }

    let signal = setter.payload.fields.is_empty();
    // GraphQL has no input objects without fields.
    let inputs = if signal {
        Vec::new()
    } else {
        input_objects(spec, &setter.payload.name, &setter.payload.fields)
    };
    // A signal has no input, so nothing to confirm. The State topic is a
    // Query field, so Query has already built its object type.
    let state_type = match (topic.operation, &topic.payload) {
        (Direction::Send, Some(state)) if !signal && !state.name.is_empty() => {
            info!("Mutation '{path}' confirms through '{}'", topic.topic);
            Some(payload_type_name(spec, &state.name))
        }
        _ => None,
    };
    let return_type = TypeRef::named_nn(state_type.as_deref().unwrap_or(TypeRef::BOOLEAN));

    let target = Target {
        topic: setter.topic.clone(),
        fields: setter.payload.fields.clone(),
        validator: setter.validator.clone(),
        state_topic: state_type.is_some().then(|| topic.topic.clone()),
        cache: cache.clone(),
        mutations: mutations.clone(),
    };
    let input_type = inputs.first().map(InputObject::type_name);
    let field = set_field(segment, input_type, return_type, target);
    (vec![field], inputs.into_iter().map(Type::from).collect())
}

/// The Mutation field `name`: takes an `input` of `input_type`, if any, sets
/// `target` and returns `return_type`.
fn set_field(name: &str, input_type: Option<&str>, return_type: TypeRef, target: Target) -> Field {
    let target = Arc::new(target);
    let field = Field::new(name, return_type, move |ctx| {
        let target = target.clone();
        FieldFuture::new(async move {
            // A signal has no `input` argument: it sets no fields.
            let input = ctx.args.get("input").map_or_else(
                || GraphQlValue::Object(IndexMap::default()),
                |input| input.as_value().clone(),
            );
            let value = target
                .set(&input)
                .await
                .map_err(|e| async_graphql::Error::new(format!("{e:#}")))?;
            Ok(Some(FieldValue::value(value)))
        })
    });
    match input_type {
        Some(input_type) => field.argument(InputValue::new("input", TypeRef::named_nn(input_type))),
        None => field,
    }
}

/// The `<Payload>Input` type of a Receive Topic, followed by the input
/// types of its nested objects. Every field is optional: with a State topic
/// omitted fields are filled from its value, without one the JSON Schema
/// decides which fields are required.
fn input_objects(spec: &str, name: &str, fields: &BTreeMap<String, FieldType>) -> Vec<InputObject> {
    let type_name = format!("{}Input", payload_type_name(spec, name));
    let mut nested = Vec::new();
    let mut object = InputObject::new(type_name.as_str());
    for (raw_name, field_type) in fields {
        let field_name = sanitize_to_graphql_name(raw_name);
        if field_name.is_empty() {
            warn!("Skipping input field '{raw_name}' sanitizes to empty GraphQL name");
            continue;
        }
        let type_ref = input_type_ref(spec, field_type, &mut nested);
        object = object.field(InputValue::new(field_name, type_ref));
    }
    nested.insert(0, object);
    nested
}

/// The input type of one field, adding the input types of nested objects
/// to `nested`.
fn input_type_ref(spec: &str, field_type: &FieldType, nested: &mut Vec<InputObject>) -> TypeRef {
    match field_type {
        FieldType::Float => TypeRef::named(TypeRef::FLOAT),
        FieldType::Int => TypeRef::named(TypeRef::INT),
        FieldType::Boolean => TypeRef::named(TypeRef::BOOLEAN),
        FieldType::String => TypeRef::named(TypeRef::STRING),
        FieldType::Json => TypeRef::named(JSON_SCALAR),
        FieldType::List(element) => TypeRef::List(Box::new(input_type_ref(spec, element, nested))),
        FieldType::Object(name, fields) => {
            let objects = input_objects(spec, name, fields);
            let type_ref = TypeRef::named(objects[0].type_name());
            nested.extend(objects);
            type_ref
        }
    }
}

/// One mutable Receive Topic, as its resolver needs it.
struct Target {
    topic: String,
    fields: BTreeMap<String, FieldType>,
    validator: Validator,
    state_topic: Option<String>,
    cache: Arc<TopicCache>,
    mutations: Mutations,
}

impl Target {
    /// Publish `input`. Without a State topic, returns `true` once handed to
    /// the MQTT client. With one, fills omitted fields from the State value
    /// first (see [`merge`]), then returns the first State value that shows
    /// every given leaf.
    async fn set(&self, input: &GraphQlValue) -> anyhow::Result<GraphQlValue> {
        let given = input_payload(input, &self.fields)?;
        let Some(state_topic) = &self.state_topic else {
            self.publish(&given).await?;
            return Ok(GraphQlValue::Boolean(true));
        };
        if given.as_object().is_none_or(Map::is_empty) {
            bail!("input for '{}' sets no fields", self.topic);
        }

        // Listen before publishing, so the confirming update can't be missed.
        let mut updates = self.cache.updates();
        let base = self.cache.get(state_topic).map_or_else(
            || JsonValue::Object(Map::new()),
            |state| project(&state, &self.fields),
        );
        self.publish(&merge(base, &given)).await?;

        let deadline = Instant::now() + self.mutations.timeout;
        loop {
            if let Some(state) = self.cache.get(state_topic)
                && shows(&state, &given)
            {
                return Ok(json_to_graphql_value(&state));
            }
            if !next_update(&mut updates, state_topic, deadline).await {
                bail!(
                    "published to '{}', but '{state_topic}' did not show the input within {:?}",
                    self.topic,
                    self.mutations.timeout
                );
            }
        }
    }

    /// Validate `payload` against the topic's JSON Schema, then publish it.
    async fn publish(&self, payload: &JsonValue) -> anyhow::Result<()> {
        let errors: Vec<String> = self
            .validator
            .iter_errors(payload)
            .map(|e| format!("{}: {e}", e.instance_path()))
            .collect();
        if !errors.is_empty() {
            bail!(
                "input for '{}' does not match its schema: {}",
                self.topic,
                errors.join("; ")
            );
        }
        info!("Publishing mutation on '{}': {payload}", self.topic);
        self.mutations
            .publisher
            .publish(self.topic.clone(), serde_json::to_vec(payload)?)
            .await
            .with_context(|| format!("publishing to '{}'", self.topic))
    }
}

/// Wait until `topic` is updated or updates were missed; `false` once
/// `deadline` passes first.
async fn next_update(updates: &mut Receiver<String>, topic: &str, deadline: Instant) -> bool {
    loop {
        match tokio::time::timeout_at(deadline, updates.recv()).await {
            Ok(Ok(other_topic)) if other_topic != topic => {}
            Ok(Ok(_) | Err(RecvError::Lagged(_))) => return true,
            Ok(Err(RecvError::Closed)) | Err(_) => return false,
        }
    }
}

/// The client-given input as a payload keyed by raw field names. Omitted
/// fields stay out; explicit nulls are kept.
fn input_payload(
    input: &GraphQlValue,
    fields: &BTreeMap<String, FieldType>,
) -> anyhow::Result<JsonValue> {
    let GraphQlValue::Object(input) = input else {
        bail!("input is not an object");
    };
    fields
        .iter()
        .filter_map(|(raw_name, field_type)| {
            let value = input.get(sanitize_to_graphql_name(raw_name).as_str())?;
            Some(input_json(field_type, value).map(|json| (raw_name.clone(), json)))
        })
        .collect::<anyhow::Result<Map<_, _>>>()
        .map(JsonValue::Object)
}

/// One client-given value as JSON, with objects, also inside lists, keyed
/// by raw field names.
fn input_json(field_type: &FieldType, value: &GraphQlValue) -> anyhow::Result<JsonValue> {
    match (field_type, value) {
        (FieldType::Object(_, nested), GraphQlValue::Object(_)) => input_payload(value, nested),
        (FieldType::List(element), GraphQlValue::List(items)) => items
            .iter()
            .map(|item| input_json(element, item))
            .collect::<anyhow::Result<Vec<_>>>()
            .map(JsonValue::Array),
        _ => value.clone().into_json().map_err(Into::into),
    }
}

/// The part of a State value that the Receive Topic's `fields` describe,
/// leaving out read-only State fields and the keys the cache flattened in.
fn project(state: &JsonValue, fields: &BTreeMap<String, FieldType>) -> JsonValue {
    let JsonValue::Object(state) = state else {
        return JsonValue::Object(Map::new());
    };
    fields
        .iter()
        .filter_map(|(raw_name, graphql_type)| {
            let value = state.get(raw_name)?;
            let projected = match (graphql_type, value) {
                (FieldType::Object(_, nested), JsonValue::Object(_)) => project(value, nested),
                _ => value.clone(),
            };
            Some((raw_name.clone(), projected))
        })
        .collect::<Map<_, _>>()
        .into()
}

/// `given` merged over the State value `base`, filling what the client left
/// out. At the root every omitted field is filled. Inside an object the
/// client wrote into, only omitted objects are filled, whole; omitted
/// scalars are not. So `{"pump": {"dutypoint": {"Value": 0.3}}}` keeps the
/// pump's other settings, but never a stale `TimeStamp` beside the new
/// `Value`: a value is replaced as a whole.
fn merge(base: JsonValue, given: &JsonValue) -> JsonValue {
    merge_level(base, given, true)
}

fn merge_level(base: JsonValue, given: &JsonValue, root: bool) -> JsonValue {
    match (base, given) {
        (JsonValue::Object(base), JsonValue::Object(given)) => {
            let mut merged: Map<String, JsonValue> = base
                .into_iter()
                .filter(|(_, value)| root || value.is_object())
                .collect();
            for (key, value) in given {
                let base = merged.remove(key).unwrap_or(JsonValue::Null);
                merged.insert(key.clone(), merge_level(base, value, false));
            }
            JsonValue::Object(merged)
        }
        (_, given) => given.clone(),
    }
}

/// Whether `state` shows every leaf of `given`. Numbers compare by value, so
/// `21` and `21.0` match, but a rounded or clamped value does not. A list
/// matches element by element, at the same length.
#[allow(clippy::float_cmp)]
fn shows(state: &JsonValue, given: &JsonValue) -> bool {
    match (state, given) {
        (_, JsonValue::Object(given)) => given
            .iter()
            .all(|(key, value)| state.get(key).is_some_and(|state| shows(state, value))),
        (JsonValue::Array(state), JsonValue::Array(given)) => {
            state.len() == given.len()
                && state
                    .iter()
                    .zip(given)
                    .all(|(state, given)| shows(state, given))
        }
        (JsonValue::Number(state), JsonValue::Number(given)) => state.as_f64() == given.as_f64(),
        _ => state == given,
    }
}

#[cfg(test)]
mod tests {
    use std::sync::Mutex;

    use serde_json::json;

    use super::*;
    use crate::api_model::{Api, Payload, SET_SUFFIX, Spec, TopicKind};
    use crate::graphql::build_schema;

    /// A service on the other side of MQTT: records what is published and,
    /// when given a reply, publishes the resulting State like a real service.
    struct Service {
        cache: Arc<TopicCache>,
        published: Mutex<Vec<(String, JsonValue)>>,
        reply: Option<fn(&JsonValue) -> JsonValue>,
    }

    impl Publisher for Service {
        fn publish(&self, topic: String, payload: Vec<u8>) -> PublishFuture<'_> {
            let payload: JsonValue = serde_json::from_slice(&payload).unwrap();
            if let Some(reply) = self.reply {
                let state_topic = topic.strip_suffix(SET_SUFFIX).unwrap_or(&topic);
                self.cache.insert(state_topic, reply(&payload));
            }
            self.published.lock().unwrap().push((topic, payload));
            Box::pin(async { Ok(()) })
        }
    }

    fn topic(address: &str, operation: Direction, fields: &[(&str, FieldType)]) -> TopicDef {
        TopicDef {
            topic: address.to_string(),
            payload: Some(Payload {
                name: address.replace('/', "-"),
                fields: fields
                    .iter()
                    .map(|(name, field_type)| ((*name).to_string(), field_type.clone()))
                    .collect(),
            }),
            ttl_secs: None,
            operation,
            setter: None,
            kind: TopicKind::Single,
        }
    }

    /// A stamped value, `{Value, TimeStamp}`, as THRS publishes them.
    fn stamped(name: &str, value: FieldType) -> FieldType {
        FieldType::Object(
            name.to_string(),
            Box::new(BTreeMap::from([
                ("Value".to_string(), value),
                ("TimeStamp".to_string(), FieldType::String),
            ])),
        )
    }

    /// A thermostat whose State topic reports its setpoint, mode and
    /// measured temperature, a light without a State topic, a pump whose
    /// settings are stamped values, a pause signal without a payload, and a
    /// heater with list settings.
    fn api() -> Api {
        let thermostat_schema = json!({
            "type": "object",
            "properties": {
                "setpoint": {"type": "number", "maximum": 30},
                "mode": {"type": "string"},
            },
            "required": ["setpoint", "mode"],
            "additionalProperties": false,
        });
        let light_schema = json!({
            "type": "object",
            "properties": {"on": {"type": "boolean"}},
            "required": ["on"],
        });
        let stamped_schema = |value_type: &str| {
            json!({
                "type": "object",
                "properties": {"Value": {"type": value_type}, "TimeStamp": {"type": "string"}},
                "required": ["Value", "TimeStamp"],
            })
        };
        let pump_schema = json!({
            "type": "object",
            "properties": {
                "dutypoint": stamped_schema("number"),
                "on": stamped_schema("boolean"),
            },
            "required": ["dutypoint", "on"],
        });
        let validators = [
            ("room/thermostat/set", thermostat_schema),
            ("room/light/set", light_schema),
            ("room/pump/set", pump_schema),
            (
                "room/pause",
                json!({"type": "object", "properties": {}, "additionalProperties": false}),
            ),
            (
                "room/heater/set",
                json!({
                    "type": "object",
                    "properties": {
                        "tuning": {
                            "type": "array",
                            "prefixItems": [{"type": "number"}, {"type": "number"}, {"type": "number"}],
                            "minItems": 3,
                            "maxItems": 3,
                        },
                        "curve": {"type": "array", "items": {"type": "number"}},
                    },
                    "required": ["tuning", "curve"],
                }),
            ),
        ]
        .into_iter()
        .map(|(topic, schema)| {
            (
                topic.to_string(),
                jsonschema::validator_for(&schema).unwrap(),
            )
        })
        .collect();
        Api::new(vec![
            Spec::new(
                "room".to_string(),
                vec![
                    topic(
                        "room/thermostat",
                        Direction::Send,
                        &[
                            ("setpoint", FieldType::Float),
                            ("mode", FieldType::String),
                            ("measured", FieldType::Float),
                        ],
                    ),
                    topic(
                        "room/thermostat/set",
                        Direction::Receive,
                        &[("setpoint", FieldType::Float), ("mode", FieldType::String)],
                    ),
                    topic(
                        "room/light/set",
                        Direction::Receive,
                        &[("on", FieldType::Boolean)],
                    ),
                    topic("room/pump", Direction::Send, &pump_fields()),
                    topic("room/pump/set", Direction::Receive, &pump_fields()),
                    topic("room/pause", Direction::Receive, &[]),
                    topic("room/heater", Direction::Send, &heater_fields()),
                    topic("room/heater/set", Direction::Receive, &heater_fields()),
                ],
                validators,
            )
            .unwrap(),
        ])
    }

    fn pump_fields() -> [(&'static str, FieldType); 2] {
        [
            ("dutypoint", stamped("StampedFloat", FieldType::Float)),
            ("on", stamped("StampedBool", FieldType::Boolean)),
        ]
    }

    /// A heater with a PID tuning whose element type is unknown, as a
    /// `prefixItems` tuple, and a curve declared as a list of numbers.
    fn heater_fields() -> [(&'static str, FieldType); 2] {
        [
            ("tuning", FieldType::Json),
            ("curve", FieldType::List(Box::new(FieldType::Float))),
        ]
    }

    /// The pump's State: both settings stamped at 10:00.
    fn pump_state() -> JsonValue {
        json!({
            "dutypoint": {"Value": 0.1, "TimeStamp": "10:00"},
            "on": {"Value": true, "TimeStamp": "10:00"},
        })
    }

    fn service(
        cache: &Arc<TopicCache>,
        reply: Option<fn(&JsonValue) -> JsonValue>,
    ) -> Arc<Service> {
        Arc::new(Service {
            cache: cache.clone(),
            published: Mutex::new(vec![]),
            reply,
        })
    }

    /// Mutations publishing to `service`, waiting briefly for confirmation.
    fn mutations_through(service: Arc<Service>) -> Mutations {
        Mutations {
            publisher: service,
            timeout: Duration::from_millis(50),
        }
    }

    async fn execute(
        cache: &Arc<TopicCache>,
        service: &Arc<Service>,
        query: &str,
    ) -> async_graphql::Response {
        let mutations = mutations_through(service.clone());
        build_schema(&api(), cache, Some(&mutations))
            .unwrap()
            .execute(query)
            .await
    }

    #[test_log::test]
    fn test_mutation_tree_mirrors_the_query_tree() {
        let cache = Arc::new(TopicCache::new());
        let mutations = mutations_through(service(&cache, None));
        let sdl = build_schema(&api(), &cache, Some(&mutations))
            .unwrap()
            .sdl();

        assert!(sdl.contains("room: MutationRoom\n"), "{sdl}");
        assert!(
            sdl.contains("thermostat(input: RoomRoomThermostatSetInput!): RoomRoomThermostat!"),
            "{sdl}"
        );
        assert!(
            sdl.contains("light(input: RoomRoomLightSetInput!): Boolean!"),
            "{sdl}"
        );
        assert!(sdl.contains("pause: Boolean!\n"), "{sdl}");
        assert!(!sdl.contains("RoomRoomPauseInput"), "{sdl}");
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_signal_takes_no_input_and_publishes_an_empty_object() {
        let cache = Arc::new(TopicCache::new());
        let service = service(&cache, None);

        let response = execute(&cache, &service, "mutation { room { pause } }").await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data = response.data.into_json().unwrap();
        assert_eq!(data["room"]["pause"], json!(true));
        assert_eq!(
            *service.published.lock().unwrap(),
            [("room/pause".to_string(), json!({}))]
        );
    }

    #[test_log::test]
    fn test_input_type_clashing_with_an_object_type_errors() {
        // The light's input type and the payload type of `room/other` are
        // both `RoomRoomLightSetInput`.
        let mut other = topic("room/other", Direction::Send, &[("x", FieldType::Float)]);
        other.payload.as_mut().unwrap().name = "room-light-set-input".to_string();
        let light = topic(
            "room/light/set",
            Direction::Receive,
            &[("on", FieldType::Boolean)],
        );
        let validators = [(
            "room/light/set".to_string(),
            jsonschema::validator_for(&json!({"type": "object"})).unwrap(),
        )]
        .into_iter()
        .collect();
        let api = Api::new(vec![
            Spec::new("room".to_string(), vec![other, light], validators).unwrap(),
        ]);
        let cache = Arc::new(TopicCache::new());
        let mutations = mutations_through(service(&cache, None));

        let err = build_schema(&api, &cache, Some(&mutations)).unwrap_err();
        assert!(
            err.to_string()
                .contains("GraphQL type name clash: 'RoomRoomLightSetInput' is used by both"),
            "{err}"
        );
    }

    #[test_log::test]
    fn test_no_mutation_tree_without_mutations() {
        let sdl = build_schema(&api(), &Arc::new(TopicCache::new()), None)
            .unwrap()
            .sdl();
        assert!(!sdl.contains("Mutation"), "{sdl}");
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_without_state_topic_publishes_and_returns_true() {
        let cache = Arc::new(TopicCache::new());
        let service = service(&cache, None);

        let response = execute(
            &cache,
            &service,
            "mutation { room { light(input: {on: true}) } }",
        )
        .await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data = response.data.into_json().unwrap();
        assert_eq!(data["room"]["light"], json!(true));
        assert_eq!(
            *service.published.lock().unwrap(),
            [("room/light/set".to_string(), json!({"on": true}))]
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_merges_state_and_returns_it_once_confirmed() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "room/thermostat",
            json!({"setpoint": 20.0, "mode": "auto", "measured": 19.5}),
        );
        let service = service(
            &cache,
            Some(|payload| {
                let mut state = payload.clone();
                state["measured"] = json!(19.6);
                state
            }),
        );

        let response = execute(
            &cache,
            &service,
            "mutation { room { thermostat(input: {setpoint: 21}) { setpoint mode measured } } }",
        )
        .await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data = response.data.into_json().unwrap();
        assert_eq!(
            data["room"]["thermostat"],
            json!({"setpoint": 21, "mode": "auto", "measured": 19.6})
        );
        // Read-only State fields are not published.
        assert_eq!(
            *service.published.lock().unwrap(),
            [(
                "room/thermostat/set".to_string(),
                json!({"setpoint": 21, "mode": "auto"})
            )]
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_errors_when_state_does_not_show_the_input() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("room/thermostat", json!({"setpoint": 20.0, "mode": "auto"}));
        // The service clamps the setpoint.
        let service = service(&cache, Some(|_| json!({"setpoint": 25.0, "mode": "auto"})));

        let response = execute(
            &cache,
            &service,
            "mutation { room { thermostat(input: {setpoint: 26}) { setpoint } } }",
        )
        .await;

        assert_eq!(
            response.errors[0].message,
            "published to 'room/thermostat/set', but 'room/thermostat' did not show the input within 50ms"
        );
        assert_eq!(service.published.lock().unwrap().len(), 1);
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_rejects_input_that_does_not_match_the_schema() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("room/thermostat", json!({"setpoint": 20.0, "mode": "auto"}));
        let service = service(&cache, None);

        let response = execute(
            &cache,
            &service,
            "mutation { room { thermostat(input: {setpoint: 99}) { setpoint } } }",
        )
        .await;

        assert!(
            response.errors[0].message.starts_with(
                "input for 'room/thermostat/set' does not match its schema: /setpoint"
            ),
            "{:?}",
            response.errors
        );
        assert!(service.published.lock().unwrap().is_empty());
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_without_cached_state_needs_a_full_input() {
        let cache = Arc::new(TopicCache::new());
        let service = service(&cache, None);

        let response = execute(
            &cache,
            &service,
            "mutation { room { thermostat(input: {setpoint: 21}) { setpoint } } }",
        )
        .await;

        assert!(
            response.errors[0]
                .message
                .contains("\"mode\" is a required property"),
            "{:?}",
            response.errors
        );
        assert!(service.published.lock().unwrap().is_empty());
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_with_state_topic_and_empty_input_errors() {
        let cache = Arc::new(TopicCache::new());
        let service = service(&cache, None);

        let response = execute(
            &cache,
            &service,
            "mutation { room { thermostat(input: {}) { setpoint } } }",
        )
        .await;

        assert_eq!(
            response.errors[0].message,
            "input for 'room/thermostat/set' sets no fields"
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_never_publishes_a_stale_timestamp() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("room/pump", pump_state());
        let service = service(&cache, Some(Clone::clone));

        let response = execute(
            &cache,
            &service,
            "mutation { room { pump(input: {dutypoint: {value: 0.3}}) { dutypoint { value } } } }",
        )
        .await;

        // The State's 10:00 is not sent beside the new value, so the schema,
        // which requires a TimeStamp, rejects the input.
        assert!(
            response.errors[0]
                .message
                .contains("\"TimeStamp\" is a required property"),
            "{:?}",
            response.errors
        );
        assert!(service.published.lock().unwrap().is_empty());
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_keeps_the_stamped_values_it_does_not_set() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("room/pump", pump_state());
        let service = service(&cache, Some(Clone::clone));

        let response = execute(
            &cache,
            &service,
            r#"mutation { room { pump(input: {dutypoint: {value: 0.3, timeStamp: "10:05"}}) { dutypoint { value } } } }"#,
        )
        .await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        assert_eq!(
            *service.published.lock().unwrap(),
            [(
                "room/pump/set".to_string(),
                json!({
                    "dutypoint": {"Value": 0.3, "TimeStamp": "10:05"},
                    "on": {"Value": true, "TimeStamp": "10:00"},
                })
            )]
        );
    }

    #[test_log::test]
    fn test_lists_are_typed_or_json_in_output_and_input() {
        let cache = Arc::new(TopicCache::new());
        let mutations = mutations_through(service(&cache, None));
        let sdl = build_schema(&api(), &cache, Some(&mutations))
            .unwrap()
            .sdl();

        assert!(sdl.contains("scalar JSON"), "{sdl}");
        for type_name in ["type RoomRoomHeater {", "input RoomRoomHeaterSetInput {"] {
            let (_, body) = sdl.split_once(type_name).unwrap();
            let (body, _) = body.split_once('}').unwrap();
            assert!(body.contains("curve: [Float]"), "{type_name}{body}");
            assert!(body.contains("tuning: JSON"), "{type_name}{body}");
        }
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_lists() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "room/heater",
            json!({"tuning": [0.01, 0.001, 0], "curve": [20.0, 21.5]}),
        );
        let service = service(&cache, None);

        let response = execute(&cache, &service, "{ room { heater { tuning curve } } }").await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data = response.data.into_json().unwrap();
        assert_eq!(
            data["room"]["heater"],
            json!({"tuning": [0.01, 0.001, 0], "curve": [20.0, 21.5]})
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_sets_a_list_and_confirms_it_by_value() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "room/heater",
            json!({"tuning": [0.01, 0.001, 0.0], "curve": [20.0, 21.5]}),
        );
        // The service reports `0.0` as `0`.
        let service = service(
            &cache,
            Some(|payload| {
                let mut state = payload.clone();
                state["tuning"] = json!([0.02, 0.001, 0]);
                state
            }),
        );

        let response = execute(
            &cache,
            &service,
            "mutation { room { heater(input: {tuning: [0.02, 0.001, 0.0], curve: [19.0, 22.0]}) { tuning curve } } }",
        )
        .await;

        assert!(response.errors.is_empty(), "{:?}", response.errors);
        // Both the `JSON` list and the typed `[Float]` list come from the input.
        assert_eq!(
            *service.published.lock().unwrap(),
            [(
                "room/heater/set".to_string(),
                json!({"tuning": [0.02, 0.001, 0.0], "curve": [19.0, 22.0]})
            )]
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_mutation_rejects_a_list_that_does_not_match_the_schema() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "room/heater",
            json!({"tuning": [0.01, 0.001, 0.0], "curve": [20.0]}),
        );
        let service = service(&cache, None);

        let response = execute(
            &cache,
            &service,
            "mutation { room { heater(input: {tuning: [0.02, 0.001]}) { tuning } } }",
        )
        .await;

        assert!(
            response.errors[0]
                .message
                .starts_with("input for 'room/heater/set' does not match its schema: /tuning"),
            "{:?}",
            response.errors
        );
        assert!(service.published.lock().unwrap().is_empty());
    }

    #[test_log::test]
    fn test_shows_compares_lists_by_element_and_length() {
        assert!(shows(&json!([1, 2.5]), &json!([1.0, 2.5])));
        assert!(!shows(&json!([1, 2.5]), &json!([1.0])));
        assert!(!shows(&json!([1, 2.5]), &json!([1.0, 2.6])));
    }

    #[test_log::test]
    fn test_merge_fills_omitted_root_fields() {
        let base = json!({"a": 1, "b": {"x": 2}});
        assert_eq!(
            merge(base, &json!({"a": 5})),
            json!({"a": 5, "b": {"x": 2}})
        );
    }

    #[test_log::test]
    fn test_merge_fills_omitted_objects_inside_given_objects() {
        let base = json!({"a": {"x": {"v": 1}, "y": {"v": 2}}});
        assert_eq!(
            merge(base, &json!({"a": {"x": {"v": 5}}})),
            json!({"a": {"x": {"v": 5}, "y": {"v": 2}}})
        );
    }

    #[test_log::test]
    fn test_merge_leaves_out_omitted_scalars_inside_given_objects() {
        let base = json!({"a": {"v": 1, "t": "10:00"}});
        assert_eq!(merge(base, &json!({"a": {"v": 5}})), json!({"a": {"v": 5}}));
    }

    #[test_log::test]
    fn test_shows_compares_given_leaves_only() {
        let state = json!({"a": {"x": 1.0, "y": 2}, "b": 3});
        assert!(shows(&state, &json!({"a": {"x": 1}})));
        assert!(!shows(&state, &json!({"a": {"x": 1.5}})));
        assert!(!shows(&state, &json!({"c": 1})));
    }

    #[test_log::test]
    fn test_project_keeps_only_input_fields() {
        let fields = BTreeMap::from([(
            "a".to_string(),
            FieldType::Object(
                "A".to_string(),
                Box::new(BTreeMap::from([("x".to_string(), FieldType::Int)])),
            ),
        )]);
        let state = json!({"a": {"x": 1, "y": 2}, "x": 1, "b": 3});
        assert_eq!(project(&state, &fields), json!({"a": {"x": 1}}));
    }
}
