use std::collections::HashMap;
use std::time::Instant;

use dashmap::DashMap;
use serde_json::Value;

use crate::asyncapi::{TopicDef, TopicGroupDef};

struct Entry {
    value: Value,
    inserted: Instant,
    ttl_secs: u64,
}

pub struct TopicCache {
    data: DashMap<String, Entry>,
    default_ttl_secs: u64,
    per_topic_ttl: HashMap<String, u64>,
}

impl Default for TopicCache {
    fn default() -> Self {
        Self::new()
    }
}

impl TopicCache {
    pub fn new() -> Self {
        Self::with_ttl(crate::config::DEFAULT_TTL_SECS, HashMap::new())
    }

    pub fn with_ttl(default_ttl_secs: u64, per_topic_ttl: HashMap<String, u64>) -> Self {
        Self {
            data: DashMap::new(),
            default_ttl_secs,
            per_topic_ttl,
        }
    }

    /// Build a cache whose TTL table is derived from the AsyncAPI
    /// definitions: topics whose `ttl_secs` differs from `default_ttl` are
    /// keyed by topic, groups by their wildcard pattern so every concrete
    /// topic under them inherits the group's `x-ttl`.
    pub fn from_definitions(
        topics: &[TopicDef],
        groups: &[TopicGroupDef],
        default_ttl: u64,
    ) -> Self {
        let topic_overrides = topics
            .iter()
            .filter(|t| t.ttl_secs != default_ttl)
            .map(|t| (t.topic.clone(), t.ttl_secs));
        let group_overrides = groups
            .iter()
            .filter(|g| g.ttl_secs != default_ttl)
            .map(|g| (g.pattern.clone(), g.ttl_secs));
        Self::with_ttl(
            default_ttl,
            topic_overrides.chain(group_overrides).collect(),
        )
    }

    fn ttl_for(&self, topic: &str) -> u64 {
        if let Some(ttl) = self.per_topic_ttl.get(topic) {
            return *ttl;
        }
        // Wildcard patterns (from parametrized topic groups) match any of
        // their concrete topics.
        self.per_topic_ttl
            .iter()
            .filter(|(pattern, _)| pattern.contains('+') || pattern.contains('#'))
            .find(|(pattern, _)| mqtt_pattern_matches(pattern, topic))
            .map(|(_, ttl)| *ttl)
            .unwrap_or(self.default_ttl_secs)
    }

    /// Insert or overwrite the cached payload for a topic.
    pub fn insert(&self, topic: &str, payload: Value) {
        let ttl = self.ttl_for(topic);
        self.data.insert(
            topic.to_string(),
            Entry {
                value: payload,
                inserted: Instant::now(),
                ttl_secs: ttl,
            },
        );
    }

    /// Get the full cached payload for a topic, or `None` if missing or expired.
    pub fn get(&self, topic: &str) -> Option<Value> {
        let entry = self.get_entry_if_fresh(topic)?;
        Some(entry.value.clone())
    }

    /// Get a specific field from a topic's cached payload.
    pub fn get_field(&self, topic: &str, field: &str) -> Option<Value> {
        let entry = self.get_entry_if_fresh(topic)?;
        entry.value.get(field).cloned()
    }

    /// Borrow the live entry for `topic`, evicting it first when its TTL
    /// has elapsed.
    fn get_entry_if_fresh(
        &self,
        topic: &str,
    ) -> Option<dashmap::mapref::one::Ref<'_, String, Entry>> {
        let entry = self.data.get(topic)?;
        if entry.inserted.elapsed().as_secs() >= entry.ttl_secs {
            drop(entry);
            self.data.remove(topic);
            None
        } else {
            Some(entry)
        }
    }

    /// Remove all expired entries.
    pub fn evict_expired(&self) {
        let to_remove: Vec<String> = self
            .data
            .iter()
            .filter(|e| e.value().inserted.elapsed().as_secs() >= e.value().ttl_secs)
            .map(|e| e.key().clone())
            .collect();
        for key in to_remove {
            self.data.remove(&key);
        }
    }
}

