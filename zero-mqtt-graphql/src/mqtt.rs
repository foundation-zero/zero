use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;

use jsonschema::Validator;
use log::{debug, error, info, warn};
use rumqttc::{AsyncClient, Event, EventLoop, Incoming, MqttOptions, QoS};
use serde_json::Value;

use crate::asyncapi::{TopicDef, TopicGroupDef};
use crate::cache::{mqtt_pattern_matches, TopicCache};

pub struct MqttConnection<'a> {
    pub host: &'a str,
    pub port: u16,
    pub username: Option<&'a str>,
    pub password: Option<&'a str>,
}

pub struct MqttSubscriber {
    client: AsyncClient,
    event_loop: EventLoop,
    cache: Arc<TopicCache>,
    listen_only: bool,
    validators: HashMap<String, Validator>,
    /// Topics to subscribe once the connection is established. Subscribing
    /// from within the polled event loop avoids deadlocking on the bounded
    /// request channel when the topic count exceeds its capacity.
    pending_subscriptions: Vec<String>,
}

impl MqttSubscriber {
    pub fn new_with_mode(
        connection: MqttConnection,
        cache: Arc<TopicCache>,
        listen_only: bool,
        topics: &[TopicDef],
        groups: &[TopicGroupDef],
    ) -> anyhow::Result<Self> {
        let client_id = format!("zero-mqtt-graphql-{:012x}", rand_u64());

        let mut mqttoptions = MqttOptions::new(&client_id, connection.host, connection.port);
        mqttoptions.set_keep_alive(Duration::from_secs(15));

        if let (Some(user), Some(pass)) = (connection.username, connection.password) {
            mqttoptions.set_credentials(user, pass);
        }

        let (client, event_loop) = AsyncClient::new(mqttoptions, 10);

        // Validators are built in both modes: listen-only rejects mismatches
        // outright, serve mode logs them and still caches the payload.
        let validators = build_validators(topics, groups);

        Ok(Self {
            client,
            event_loop,
            cache,
            listen_only,
            validators,
            pending_subscriptions: Vec::new(),
        })
    }

    /// Queue topics to subscribe to once the broker connection is up.
    pub fn set_pending_subscriptions(&mut self, topics: &[String]) {
        debug!("Queuing {} subscription(s)", topics.len());
        self.pending_subscriptions = topics.to_vec();
    }

