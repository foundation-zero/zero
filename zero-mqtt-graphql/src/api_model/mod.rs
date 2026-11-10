use std::collections::BTreeMap;

use jsonschema::Validator;
use serde_json::Value;

use crate::topic_map::TopicMap;

pub use graphql_path::GraphqlPath;
pub use tree::{PathNode, Tree};

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
    /// What is published on the topic; `None` when it carries no payload.
    pub payload: Option<Payload>,
    /// TTL in seconds for cached values of this topic; `None` uses the
    /// cache's default.
    pub ttl_secs: Option<u64>,
    /// Whether the topic comes from a Send or a Receive operation.
    pub operation: Direction,
    pub kind: TopicKind,
    /// How a client sets this topic, if it can: the Receive topic paired with
    /// this Send topic, or, on an unpaired Receive topic, that topic itself.
    pub setter: Option<Box<Setter>>,
}

/// The Receive topic through which a client sets a [`TopicDef`].
#[derive(Debug, Clone)]
pub struct Setter {
    /// MQTT topic the input is published on: `room/thermostat/set`.
    pub topic: String,
    /// What the input looks like.
    pub payload: Payload,
    /// The JSON Schema of `payload`; inputs are checked against it before
    /// publishing.
    pub validator: Validator,
}

/// The format of a topic's payload.
#[derive(Debug, Clone)]
pub struct Payload {
    /// The name of the payload format, shared by topics that publish the
    /// same format.
    pub name: String,
    /// Payload fields by raw field name.
    pub fields: BTreeMap<String, FieldType>,
}

/// Which way data flows through a topic, seen from the service whose Spec
/// declares it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Direction {
    /// A Send operation: the service publishes on the topic.
    Send,
    /// A Receive operation: the service accepts input on the topic.
    Receive,
}

/// Whether a [`TopicDef`] is one fixed topic or a Group of Members.
#[derive(Debug, Clone)]
pub enum TopicKind {
    /// One fixed topic, readable as one current value.
    Single,
    /// A parametrized family of Members read together as a collection.
    Group(GroupDef),
}

/// Static attributes per Member, keyed by its concrete topic.
pub type MetadataByTopic = BTreeMap<String, BTreeMap<String, Value>>;

/// What only a Group has: its Members' static metadata and how to bucket them.
#[derive(Debug, Clone)]
pub struct GroupDef {
    /// Static attributes per payload field, such as its `unit`, keyed by raw
    /// field name.
    pub field_attributes: BTreeMap<String, BTreeMap<String, String>>,
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
            TopicKind::Single => !self.has_wildcards(),
            TopicKind::Group(_) => true,
        };
        concrete && self.has_fields() && self.operation == Direction::Send
    }

    /// Whether this topic can set state: a single Receive operation with a
    /// payload on a concrete address. A payload without fields is a signal,
    /// such as a pause. Groups are left out.
    #[must_use]
    pub fn is_settable(&self) -> bool {
        matches!(self.kind, TopicKind::Single)
            && !self.has_wildcards()
            && self.payload.is_some()
            && self.operation == Direction::Receive
    }

    /// Whether this topic is a single topic that can report the state a
    /// Receive topic sets.
    fn is_state(&self) -> bool {
        matches!(self.kind, TopicKind::Single) && self.is_queryable()
    }

    fn has_wildcards(&self) -> bool {
        self.topic
            .split('/')
            .any(|level| level == "+" || level == "#")
    }

    fn has_fields(&self) -> bool {
        self.payload.as_ref().is_some_and(|p| !p.fields.is_empty())
    }
}

/// The type of a payload field.
#[derive(Debug, Clone, PartialEq)]
pub enum FieldType {
    Object(String, Box<BTreeMap<String, FieldType>>),
    /// An array whose elements all have this type.
    List(Box<FieldType>),
    /// Any JSON value: an array whose element type is not known, such as a
    /// tuple written with JSON Schema 2020-12 `prefixItems`, which the
    /// AsyncAPI 3.0 (draft-07) parser drops.
    Json,
    /// A string with a fixed set of values, named after its schema.
    Enum(String, Vec<EnumValue>),
    /// A string in JSON Schema `format: date-time`, an RFC 3339 timestamp.
    DateTime,
    String,
    Float,
    Int,
    Boolean,
}

/// One value of a string enum.
#[derive(Debug, Clone, PartialEq)]
pub struct EnumValue {
    /// The GraphQL name: `IN_USE`.
    pub name: String,
    /// The value on the wire: `in use`.
    pub raw: String,
}

/// What a Receive Topic's MQTT topic adds to its State topic's: Receive topic
/// `<state>/set` sets Send topic `<state>`. The same for every Spec for now;
/// it belongs with a Spec's Mount config once that exists.
pub const SET_SUFFIX: &str = "/set";

/// One loaded Spec: what the bridge subscribes to, validates and serves for
/// one AsyncAPI document.
#[derive(Debug, Clone)]
pub struct Spec {
    pub name: String,
    /// The broadest filters covering the Send topics.
    subscribe_topics: TopicMap<()>,
    validators: TopicMap<Validator>,
    /// TTL in seconds per topic or topic filter that sets one, taken from
    /// every topic, also those left out of the Query tree.
    ttl_map: TopicMap<u64>,
    /// The queryable and settable topics at their GraphQL paths; Query and
    /// Mutation are both laid out from it.
    pub tree: Tree,
}

impl Spec {
    /// Errors on a queryable or settable topic without a GraphQL path, or on
    /// a Path conflict within this Spec.
    pub fn new(
        name: String,
        topics: Vec<TopicDef>,
        validators: TopicMap<Validator>,
    ) -> anyhow::Result<Self> {
        let subscribe_topics = topics
            .iter()
            .filter(|t| t.operation == Direction::Send)
            .fold(TopicMap::new(), |mut acc, t| {
                if !acc.covers_topic(&t.topic) {
                    acc.insert_with_replace(t.topic.clone(), ());
                }
                acc
            });
        let ttl_map = topics
            .iter()
            .filter_map(|t| Some((t.topic.clone(), t.ttl_secs?)))
            .collect();
        let tree = tree::tree(topics, &validators, SET_SUFFIX)?;
        Ok(Self {
            name,
            subscribe_topics,
            validators,
            ttl_map,
            tree,
        })
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.tree.is_empty()
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

    /// The cache's TTL table: topics with a TTL are keyed by topic; a
    /// group's topic is a wildcard filter, so every Member inherits the
    /// group's TTL.
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
            payload: Some(Payload {
                name: "payload".to_owned(),
                fields: BTreeMap::from([("x".to_owned(), FieldType::Float)]),
            }),
            ttl_secs,
            operation: Direction::Send,
            setter: None,
            kind: TopicKind::Single,
        }
    }

    fn spec(topics: Vec<TopicDef>) -> Spec {
        Spec::new("test".to_owned(), topics, TopicMap::new()).unwrap()
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
