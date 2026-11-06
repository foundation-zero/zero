use std::time::Instant;

use dashmap::DashMap;
use serde_json::Value;

use crate::topic_map::TopicMap;

struct Entry {
    value: Value,
    inserted: Instant,
    ttl_secs: u64,
}

pub struct TopicCache {
    data: DashMap<String, Entry>,
    default_ttl_secs: u64,
    per_topic_ttl: TopicMap<u64>,
}

impl Default for TopicCache {
    fn default() -> Self {
        Self::new()
    }
}

impl TopicCache {
    #[must_use]
    pub fn new() -> Self {
        Self::with_ttl(crate::config::DEFAULT_TTL_SECS, TopicMap::new())
    }

    #[must_use]
    pub fn with_ttl(default_ttl_secs: u64, per_topic_ttl: TopicMap<u64>) -> Self {
        Self {
            data: DashMap::new(),
            default_ttl_secs,
            per_topic_ttl,
        }
    }

    /// Insert or overwrite the cached payload for a topic.
    pub fn insert(&self, topic: &str, payload: Value) {
        let ttl = self.per_topic_ttl.get(topic);
        self.data.insert(
            topic.to_string(),
            Entry {
                value: payload,
                inserted: Instant::now(),
                ttl_secs: *ttl.unwrap_or(&self.default_ttl_secs),
            },
        );
    }

    /// Get the full cached payload for a topic, or `None` if missing or expired.
    #[must_use]
    pub fn get(&self, topic: &str) -> Option<Value> {
        let entry = self.get_entry_if_fresh(topic)?;
        Some(entry.value.clone())
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

/// Evict expired entries from the cache periodically.
pub fn spawn_eviction(cache: std::sync::Arc<TopicCache>) {
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(std::time::Duration::from_secs(30));
        loop {
            interval.tick().await;
            cache.evict_expired();
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test_log::test]
    fn test_from_definitions_collects_overrides() {
        let mut topic_map = TopicMap::new();
        topic_map.insert_with_replace("default/ttl".to_string(), 300);
        topic_map.insert_with_replace("custom/ttl".to_string(), 0);
        topic_map.insert_with_replace("power-tags/+/+".to_string(), 0);

        let cache = TopicCache::with_ttl(300, topic_map);

        cache.insert("default/ttl", json!(1));
        cache.insert("custom/ttl", json!(1));
        cache.insert("power-tags/a/b", json!(1));
        std::thread::sleep(std::time::Duration::from_millis(10));

        assert!(cache.get("default/ttl").is_some());
        assert!(cache.get("custom/ttl").is_none());
        assert!(cache.get("power-tags/a/b").is_none());
    }

    #[test_log::test]
    fn test_insert_and_get() {
        let cache = TopicCache::new();
        let payload = json!({"celsius": 23.5, "ok": true});
        cache.insert("test/topic", payload.clone());

        let got = cache.get("test/topic").unwrap();
        assert_eq!(got, payload);
    }

    #[test_log::test]
    fn test_get_missing() {
        let cache = TopicCache::new();
        assert!(cache.get("nonexistent").is_none());
    }

    #[test_log::test]
    fn test_overwrite() {
        let cache = TopicCache::new();
        cache.insert("test/topic", json!({"v": 1}));
        cache.insert("test/topic", json!({"v": 2}));

        assert_eq!(cache.get("test/topic").unwrap(), json!({"v": 2}));
    }

    #[test_log::test]
    fn test_insert_null_payload_is_stored() {
        let cache = TopicCache::new();
        cache.insert("test/topic", serde_json::Value::Null);

        assert_eq!(cache.get("test/topic").unwrap(), serde_json::Value::Null);
    }

    #[test_log::test]
    fn test_expires_returns_none() {
        let cache = TopicCache::with_ttl(0, TopicMap::new());
        cache.insert("test/topic", json!({"v": 1}));
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(cache.get("test/topic").is_none());
    }

    #[test_log::test]
    fn test_per_topic_ttl_overrides_default() {
        let mut per_topic = TopicMap::new();
        per_topic.insert_with_replace("fast".to_string(), 0);
        let cache = TopicCache::with_ttl(60, per_topic);
        cache.insert("fast", json!(1));
        cache.insert("slow", json!(2));
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(cache.get("fast").is_none());
        assert!(cache.get("slow").is_some());
    }

    #[test_log::test]
    fn test_group_pattern_ttl_overrides_default_insert_and_evicted() {
        let mut per_topic = TopicMap::new();
        per_topic.insert_with_replace("power-tags/+/+".to_string(), 0);
        per_topic.insert_with_replace("logs/#".to_string(), 0);
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

    #[test_log::test]
    fn test_evict_expired() {
        let cache = TopicCache::with_ttl(0, TopicMap::new());
        cache.insert("a", json!(1));
        cache.insert("b", json!(2));
        std::thread::sleep(std::time::Duration::from_millis(10));
        cache.evict_expired();
        assert!(cache.get("a").is_none());
        assert!(cache.get("b").is_none());
    }
}