    /// Run the event loop, caching incoming MQTT publishes.
    ///
    /// In listen-only mode, each JSON payload is validated against its topic's
    /// JSON Schema (from the AsyncAPI specs). Mismatches are logged at WARN
    /// level; valid payloads are logged at INFO. Nothing is cached and no
    /// HTTP server is involved in that mode. In serve mode, mismatches are
    /// logged but the payload is still cached.
    pub async fn run(mut self) {
        const INITIAL_BACKOFF: Duration = Duration::from_secs(1);
        const MAX_BACKOFF: Duration = Duration::from_secs(60);
        let mut backoff = INITIAL_BACKOFF;

        loop {
            match self.event_loop.poll().await {
                Ok(Event::Incoming(Incoming::Publish(publish))) => {
                    self.handle_publish(publish.topic, &publish.payload).await;
                }
                Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                    backoff = INITIAL_BACKOFF;
                    info!("MQTT connected");
                    self.spawn_pending_subscriptions();
                }
                Ok(_) => {
                    // Other events — ignore
                }
                Err(e) => {
                    error!(
                        "MQTT event loop error: {}. Reconnecting in {:?}...",
                        e, backoff
                    );
                    // rumqttc auto-reconnects; back off exponentially to avoid
                    // hammering the broker on persistent failures.
                    tokio::time::sleep(backoff).await;
                    backoff = (backoff * 2).min(MAX_BACKOFF);
                }
            }
        }
    }

    /// Subscribe to every queued topic without blocking the event loop.
    ///
    /// Client requests flow through a bounded channel that is only drained
    /// while [`Self::run`] polls the event loop, so awaiting sends inline
    /// would deadlock once more topics than the channel capacity are queued.
    /// Each ConnAck spawns a fresh batch; duplicate subscribes across
    /// reconnects are harmless.
    fn spawn_pending_subscriptions(&self) {
        if self.pending_subscriptions.is_empty() {
            return;
        }
        let client = self.client.clone();
        let topics = self.pending_subscriptions.clone();
        tokio::spawn(async move {
            let count = topics.len();
            for topic in topics {
                info!("Subscribing to {topic}");
                if let Err(e) = client.subscribe(&topic, QoS::AtLeastOnce).await {
                    error!("Failed to subscribe to '{topic}': {e}");
                }
            }
            info!("Subscribed to {count} topic(s)");
        });
    }

    /// Decode and dispatch one incoming publish: non-UTF8, empty, and
    /// non-JSON payloads are logged and dropped; JSON values go to
    /// [`Self::handle_json_payload`].
    ///
    /// Takes `&mut self` because `EventLoop` (owned by the same struct) is
    /// `!Sync`; a shared borrow would make the polling future non-`Send`.
    async fn handle_publish(&mut self, topic: String, payload: &[u8]) {
        let payload = match std::str::from_utf8(payload) {
            Ok(s) => s,
            Err(e) => {
                warn!("Non-UTF8 payload on topic '{}': {}", topic, e);
                return;
            }
        };

        if payload.trim().is_empty() {
            debug!("Empty payload on topic '{}', skipping", topic);
            return;
        }

        match serde_json::from_str::<Value>(payload) {
            Ok(value) => self.handle_json_payload(&topic, value),
            Err(e) => {
                warn!("Non-JSON payload on topic '{}': {}", topic, e);
            }
        }
    }

    /// Route a decoded JSON payload: schema-validate it in listen-only mode,
    /// cache it (flattened) otherwise.
    fn handle_json_payload(&self, topic: &str, value: Value) {
        if self.listen_only {
            match self.validate_payload(topic, &value) {
                Some(true) => info!("Schema OK for topic '{}': {}", topic, value),
                Some(false) => {} // mismatch already logged
                None if self.validators.is_empty() => {
                    info!("Received on topic '{}' (no schema known): {}", topic, value)
                }
                None => warn!(
                    "Received on unknown topic '{}' (not in specs): {}",
                    topic, value
                ),
            }
            return;
        }

        // Mismatch details are logged by `validate_payload`; serve mode
        // caches the payload regardless of validity.
        let _ = self.validate_payload(topic, &value);

        let rendered = value.to_string();
        let preview_len = rendered
            .char_indices()
            .nth(100)
            .map(|(idx, _)| idx)
            .unwrap_or(rendered.len());
        if preview_len < rendered.len() {
            debug!(
                "Caching payload for topic '{}': {}...",
                topic,
                &rendered[..preview_len]
            );
        } else {
            debug!("Caching payload for topic '{}': {}", topic, rendered);
        }
        self.cache.insert(topic, flatten_payload(value));
    }

    /// Validate a payload against its topic's compiled schema, logging
    /// mismatch details. Tries an exact-topic key first, then falls back to
    /// the wildcard-containing keys (from topic groups). Returns `None`
    /// when no schema covers the topic, else whether the payload is valid.
    fn validate_payload(&self, topic: &str, value: &Value) -> Option<bool> {
        let validator = self.validators.get(topic).or_else(|| {
            self.validators
                .iter()
                .filter(|(pattern, _)| pattern.contains('+') || pattern.contains('#'))
                .find(|(pattern, _)| mqtt_pattern_matches(pattern, topic))
                .map(|(_, validator)| validator)
        })?;
        let valid = validator.is_valid(value);
        if !valid {
            let details: Vec<String> = validator
                .iter_errors(value)
                .map(|e| format!("{}: {}", e.instance_path, e))
                .collect();
            warn!(
                "Schema mismatch on topic '{}': {} | payload: {}",
                topic,
                details.join("; "),
                value
            );
        }
        Some(valid)
    }
}

/// Compile one validator per topic and one per topic group, into a single
/// map keyed by exact topic (`TopicDef`) or wildcard pattern (`TopicGroupDef`,
/// e.g. `power-tags/+/+`)
fn build_validators(topics: &[TopicDef], groups: &[TopicGroupDef]) -> HashMap<String, Validator> {
    let topic_validators: Vec<(String, Validator)> = topics
        .iter()
        .filter_map(|td| {
            let schema_value = td.payload_schema.as_ref()?;
            match Validator::new(schema_value) {
                Ok(validator) => Some((td.topic.clone(), validator)),
                Err(e) => {
                    warn!(
                        "Failed to compile JSON Schema for topic '{}': {} — skipping validation for this topic",
                        td.topic, e
                    );
                    None
                }
            }
        })
        .collect();
    if !topic_validators.is_empty() {
        info!(
            "Compiled JSON Schema validators for {} topic(s)",
            topic_validators.len()
        );
    }

    let group_validators: Vec<(String, Validator)> = groups
        .iter()
        .filter_map(|group| {
            let schema_value = group.payload_schema.as_ref()?;
            match Validator::new(schema_value) {
                Ok(validator) => Some((group.pattern.clone(), validator)),
                Err(e) => {
                    warn!(
                        "Failed to compile JSON Schema for topic group '{}': {} — skipping validation for this group",
                        group.pattern, e
                    );
                    None
                }
            }
        })
        .collect();
    if !group_validators.is_empty() {
        info!(
            "Compiled JSON Schema validators for {} topic group(s)",
            group_validators.len()
        );
    }

    topic_validators
        .into_iter()
        .chain(group_validators)
        .collect()
}

