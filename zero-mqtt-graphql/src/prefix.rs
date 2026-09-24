use crate::asyncapi::{TopicDef, TopicGroupDef, ValidatorSpec};
use crate::config::{AppConfig, PrefixStrategy};
use crate::extension::GraphqlExtension;

/// Leading-prefix substitutions from spec prefixes to the live broker's
/// (`PREFIX_STRATEGY=runtime`); `from` matches whole segments only.
#[derive(Debug, Clone, Default)]
pub struct PrefixRewriter {
    rules: Vec<(String, String)>,
}

impl PrefixRewriter {
    /// Build the rewriter; a no-op unless the runtime strategy sets a differing prefix.
    pub fn from_config(config: &AppConfig) -> Self {
        if config.prefix_strategy != PrefixStrategy::Runtime {
            return Self::default();
        }
        let mut rules = Vec::new();
        // Controller first: its default is the more specific prefix.
        push_rule(
            &mut rules,
            &config.spec_controller_prefix,
            config.mqtt_controller_topic_prefix.as_deref(),
        );
        push_rule(
            &mut rules,
            &config.spec_simulator_prefix,
            config.mqtt_simulator_topic_prefix.as_deref(),
        );
        push_rule(
            &mut rules,
            &config.spec_devices_prefix,
            config.mqtt_devices_topic_prefix.as_deref(),
        );
        Self { rules }
    }

    /// True when no rule would ever change a topic.
    pub fn is_noop(&self) -> bool {
        self.rules.is_empty()
    }

    /// Rewrite a single topic, returning it unchanged when no rule matches.
    pub fn rewrite(&self, topic: &str) -> String {
        for (from, to) in &self.rules {
            if topic == from {
                return to.clone();
            }
            if let Some(rest) = topic.strip_prefix(from) {
                if rest.starts_with('/') {
                    return format!("{to}{rest}");
                }
            }
        }
        topic.to_string()
    }

    /// Rewrite each topic def's subscribe/cache topic in place.
    pub fn apply_to_topics(&self, topics: &mut [TopicDef]) {
        if self.is_noop() {
            return;
        }
        for topic in topics {
            topic.topic = self.rewrite(&topic.topic);
        }
    }

    /// Rewrite each topic-group wildcard pattern in place.
    pub fn apply_to_groups(&self, groups: &mut [TopicGroupDef]) {
        if self.is_noop() {
            return;
        }
        for group in groups {
            group.pattern = self.rewrite(&group.pattern);
        }
    }

    /// Rewrite the topic each validator is keyed by in place.
    pub fn apply_to_validators(&self, validators: &mut [ValidatorSpec]) {
        if self.is_noop() {
            return;
        }
        for (topic, _) in validators {
            *topic = self.rewrite(topic);
        }
    }

    /// Rewrite every resolved topic of the extension in place.
    pub fn apply_to_extension(&self, extension: &mut GraphqlExtension) {
        if self.is_noop() {
            return;
        }
        extension.rewrite_topics(&|topic| self.rewrite(topic));
    }
}

fn push_rule(rules: &mut Vec<(String, String)>, from: &str, to: Option<&str>) {
    if let Some(to) = to {
        if !to.is_empty() && to != from && !from.is_empty() {
            rules.push((from.to_string(), to.to_string()));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn cfg(strategy: PrefixStrategy, dev: Option<&str>, ctrl: Option<&str>) -> AppConfig {
        AppConfig {
            mqtt_host: "localhost".into(),
            mqtt_port: 1883,
            mqtt_username: None,
            mqtt_password: None,
            listen_port: 5103,
            default_ttl_secs: 300,
            strict_validation: false,
            enable_optional_sensor_values: false,
            enable_mutations: false,
            prefix_strategy: strategy,
            spec_devices_prefix: "simulation".into(),
            spec_controller_prefix: "thrs/controller".into(),
            mqtt_devices_topic_prefix: dev.map(str::to_string),
            mqtt_controller_topic_prefix: ctrl.map(str::to_string),
            spec_simulator_prefix: "thrs/simulator".into(),
            mqtt_simulator_topic_prefix: None,
        }
    }

    #[test]
    fn build_time_strategy_is_noop_even_with_runtime_prefixes() {
        let r = PrefixRewriter::from_config(&cfg(
            PrefixStrategy::BuildTime,
            Some("devices_topic"),
            Some("controller_topic"),
        ));
        assert!(r.is_noop());
        assert_eq!(
            r.rewrite("simulation/500000-thrs/thrusters/x"),
            "simulation/500000-thrs/thrusters/x"
        );
    }

    #[test]
    fn runtime_rewrites_both_devices_and_controller_prefixes() {
        let r = PrefixRewriter::from_config(&cfg(
            PrefixStrategy::Runtime,
            Some("devices_topic"),
            Some("controller_topic"),
        ));
        assert!(!r.is_noop());
        assert_eq!(
            r.rewrite("simulation/500000-thrs/thrusters/thrusters-flow-aft"),
            "devices_topic/500000-thrs/thrusters/thrusters-flow-aft"
        );
        assert_eq!(
            r.rewrite("thrs/controller/thrusters/parameters/set"),
            "controller_topic/thrusters/parameters/set"
        );
    }

    #[test]
    fn runtime_with_no_overrides_is_noop() {
        let r = PrefixRewriter::from_config(&cfg(PrefixStrategy::Runtime, None, None));
        assert!(r.is_noop());
    }

    #[test]
    fn runtime_ignores_prefix_equal_to_spec() {
        let r = PrefixRewriter::from_config(&cfg(
            PrefixStrategy::Runtime,
            Some("simulation"),
            Some("controller_topic"),
        ));
        // Only the controller rule survives; the devices "override" equals the
        // spec value so it is dropped.
        assert_eq!(
            r.rewrite("simulation/500000-thrs/thrusters/x"),
            "simulation/500000-thrs/thrusters/x"
        );
        assert_eq!(
            r.rewrite("thrs/controller/thrusters/parameters"),
            "controller_topic/thrusters/parameters"
        );
    }

    #[test]
    fn runtime_rewrites_validator_topics_and_patterns() {
        let rewriter =
            PrefixRewriter::from_config(&cfg(PrefixStrategy::Runtime, Some("devices_topic"), None));
        let mut validators = vec![
            ("simulation/a/b".to_string(), serde_json::json!({})),
            ("simulation/+/b".to_string(), serde_json::json!({})),
            ("other/x".to_string(), serde_json::json!({})),
        ];
        rewriter.apply_to_validators(&mut validators);
        let topics: Vec<&str> = validators.iter().map(|(t, _)| t.as_str()).collect();
        assert_eq!(
            topics,
            vec!["devices_topic/a/b", "devices_topic/+/b", "other/x"]
        );
    }

    #[test]
    fn does_not_rewrite_a_non_segment_prefix_match() {
        let r =
            PrefixRewriter::from_config(&cfg(PrefixStrategy::Runtime, Some("devices_topic"), None));
        // "simulation-extra" shares the "simulation" text but is a different
        // top segment, so it must be left untouched.
        assert_eq!(r.rewrite("simulation-extra/x"), "simulation-extra/x");
    }
}
