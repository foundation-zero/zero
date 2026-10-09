use std::collections::BTreeMap;

#[derive(Debug, Clone)]
pub struct TopicMap<T>(BTreeMap<String, T>);

impl<T> TopicMap<T> {
    pub fn new() -> Self {
        Self(BTreeMap::new())
    }

    #[must_use]
    pub fn get(&self, topic: &str) -> Option<&T> {
        // Wildcard patterns (from parametrized topic groups) match any of
        // their concrete topics.
        self.0
            .range(..=topic.to_owned())
            .rev()
            .find(|(pattern, _)| mqtt_pattern_matches(pattern, topic))
            .map(|(_, value)| Some(value))?
    }

    #[cfg(test)]
    pub fn len(&self) -> usize {
        self.0.len()
    }

    #[cfg(test)]
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    #[allow(dead_code)]
    pub(crate) fn covers_topic(&self, key: &str) -> bool {
        self.get(key).is_some()
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
            (Some("+"), Some(_)) => {}
            (Some(p), Some(t)) if p == t => {}
            _ => return false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
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

    #[test]
    fn test_pattern_matches_plus_single_level() {
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

    #[test]
    fn test_pattern_matches_hash_matches_remaining_levels() {
        assert!(mqtt_pattern_matches("logs/#", "logs/a"));
        assert!(mqtt_pattern_matches("logs/#", "logs/a/b/c"));
        // `#` also matches zero remaining levels (the prefix topic itself).
        assert!(mqtt_pattern_matches("logs/#", "logs"));
    }

    #[test]
    fn test_pattern_matches_rejects_different_prefix() {
        assert!(!mqtt_pattern_matches("logs/#", "metrics/a"));
        assert!(!mqtt_pattern_matches(
            "power-tags/+/+",
            "power-tags-other/10P1/slug"
        ));
    }

    #[test]
    fn test_pattern_matches_rejects_pattern_longer_than_topic() {
        assert!(!mqtt_pattern_matches("power-tags/+/+", "power-tags/10P1"));
    }

    #[test]
    fn test_topics_return_value_in_correct_order() {
        let topic_map: TopicMap<_> = [
            ("power-tags/#".to_string(), 1),
            ("power-tags/+".to_string(), 2),
            ("power-tags/+/+".to_string(), 3),
            ("power-tags/aaaa".to_string(), 4),
            ("power-tags/aaaa/bbbb".to_string(), 5),
            ("logs/#".to_string(), 10),
        ]
        .into_iter()
        .collect();
        assert_eq!(*topic_map.get("power-tags/aaaa/bbbb").unwrap(), 5);
        assert_eq!(*topic_map.get("power-tags/aaaa/cccc").unwrap(), 3);
        assert_eq!(*topic_map.get("power-tags/aaaa").unwrap(), 4);
        assert_eq!(*topic_map.get("power-tags/10P1/slug").unwrap(), 3);
        assert_eq!(*topic_map.get("power-tags/cccc").unwrap(), 2);
        assert_eq!(*topic_map.get("power-tags/aaaa/bbbb/cccc").unwrap(), 1);
        assert_eq!(*topic_map.get("logs/a/b").unwrap(), 10);
        assert!(topic_map.get("other/topic").is_none());
    }

    #[test]
    fn test_covers_topic() {
        let topic_map: TopicMap<_> = [
            ("power-tags/#".to_string(), ()),
            ("power-tags/+".to_string(), ()),
            ("power-tags/+/+".to_string(), ()),
            ("power-tags/aaaa".to_string(), ()),
            ("power-tags/aaaa/bbbb".to_string(), ()),
            ("logs/#".to_string(), ()),
        ]
        .into_iter()
        .collect();
        assert!(topic_map.covers_topic("power-tags/aaaa/bbbb"));
        assert!(topic_map.covers_topic("power-tags/aaaa/cccc"));
        assert!(topic_map.covers_topic("power-tags/aaaa"));
        assert!(topic_map.covers_topic("power-tags/10P1/slug"));
        assert!(topic_map.covers_topic("power-tags/cccc"));
        assert!(topic_map.covers_topic("power-tags/aaaa/bbbb/cccc"));
        assert!(topic_map.covers_topic("logs/a/b"));
        assert!(!topic_map.covers_topic("other/topic"));
    }
}