/// MQTT wildcard match: `+` matches one level, `#` matches the rest.
fn mqtt_pattern_matches(pattern: &str, topic: &str) -> bool {
    let mut pattern_levels = pattern.split('/');
    let mut topic_levels = topic.split('/');
    loop {
        match (pattern_levels.next(), topic_levels.next()) {
            (Some("#"), _) => return true,
            (Some("+"), Some(_)) => {}
            (Some(p), Some(t)) if p == t => {}
            (None, None) => return true,
            _ => return false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::asyncapi::{FieldDef, TopicGroupDef};
    use serde_json::json;
    use std::collections::BTreeMap;

    fn topic(topic_name: &str, ttl_secs: u64) -> TopicDef {
        TopicDef {
            topic: topic_name.to_string(),
            fields: vec![FieldDef {
                name: "v".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs,
        }
    }

    fn group(group_id: &str, pattern: &str, ttl_secs: u64) -> TopicGroupDef {
        TopicGroupDef {
            group: group_id.to_string(),
            pattern: pattern.to_string(),
            params: Vec::new(),
            fields: Vec::new(),
            payload_schema: None,
            value_extensions: BTreeMap::new(),
            ttl_secs,
        }
    }

    #[test]
    fn test_from_definitions_collects_overrides() {
        let topics = vec![topic("default/ttl", 300), topic("custom/ttl", 0)];
        let groups = vec![group("power-tags", "power-tags/+/+", 0)];
        let cache = TopicCache::from_definitions(&topics, &groups, 300);

        cache.insert("default/ttl", json!(1));
        cache.insert("custom/ttl", json!(1));
        cache.insert("power-tags/a/b", json!(1));
        std::thread::sleep(std::time::Duration::from_millis(10));

        assert!(cache.get("default/ttl").is_some());
        assert!(cache.get("custom/ttl").is_none());
        assert!(cache.get("power-tags/a/b").is_none());
    }

    #[test]
    fn test_insert_and_get() {
        let cache = TopicCache::new();
        let payload = json!({"celsius": 23.5, "ok": true});
        cache.insert("test/topic", payload.clone());

        let got = cache.get("test/topic").unwrap();
        assert_eq!(got, payload);
    }

    #[test]
    fn test_get_missing() {
        let cache = TopicCache::new();
        assert!(cache.get("nonexistent").is_none());
    }

    #[test]
    fn test_get_field() {
        let cache = TopicCache::new();
        let payload = json!({"celsius": 23.5, "ok": true});
        cache.insert("test/topic", payload);

        assert_eq!(
            cache.get_field("test/topic", "celsius").unwrap(),
            json!(23.5)
        );
        assert_eq!(cache.get_field("test/topic", "ok").unwrap(), json!(true));
        assert!(cache.get_field("test/topic", "missing").is_none());
    }

    #[test]
    fn test_overwrite() {
        let cache = TopicCache::new();
        cache.insert("test/topic", json!({"v": 1}));
        cache.insert("test/topic", json!({"v": 2}));

        assert_eq!(cache.get("test/topic").unwrap(), json!({"v": 2}));
    }

    #[test]
    fn test_get_field_returns_raw_nested_payload() {
        let cache = TopicCache::new();
        cache.insert("test/topic", json!({"nested": {"v": 1.0}, "flat": 2}));

        assert_eq!(cache.get_field("test/topic", "flat").unwrap(), json!(2));
        assert_eq!(
            cache.get_field("test/topic", "nested").unwrap(),
            json!({"v": 1.0})
        );
        // The cache stores payloads verbatim; flattening happens at insert time upstream
        assert!(cache.get_field("test/topic", "v").is_none());
    }

    #[test]
    fn test_insert_null_payload_is_stored() {
        let cache = TopicCache::new();
        cache.insert("test/topic", serde_json::Value::Null);

        assert_eq!(cache.get("test/topic").unwrap(), serde_json::Value::Null);
        assert!(cache.get_field("test/topic", "anything").is_none());
    }

    #[test]
    fn test_expires_returns_none() {
        let cache = TopicCache::with_ttl(0, HashMap::new());
        cache.insert("test/topic", json!({"v": 1}));
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(cache.get("test/topic").is_none());
        assert!(cache.get_field("test/topic", "v").is_none());
    }

    #[test]
    fn test_per_topic_ttl_overrides_default() {
        let mut per_topic = HashMap::new();
        per_topic.insert("fast".to_string(), 0);
        let cache = TopicCache::with_ttl(60, per_topic);
        cache.insert("fast", json!(1));
        cache.insert("slow", json!(2));
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(cache.get("fast").is_none());
        assert!(cache.get("slow").is_some());
    }

    #[test]
    fn test_group_pattern_ttl_overrides_default() {
        let mut per_topic = HashMap::new();
        per_topic.insert("power-tags/+/+".to_string(), 0);
        per_topic.insert("logs/#".to_string(), 0);
        let cache = TopicCache::with_ttl(60, per_topic);
        cache.insert("power-tags/10P1/slug", json!(1));
        cache.insert("logs/a/b", json!(1));
        cache.insert("other/topic", json!(1));
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(cache.get("power-tags/10P1/slug").is_none());
        assert!(cache.get("logs/a/b").is_none());
        // Exact-match keys still win over patterns for the same topic
        assert!(cache.get("other/topic").is_some());
    }

    #[test]
    fn test_evict_expired() {
        let cache = TopicCache::with_ttl(0, HashMap::new());
        cache.insert("a", json!(1));
        cache.insert("b", json!(2));
        std::thread::sleep(std::time::Duration::from_millis(10));
        cache.evict_expired();
        assert!(cache.get("a").is_none());
        assert!(cache.get("b").is_none());
    }
}
