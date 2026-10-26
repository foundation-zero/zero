use std::collections::{BTreeMap, btree_map::Keys};

#[derive(Debug, Clone)]
pub struct TopicMap<T>(BTreeMap<String, T>);

impl<T> TopicMap<T> {
    pub fn new() -> Self {
        Self(BTreeMap::new())
    }

    #[must_use]
    pub fn get<'a>(&'a self, topic: &'a str) -> Option<&'a T> {
        self.get_with_key(topic).map(|(_, value)| value)
    }

    #[must_use]
    pub fn get_with_key<'a>(&'a self, topic: &'a str) -> Option<(&'a str, &'a T)> {
        if let Some((key, val)) = self.0.get_key_value(topic) {
            return Some((key, val));
        }

        // Wildcard patterns (from parametrized topic groups) match any of
        // their concrete topics.
        // TODO: This still selects the wrong entry when multiple patterns are involved and they contain spaces or ascii chars that sort before '+'
        self.0
            .iter()
            .rev() // We want + patterns before # patterns and logner before shorter
            .filter(|(pattern, _)| pattern.contains('+') || pattern.contains('#'))
            .find(|(pattern, _)| mqtt_pattern_matches(pattern, topic))
            .map(|(key, value)| (key.as_ref(), value))
    }

    /// Removes a key from the map, returning the value at the key if the key was previously in the map.
    pub fn remove(&mut self, topic: &str) -> Option<T> {
        self.0.remove(topic)
    }

    /// Returns true if the map contains no elements.
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// Does this topic map include a topic or pattern that covers the topic given
    pub(crate) fn covers_topic(&self, key: &str) -> bool {
        self.get(key).is_some()
    }

    /// Gets an iterator over the keys of the map, in sorted order.
    pub fn keys(&self) -> Keys<'_, String, T> {
        self.0.keys()
    }

    #[cfg(test)]
    pub(crate) fn insert(&mut self, key: String, value: T) -> Option<T> {
        self.0.insert(key, value)
    }

    /// Extends TopicMap with the contents of another TopicMap.
    pub(crate) fn extend(mut self, other: TopicMap<T>) -> TopicMap<T> {
        self.0.extend(other.0);
        self
    }
}

impl<T: PartialEq> TopicMap<T> {
    /// Insert a new topic, replacing all values thats are covered by the pattern if they have the same value
    ///
    ///  This does not prevent narrower values being added later that are covered by existing values
    ///  So you want to typically gate
    pub(crate) fn insert_with_replace(&mut self, key: String, value: T) -> Option<T> {
        // Fast path: Concrete topics cannot subsume other topics
        if key.contains('+') || key.ends_with('#') {
            // Evict existing keys ONLY if they are covered by the new pattern
            // AND share the exact same value.
            self.0.retain(|existing_key, existing_val| {
                // Never remove the exact key during retain; let insert handle it
                // so standard replacement return semantics are preserved.
                if existing_key == &key {
                    return true;
                }

                existing_val != &value || !mqtt_pattern_matches(&key, existing_key)
            });
        }

        // Normal insert: returns Some(old) only if the exact key was already present
        self.0.insert(key, value)
    }
}
impl<T> Default for TopicMap<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> FromIterator<(String, T)> for TopicMap<T> {
    fn from_iter<I: IntoIterator<Item = (String, T)>>(iter: I) -> Self {
        Self(BTreeMap::from_iter(iter))
    }
}

