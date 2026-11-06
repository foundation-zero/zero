use std::collections::BTreeMap;

use crate::{metadata::MetadataByTopic, roas_asyncapi::OperationAction};
use jsonschema::Validator;

use crate::topic_map::TopicMap;

pub use graphql_path::GraphqlPath;
pub use tree::{PathNode, QueryTree};

mod graphql_path;
mod tree;

/// One MQTT topic, or a parametrized family of them, declared by one channel
/// of a Spec.
#[derive(Debug, Clone)]
pub struct TopicDef {
    /// MQTT topic, or topic filter for a Group:
    /// `thrs/compressor/temperature` or `power-tags/+/+`.
    /// Used for subscribing, TTL, validator lookup and the GraphQL path.
    pub topic: String,
    pub fields: BTreeMap<String, GraphqlType>,
    /// Pointer to payload in json reference format (e.g. #/components/schemas/field)
    /// None means there is no payload
    pub payload_schema_ref: Option<String>,
    /// TTL in seconds for cached values of this topic. Determined from
    /// `x-ttl` extensions on the AsyncAPI message or channel
    /// (per-schema override) or a global default.
    pub ttl_secs: Option<u64>,
    pub action: OperationAction,
    pub kind: TopicKind,
}

/// Whether a [`TopicDef`] is one fixed topic or a Group of Members.
#[derive(Debug, Clone)]
pub enum TopicKind {
    /// One fixed topic, readable as one current value.
    Single,
    /// A parametrized family of Members read together as a collection.
    Group(GroupDef),
}

/// What only a Group has: its Members' static metadata and how to bucket them.
#[derive(Debug, Clone)]
pub struct GroupDef {
    /// Extension attributes per payload field (`x-*` schema extensions
    /// minus the prefix), keyed by raw field name.
    pub value_extensions: BTreeMap<String, BTreeMap<String, String>>,
    pub topic_metadata: MetadataByTopic,
    pub group_by: String,
}

impl TopicDef {
    /// The Group part of this topic, if it is a Group.
    #[must_use]
    pub fn as_group(&self) -> Option<&GroupDef> {
        match &self.kind {
            TopicKind::Single => None,
            TopicKind::Group(group) => Some(group),
        }
    }

    /// Whether this topic belongs in the Query tree: a Send operation with
    /// payload fields. A single topic with MQTT wildcards (`+`, `#`) cannot
    /// form a GraphQL path; a Group's wildcards stand for its Members.
    #[must_use]
    pub fn is_queryable(&self) -> bool {
        let concrete = match self.kind {
            TopicKind::Single => !self
                .topic
                .split('/')
                .any(|level| level == "+" || level == "#"),
            TopicKind::Group(_) => true,
        };
        concrete && !self.fields.is_empty() && self.action == OperationAction::Send
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum GraphqlType {
    Object(String, Box<BTreeMap<String, GraphqlType>>),
    String,
    Float,
    Int,
    Boolean,
}

/// One loaded Spec: what the bridge subscribes to, validates and serves for
/// one AsyncAPI document.
#[derive(Debug, Clone)]
pub struct Spec {
    pub name: String,
    subscribe_topics: TopicMap<()>,
    validators: TopicMap<Validator>,
    /// TTL in seconds per topic or topic filter that sets one, taken from
    /// every topic, also those left out of the Query tree.
    ttl_map: TopicMap<u64>,
    pub query_tree: QueryTree,
}

impl Spec {
    /// Errors on a queryable topic without a GraphQL path, or on a Path
    /// conflict within this Spec.
    pub fn new(
        name: String,
        subscribe_topics: TopicMap<()>,
        topics: Vec<TopicDef>,
        validators: TopicMap<Validator>,
    ) -> anyhow::Result<Self> {
        let ttl_map = topics
            .iter()
            .filter_map(|t| Some((t.topic.clone(), t.ttl_secs?)))
            .collect();
        Ok(Self {
            name,
            subscribe_topics,
            validators,
            ttl_map,
            query_tree: tree::query_tree(topics)?,
        })
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.query_tree.is_empty()
    }
}

#[derive(Debug)]
pub struct Api {
    pub(crate) specs: Vec<Spec>,
}

impl Api {
    #[must_use]
    pub fn new(specs: Vec<Spec>) -> Self {
        Api { specs }
    }

    /// Topics to subscribe on.
    ///
    /// This set will not be exactly the same as the topics that are exposed in the graphql schemas.
    /// We want to work as much as we can with mqtt wildcards
    #[must_use]
    pub fn subscribe_topics(&self) -> Vec<String> {
        self.specs
            .iter()
            .flat_map(|spec| spec.subscribe_topics.keys())
            .cloned()
            .collect()
    }

    pub fn is_empty(&self) -> bool {
        self.specs.iter().all(Spec::is_empty)
    }

    /// Build a set of validators
    ///
    /// This is used in validation incomming mqtt messages
    #[must_use]
    pub fn validators(&self) -> TopicMap<Validator> {
        self.specs.iter().fold(TopicMap::new(), |acc, spec| {
            acc.extend(spec.validators.clone())
        })
    }

    /// The cache's TTL table, derived from the AsyncAPI definitions: topics
    /// with an `x-ttl` are keyed by topic; a group's topic is a wildcard
    /// filter, so every Member inherits the group's `x-ttl`.
    #[must_use]
    pub fn ttl_map(&self) -> TopicMap<u64> {
        self.specs.iter().fold(TopicMap::new(), |acc, spec| {
            acc.extend(spec.ttl_map.clone())
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn topic(topic: &str, ttl_secs: Option<u64>) -> TopicDef {
        TopicDef {
            topic: topic.to_owned(),
            fields: BTreeMap::from([("x".to_owned(), GraphqlType::Float)]),
            payload_schema_ref: None,
            ttl_secs,
            action: OperationAction::Send,
            kind: TopicKind::Single,
        }
    }

    fn spec(topics: Vec<TopicDef>) -> Spec {
        Spec::new("test".to_owned(), TopicMap::new(), topics, TopicMap::new()).unwrap()
    }

    #[test_log::test]
    fn test_api_is_empty() {
        assert!(Api::new(vec![spec(vec![])]).is_empty());
        assert!(!Api::new(vec![spec(vec![topic("some/topic", None)])]).is_empty());
    }

    #[test_log::test]
    fn test_ttl_of_a_topic_left_out_of_the_tree_still_applies() {
        let api = Api::new(vec![spec(vec![topic("marpower/#", Some(30))])]);

        assert!(api.is_empty());
        assert_eq!(api.ttl_map().get("marpower/a/b"), Some(&30));
    }
}
