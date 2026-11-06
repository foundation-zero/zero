use std::collections::BTreeMap;

use crate::{metadata::MetadataByTopic, roas_asyncapi::OperationAction};
use jsonschema::Validator;

use crate::topic_map::TopicMap;

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
}

#[derive(Debug, Clone, PartialEq)]
pub enum GraphqlType {
    Object(String, Box<BTreeMap<String, GraphqlType>>),
    String,
    Float,
    Int,
    Boolean,
}

#[derive(Debug, Clone)]
pub struct ApiModel {
    pub name: String,
    subscribe_topics: TopicMap<()>,
    pub topics: Vec<TopicDef>,
    pub validators: TopicMap<Validator>,
}

impl ApiModel {
    #[must_use]
    pub fn new(
        name: String,
        subscribe_topics: TopicMap<()>,
        topics: Vec<TopicDef>,
        validators: TopicMap<Validator>,
    ) -> Self {
        Self {
            name,
            subscribe_topics,
            topics,
            validators,
        }
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.topics.is_empty()
    }
}
#[derive(Debug)]

pub struct Api {
    pub(crate) models: Vec<ApiModel>,
}

impl Api {
    #[must_use]
    pub fn new(models: Vec<ApiModel>) -> Self {
        Api { models }
    }

    /// Topics to subscribe on.
    ///
    /// This set will not be exactly the same as the topics that are exposed in the graphql schemas.
    /// We want to work as much as we can with mqtt wildcards
    #[must_use]
    pub fn subscribe_topics(&self) -> Vec<String> {
        self.models
            .iter()
            .flat_map(|model| model.subscribe_topics.keys())
            .cloned()
            .collect()
    }

    /// Build a list of topics
    #[must_use]
    pub fn topics(&self) -> Vec<TopicDef> {
        self.models
            .iter()
            .flat_map(|model| model.topics.clone())
            .collect()
    }

    pub fn is_empty(&self) -> bool {
        self.models.iter().all(ApiModel::is_empty)
    }

    /// Build a set of validators
    ///
    /// This is used in validation incomming mqtt messages
    #[must_use]
    pub fn validators(&self) -> crate::topic_map::TopicMap<jsonschema::Validator> {
        self.models.iter().fold(TopicMap::new(), |acc, model| {
            acc.extend(model.validators.clone())
        })
    }

    /// Build a cache whose TTL table is derived from the AsyncAPI
    /// definitions: topics whose `ttl_secs` differs from `default_ttl` are
    /// keyed by topic; a group's topic is a wildcard filter, so every Member
    /// inherits the group's `x-ttl`.
    #[must_use]
    pub fn ttl_map(&self) -> TopicMap<u64> {
        self.models
            .iter()
            .flat_map(|model| &model.topics)
            .filter_map(|t| Some((t.topic.clone(), t.ttl_secs?)))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test_log::test]
    fn test_api_is_empty() {
        let api = Api::new(vec![ApiModel::new(
            "test".to_owned(),
            TopicMap::new(),
            vec![],
            TopicMap::new(),
        )]);

        assert!(api.is_empty());

        let api_not_empty = Api::new(vec![ApiModel::new(
            "test".to_owned(),
            TopicMap::new(),
            vec![TopicDef {
                topic: "some/topic".to_owned(),
                fields: BTreeMap::new(),
                payload_schema_ref: None,
                ttl_secs: None,
                action: OperationAction::Send,
                kind: TopicKind::Single,
            }],
            TopicMap::new(),
        )]);

        assert!(!api_not_empty.is_empty());
    }
}