/// MQTT wildcard match: `+` matches one level, `#` matches the rest.
fn mqtt_pattern_matches(pattern: &str, topic: &str) -> bool {
    let mut pattern_levels = pattern.split('/');
    let mut topic_levels = topic.split('/');
    loop {
        match (pattern_levels.next(), topic_levels.next()) {
            (Some("#"), _) | (None, None) => return true,
            (Some("+"), Some(p)) if p != "#" => {}
            (Some(p), Some(t)) if p == t => {}
            _ => return false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test_log::test]
    fn test_pattern_matches_exact() {
        assert!(mqtt_pattern_matches(
            "power-tags/10P1/slug",
            "power-tags/10P1/slug"
        ));
        assert!(!mqtt_pattern_matches(
            "power-tags/10P1/slug",
            "power-tags/10P1/other"
        ));
    }

    #[test_log::test]
    fn test_pattern_matches_plus_single_level() {
        assert!(mqtt_pattern_matches("+/+", "power-tags/"));
        assert!(mqtt_pattern_matches("/+", "/power-tags"));
        assert!(!mqtt_pattern_matches("/+", "power-tags"));
        assert!(!mqtt_pattern_matches("+", "/power-tags"));
        assert!(mqtt_pattern_matches(
            "power-tags/+/+",
            "power-tags/10P1/slug"
        ));
        assert!(mqtt_pattern_matches(
            "power-tags/+/+",
            "power-tags/10P2/other-slug"
        ));
        // `+` matches exactly one level, not zero and not several.
        assert!(!mqtt_pattern_matches("power-tags/+/+", "power-tags/10P1"));
        assert!(!mqtt_pattern_matches(
            "power-tags/+/+",
            "power-tags/10P1/a/b"
        ));
    }

    #[test_log::test]
    fn test_pattern_matches_wildcards() {
        assert!(mqtt_pattern_matches("a/+/+", "a/b/+"));
        assert!(mqtt_pattern_matches("a/#", "a/+"));
        assert!(mqtt_pattern_matches("a/#", "a/+/+"));
        assert!(!mqtt_pattern_matches("a/+", "a/#"));
    }

    #[test_log::test]
    fn test_pattern_matches_hash_matches_remaining_levels() {
        assert!(mqtt_pattern_matches("logs/#", "logs/a"));
        assert!(mqtt_pattern_matches("logs/#", "logs/a/b/c"));
        // `#` also matches zero remaining levels (the prefix topic itself).
        assert!(mqtt_pattern_matches("logs/#", "logs"));
    }

    #[test_log::test]
    fn test_pattern_matches_rejects_different_prefix() {
        assert!(!mqtt_pattern_matches("logs/#", "metrics/a"));
        assert!(!mqtt_pattern_matches(
            "power-tags/+/+",
            "power-tags-other/10P1/slug"
        ));
    }

    #[test_log::test]
    fn test_pattern_matches_rejects_pattern_longer_than_topic() {
        assert!(!mqtt_pattern_matches("power-tags/+/+", "power-tags/10P1"));
    }

    #[test_log::test]
    fn test_topics_return_value_in_correct_order() {
        let topic_map: TopicMap<_> = [
            ("metrics/#".to_string(), 1),   // Multi-level wildcard (lowest priority)
            ("metrics/+".to_string(), 2),   // 1-level wildcard
            ("metrics/+/+".to_string(), 3), // 2-level wildcard
            ("metrics/cpu".to_string(), 4), // 1-level exact
            ("metrics/cpu/usage".to_string(), 5), // 2-level exact
            ("logs/#".to_string(), 10),
        ]
        .into_iter()
        .collect();

        let test_cases = [
            // Exact match beats wildcards
            ("metrics/cpu", Some(4)),       // Exact (4) > '+' (2) > '#' (1)
            ("metrics/cpu/usage", Some(5)), // Exact (5) > '+/+' (3) > '#' (1)
            // Single-level wildcard (+) beats multi-level wildcard (#)
            ("metrics/ram", Some(2)),      // '+' (2) > '#' (1)
            ("metrics/ ", Some(2)), // ' '' comes before + in lexographic ordering but should work since its a valid topic
            ("metrics/cpu/temp", Some(3)), // '+/+' (3) > '#' (1) [partial exact prefix]
            ("metrics/disk/io", Some(3)), // '+/+' (3) > '#' (1) [fully wildcarded]
            // Multi-level wildcard (#) acts as fallback
            ("metrics/cpu/usage/idle", Some(1)), // Depth 3 has no exact or '+', falls back to '#'
            ("metrics", Some(1)),                // Root topic matches '#' per MQTT spec
            ("logs/system/err", Some(10)),       // Multi-level traversal
            ("logs", Some(10)),                  // Standalone root matches '#'
            // Non-matching topics
            ("metrics-other", None), // Sibling prefix without delimiter boundary
            ("other/topic", None),   // Unmapped tree
        ];

        for (topic, expected) in test_cases {
            assert_eq!(
                topic_map.get(topic),
                expected.as_ref(),
                "Precedence resolution mismatch for topic: {topic}"
            );
        }
    }

    #[test_log::test]
    fn test_covers_topic() {
        let topic_map: TopicMap<_> = [
            ("exact/device/state".to_string(), ()),
            ("single/+/status".to_string(), ()),
            ("multi/#".to_string(), ()),
            ("mixed/+/telemetry/#".to_string(), ()),
        ]
        .into_iter()
        .collect();

        let test_cases = [
            // Exact matching
            ("exact/device/state", true),
            ("exact/device/power", false),
            ("exact/device", false),
            ("exact/device/state/extra", false),
            // Single-level wildcard (+)
            ("single/sensor1/status", true),
            ("single/sensor2/status", true),
            ("single/status", false),         // Missing level
            ("single/a/b/status", false),     // Too many levels
            ("single/sensor1/errors", false), // Sibling mismatch
            // Multi-level wildcard (#)
            ("multi/a", true),
            ("multi/a/b/c", true),
            ("multi", true), // Root matches in MQTT spec
            ("other/multi/a", false),
            // Mixed (+ and #)
            ("mixed/sensor/telemetry", true),
            ("mixed/sensor/telemetry/temp", true),
            ("mixed/sensor/telemetry/temp/raw", true),
            ("mixed/telemetry/temp", false), // Missing `+` segment
            // Subsumption / wildcard query checks
            ("multi/sub/#", true),     // Covered by multi/#
            ("exact/#", false),        // exact/device/state does not cover exact/#
            ("single/+/status", true), // Identical pattern covered
        ];

        for (topic, expected) in test_cases {
            assert_eq!(
                topic_map.covers_topic(topic),
                expected,
                "Assertion failed for topic pattern: {topic}"
            );
        }
    }

    #[test_log::test]
    fn test_insert_with_replace() {
        let mut map: TopicMap<i32> = TopicMap::default();

        // Initial entries
        assert_eq!(map.insert_with_replace("logs/a".to_string(), 1), None);
        assert_eq!(map.insert_with_replace("logs/b".to_string(), 2), None);
        assert_eq!(map.insert_with_replace("logs/sub/c".to_string(), 1), None);
        assert_eq!(map.insert_with_replace("other/a".to_string(), 1), None);

        // Insert broader pattern with value 1:
        // - Subsumed keys with value 1 ("logs/a", "logs/sub/c") are evicted.
        // - Subsumed key with value 2 ("logs/b") is PRESERVED.
        // - Sibling topic with value 1 ("other/a") is PRESERVED.
        // - Return value is None because "logs/#" was not previously in the map.
        let replaced = map.insert_with_replace("logs/#".to_string(), 1);
        assert_eq!(replaced, None);

        assert_eq!(map.0.get("logs/a"), None);
        assert_eq!(map.0.get("logs/sub/c"), None);
        assert_eq!(map.0.get("logs/b"), Some(2).as_ref());
        assert_eq!(map.0.get("other/a"), Some(1).as_ref());
        assert_eq!(map.0.get("logs/#"), Some(1).as_ref());

        // Wildcard combinations work properly
        assert_eq!(map.insert_with_replace("valve/#".to_string(), 1), None);
        assert_eq!(map.insert_with_replace("valve/+/#".to_string(), 1), None);
        assert_eq!(map.insert_with_replace("valve/+/+".to_string(), 1), None);

        assert_eq!(map.0.get("valve/#"), Some(1).as_ref());
        assert_eq!(map.0.get("valve/+/#"), Some(1).as_ref());
        assert_eq!(map.0.get("valve/+/+"), Some(1).as_ref());

        // Exact key re-insert returns the previous value for that key
        let replaced_exact = map.insert_with_replace("logs/#".to_string(), 99);
        assert_eq!(replaced_exact, Some(1));
        assert_eq!(map.0.get("logs/#"), Some(99).as_ref());

        // Single-level wildcard (+) only evicts matching depth with the same value
        map.insert_with_replace("metrics/cpu".to_string(), 42);
        map.insert_with_replace("metrics/ram".to_string(), 100); // different value
        map.insert_with_replace("metrics/disk/io".to_string(), 42); // different depth

        let replaced_plus = map.insert_with_replace("metrics/+".to_string(), 42);
        assert_eq!(replaced_plus, None);

        assert_eq!(map.0.get("metrics/cpu"), None); // Evicted (value 42, 1 level)
        assert_eq!(map.0.get("metrics/ram"), Some(100).as_ref()); // Kept (different value)
        assert_eq!(map.0.get("metrics/disk/io"), Some(42).as_ref()); // Kept (depth 2 vs '+')
        assert_eq!(map.0.get("metrics/+"), Some(42).as_ref());
    }
}
