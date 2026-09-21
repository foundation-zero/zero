//! Runtime topic-prefix rewriting.
//!
//! Spec files bake a topic prefix at generation time (THRS
//! `mqtt_devices_topic_prefix` / `mqtt_controller_topic_prefix`, defaulting to
//! `simulation` and `thrs/controller`). When the live broker uses different
//! prefixes, `PREFIX_STRATEGY=runtime` rewrites each spec topic's leading
//! prefix from the "spec" value to the "runtime" value at load time, so the
//! same spec can target a differently-prefixed broker without regeneration.
//!
//! The alternative is baking the correct prefix into the spec directly, via
//! the generator's `--devices-prefix`/`--controller-prefix` flags, and leaving
//! this rewriter disabled.

use crate::asyncapi::{TopicDef, TopicGroupDef, ValidatorSpec};
use crate::config::{AppConfig, PrefixStrategy};
use crate::extension::GraphqlExtension;

/// A set of leading-prefix substitutions applied to MQTT topics.
///
/// Each rule replaces a leading `from` segment-prefix with a `to` one. A topic
/// matches a rule when it equals `from` or starts with `from` followed by `/`,
/// so `simulation` never accidentally rewrites `simulation-extra/...`.
#[derive(Debug, Clone, Default)]
pub struct PrefixRewriter {
    rules: Vec<(String, String)>,
}

impl PrefixRewriter {
    /// Build the rewriter for the active config. Returns an empty (no-op)
    /// rewriter unless `prefix_strategy = runtime` and a runtime prefix is set
    /// that actually differs from the spec prefix.
    pub fn from_config(config: &AppConfig) -> Self {
        if config.prefix_strategy != PrefixStrategy::Runtime {
            return Self::default();
        }
        let mut rules = Vec::new();
        // Controller first: its default (`thrs/controller`) is more specific,
        // and keeping the more-specific rule ahead avoids any future overlap.
        push_rule(
            &mut rules,
            &config.spec_controller_prefix,
            config.runtime_controller_prefix.as_deref(),
        );
        push_rule(
            &mut rules,
            &config.spec_simulator_prefix,
            config.runtime_simulator_prefix.as_deref(),
        );
        push_rule(
            &mut rules,
            &config.spec_devices_prefix,
            config.runtime_devices_prefix.as_deref(),
        );
        Self { rules }
    }

    /// True when no rule would ever change a topic (build-time strategy, or
    /// runtime with no differing prefixes configured).
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

    /// Rewrite the concrete subscribe/cache topic of each flat AsyncAPI topic
    /// def in place. These are the cache keys the read resolvers hit, so they
    /// must move in lockstep with the module-view topics.
    pub fn apply_to_topics(&self, topics: &mut [TopicDef]) {
        if self.is_noop() {
            return;
        }
        for topic in topics {
            topic.topic = self.rewrite(&topic.topic);
        }
    }

    /// Rewrite each topic-group wildcard pattern in place. THRS prefixes never
    /// match the non-THRS groups (e.g. `power-tags/+/+`), so this is a no-op for
    /// them, but it keeps any future prefixed group correct.
    pub fn apply_to_groups(&self, groups: &mut [TopicGroupDef]) {
        if self.is_noop() {
            return;
        }
        for group in groups {
            group.pattern = self.rewrite(&group.pattern);
        }
    }

    /// Rewrite the topic (or pattern) each validator is keyed by in place, so
    /// payloads on the live-broker topics are checked against their schemas.
    pub fn apply_to_validators(&self, validators: &mut [ValidatorSpec]) {
        if self.is_noop() {
            return;
        }
        for (topic, _) in validators {
            *topic = self.rewrite(topic);
        }
    }

    /// Rewrite every resolved topic of the extension (view sections, mutation
    /// state/target topics, lifecycle status/objects/directives) in place.
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
            runtime_devices_prefix: dev.map(str::to_string),
            runtime_controller_prefix: ctrl.map(str::to_string),
            spec_simulator_prefix: "thrs/simulator".into(),
            runtime_simulator_prefix: None,
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