/// Generate a unique suffix for the MQTT client ID from full-precision
/// wall-clock nanoseconds, so concurrent instances and rapid restarts do not
/// collide (brokers disconnect clients sharing an ID).
fn rand_u64() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos() as u64;
    let mut x = nanos;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    x
}

/// Flatten nested objects one level deep into the payload root.
///
/// Services such as hull-temperature publish `{"temperatures": {sensor: value}}`
/// while their AsyncAPI spec lists the nested keys as top-level fields, so the
/// GraphQL schema expects them at the top level. Existing top-level keys win on
/// collision; the wrapper key is kept so the raw payload stays visible.
fn flatten_payload(value: Value) -> Value {
    let Value::Object(map) = &value else {
        return value;
    };

    let mut merged = map.clone();
    for nested in map.values() {
        if let Value::Object(nested_map) = nested {
            for (nested_key, nested_value) in nested_map {
                if !merged.contains_key(nested_key) {
                    merged.insert(nested_key.clone(), nested_value.clone());
                }
            }
        }
    }
    Value::Object(merged)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::asyncapi::FieldDef;
    use serde_json::json;
    use std::collections::BTreeMap;

    fn group_with_schema(pattern: &str, schema: Value) -> TopicGroupDef {
        TopicGroupDef {
            group: "power-tags".to_string(),
            pattern: pattern.to_string(),
            params: vec!["panel".to_string(), "slug".to_string()],
            fields: vec![FieldDef {
                name: "active_power_total".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: Some(schema),
            value_extensions: BTreeMap::new(),
            ttl_secs: 300,
        }
    }

    #[test]
    fn test_build_validators_compiles_group_schema() {
        let groups = vec![group_with_schema(
            "power-tags/+/+",
            json!({"type": "object", "required": ["active_power_total"]}),
        )];
        let validators = build_validators(&[], &groups);
        assert_eq!(validators.len(), 1);
        assert!(validators.contains_key("power-tags/+/+"));
    }

    #[test]
    fn test_build_validators_skips_group_without_schema() {
        let mut group = group_with_schema("power-tags/+/+", json!({}));
        group.payload_schema = None;
        let validators = build_validators(&[], &[group]);
        assert!(validators.is_empty());
    }

    /// Regression test for the gap where payloads on parametrized topic
    /// group patterns (e.g. `power-tags/+/+`) were never validated: no
    /// validator was ever compiled from `TopicGroupDef`, and the exact-key
    /// lookup wouldn't have matched a concrete topic against a pattern key
    /// anyway.
    #[test]
    fn test_validate_payload_matches_concrete_topic_against_group_pattern() {
        let group = group_with_schema(
            "power-tags/+/+",
            json!({"type": "object", "required": ["active_power_total"]}),
        );
        let sub = test_subscriber(&[], &[group]);

        // Matches: concrete topic under the group's wildcard pattern.
        assert_eq!(
            sub.validate_payload(
                "power-tags/10P1/breaker3",
                &json!({"active_power_total": 42.0})
            ),
            Some(true)
        );
        assert_eq!(
            sub.validate_payload("power-tags/10P1/breaker3", &json!({})),
            Some(false)
        );

        // No topic or group covers this — unknown to the subscriber.
        assert_eq!(sub.validate_payload("unrelated/topic", &json!({})), None);
    }

    /// One group validator must cover every concrete topic under its
    /// pattern, not just whichever one happens to be tested — two unrelated
    /// panels here both validate against the same `power-tags/+/+` schema.
    #[test]
    fn test_validate_payload_group_validator_covers_multiple_distinct_topics() {
        let group = group_with_schema(
            "power-tags/+/+",
            json!({"type": "object", "required": ["active_power_total"]}),
        );
        let sub = test_subscriber(&[], &[group]);

        assert_eq!(
            sub.validate_payload(
                "power-tags/10P1/breaker3",
                &json!({"active_power_total": 1.0})
            ),
            Some(true)
        );
        assert_eq!(
            sub.validate_payload(
                "power-tags/10P2/breaker9",
                &json!({"active_power_total": 2.0})
            ),
            Some(true)
        );
        assert_eq!(
            sub.validate_payload("power-tags/10P2/breaker9", &json!({})),
            Some(false)
        );
    }

    /// A topic-specific validator must win over an overlapping group
    /// pattern for the same concrete topic, per the exact-key-first lookup
    /// in `validate_payload`.
    #[test]
    fn test_validate_payload_exact_topic_wins_over_overlapping_group() {
        let topic = TopicDef {
            topic: "power-tags/10P1/breaker3".to_string(),
            fields: vec![FieldDef {
                name: "active_power_total".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: Some(json!({"type": "object", "required": ["active_power_total"]})),
            ttl_secs: 300,
        };
        let group = group_with_schema("power-tags/+/+", json!({"type": "object"}));
        let sub = test_subscriber(&[topic], &[group]);

        // Fails the exact-topic schema (missing required field) even though
        // it would pass the group's permissive schema — proves the exact
        // match, not the group, was used.
        assert_eq!(
            sub.validate_payload("power-tags/10P1/breaker3", &json!({})),
            Some(false)
        );
    }

    /// The `#` multi-level wildcard, used e.g. for a catch-all logs group,
    /// must also drive validation — not just the `+` groups exercised above.
    #[test]
    fn test_validate_payload_matches_hash_wildcard_pattern() {
        let group = group_with_schema("logs/#", json!({"type": "object", "required": ["level"]}));
        let sub = test_subscriber(&[], &[group]);

        assert_eq!(
            sub.validate_payload("logs/a", &json!({"level": "info"})),
            Some(true)
        );
        assert_eq!(
            sub.validate_payload("logs/a/b/c", &json!({"level": "warn"})),
            Some(true)
        );
        assert_eq!(sub.validate_payload("logs/a", &json!({})), Some(false));
        assert_eq!(sub.validate_payload("metrics/a", &json!({})), None);
    }

    fn test_subscriber(topics: &[TopicDef], groups: &[TopicGroupDef]) -> MqttSubscriber {
        let connection = MqttConnection {
            host: "localhost",
            port: 1883,
            username: None,
            password: None,
        };
        MqttSubscriber::new_with_mode(
            connection,
            Arc::new(TopicCache::new()),
            true,
            topics,
            groups,
        )
        .unwrap()
    }

    #[test]
    fn test_flatten_nested_payload() {
        let payload = json!({"temperatures": {"sensor_a": 20.0, "sensor_b": 21.5}});
        let flattened = flatten_payload(payload);
        assert_eq!(flattened["sensor_a"], json!(20.0));
        assert_eq!(flattened["sensor_b"], json!(21.5));
        assert!(flattened.get("temperatures").is_some());
    }

    #[test]
    fn test_flatten_keeps_existing_keys() {
        let payload = json!({"watts": 4.2, "nested": {"watts": 99.0}});
        let flattened = flatten_payload(payload);
        assert_eq!(flattened["watts"], json!(4.2));
    }

    #[test]
    fn test_flatten_flat_payload_is_unchanged() {
        let payload = json!({"watts": 4.2, "ok": true});
        let flattened = flatten_payload(payload);
        assert_eq!(flattened, json!({"watts": 4.2, "ok": true}));
    }

    #[test]
    fn test_flatten_non_object_passthrough() {
        let payload = json!(42.0);
        assert_eq!(flatten_payload(payload), json!(42.0));
    }

    #[test]
    fn test_flatten_merges_multiple_nested_objects() {
        let payload = json!({"a": {"x": 1.0}, "b": {"y": 2.0}});
        let flattened = flatten_payload(payload);
        assert_eq!(flattened["x"], json!(1.0));
        assert_eq!(flattened["y"], json!(2.0));
        assert_eq!(flattened["a"]["x"], json!(1.0));
    }

    #[test]
    fn test_flatten_ignores_non_object_values() {
        let payload = json!({"a": 1, "b": "str", "c": [1, 2], "d": {"z": 3}});
        let flattened = flatten_payload(payload);
        assert_eq!(flattened["a"], json!(1));
        assert_eq!(flattened["b"], json!("str"));
        assert_eq!(flattened["c"], json!([1, 2]));
        assert_eq!(flattened["z"], json!(3));
    }

    #[test]
    fn test_flatten_only_hoists_one_level() {
        let payload = json!({"a": {"b": {"c": 1}}});
        let flattened = flatten_payload(payload);
        // "b" is hoisted, but "c" stays two levels deep
        assert_eq!(flattened["b"], json!({"c": 1}));
        assert!(flattened.get("c").is_none());
    }

    #[test]
    fn test_flatten_empty_payload_is_unchanged() {
        let payload = json!({});
        assert_eq!(flatten_payload(payload), json!({}));
    }
}
