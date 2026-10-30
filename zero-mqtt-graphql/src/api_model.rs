use std::collections::BTreeMap;

use crate::{metadata::MetadataByTopic, roas_asyncapi::OperationAction};
use jsonschema::Validator;

use crate::topic_map::TopicMap;

#[derive(Debug, Clone)]
pub struct TopicDef {
    pub topic: String,
    pub fields: BTreeMap<String, GraphqlType>,
    /// Pointer to payload in json reference format (e.g. #/components/schemas/field)
    pub payload_schema_ref: Option<String>,
    /// TTL in seconds for cached values of this topic. Determined from
    /// `x-ttl` extensions on the AsyncAPI message or channel
    /// (per-schema override) or a global default.
    pub ttl_secs: u64,
    pub action: OperationAction,
}

/// A parametrized topic family declared by a single channel, e.g.
/// address `power-tags/{panel}/{slug}`.
#[derive(Debug, Clone)]
pub struct TopicGroupDef {
    /// Static prefix of the address (`power-tags`); seeds the GraphQL names.
    pub group: String,
    /// Wildcard MQTT topic to subscribe to (`power-tags/+/+`).
    pub pattern: String,
    pub fields: BTreeMap<String, GraphqlType>,
    /// Raw JSON Schema value for the payload.
    pub payload_schema_ref: Option<String>,
    /// Extension attributes per payload field (`x-*` schema extensions
    /// minus the prefix), keyed by raw field name.
    pub ttl_secs: u64,
    pub action: OperationAction,
    pub value_extensions: BTreeMap<String, BTreeMap<String, String>>,
    pub topic_metadata: MetadataByTopic,
    pub group_by: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum GraphqlType {
    Object(Box<BTreeMap<String, GraphqlType>>),
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
    pub groups: Vec<TopicGroupDef>,
    pub validators: TopicMap<Validator>,
}

impl ApiModel {
    #[must_use]
    pub fn new(
        name: String,
        subscribe_topics: TopicMap<()>,
        topics: Vec<TopicDef>,
        groups: Vec<TopicGroupDef>,
        validators: TopicMap<Validator>,
    ) -> Self {
        Self {
            name,
            subscribe_topics,
            topics,
            groups,
            validators,
        }
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.topics.is_empty() && self.groups.is_empty()
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
    /// keyed by topic, groups by their wildcard pattern so every concrete
    /// topic under them inherits the group's `x-ttl`.
    #[must_use]
    pub fn ttl_map(&self, default_ttl: u64) -> TopicMap<u64> {
        let topic_overrides = self
            .models
            .iter()
            .flat_map(|model| &model.topics)
            .filter(|t| t.ttl_secs != default_ttl)
            .map(|t| (t.topic.clone(), t.ttl_secs));

        let group_overrides = self
            .models
            .iter()
            .flat_map(|model| &model.groups)
            .filter(|g| g.ttl_secs != default_ttl)
            .map(|g| (g.pattern.clone(), g.ttl_secs));
        topic_overrides.chain(group_overrides).collect()
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
            vec![],
            TopicMap::new(),
        )]);

        assert!(api.is_empty());

        let api_not_empty = Api::new(vec![ApiModel::new(
            "test".to_owned(),
            TopicMap::new(),
            vec![TopicDef {
                topic: "".to_owned(),
                fields: BTreeMap::new(),
                payload_schema_ref: None,
                ttl_secs: 0,
                action: OperationAction::Send,
            }],
            vec![],
            TopicMap::new(),
        )]);

        assert!(!api_not_empty.is_empty());
    }
}
