use jsonschema::{Registry, Resource, Validator};
use log::{info, warn};
use serde_json::{Value, json};

use crate::{api_model::TopicDef, topic_map::TopicMap};

#[derive(Debug, Clone)]
pub struct ValidatorBuilder<'a> {
    registry: Registry<'a>,
}

const ROOT_DOC_URI: &str = "urn:asyncapi:doc";

impl ValidatorBuilder<'_> {
    pub fn new(document_json: Value) -> anyhow::Result<Self> {
        let registry: Registry<'_> = Registry::new()
            .add(ROOT_DOC_URI, Resource::from_contents(document_json))?
            .prepare()?;

        Ok(Self { registry })
    }

    pub fn build_validator(&self, payload_schema_ref: &str) -> anyhow::Result<Validator> {
        let json_reference = json!({"$ref": format!("{ROOT_DOC_URI}{payload_schema_ref}")});

        Ok(jsonschema::options()
            .with_registry(&self.registry)
            .build(&json_reference)?)
    }
}

/// Compile one validator per topic into a map keyed by its topic: an exact
/// topic, or a wildcard filter for a Group (e.g. `power-tags/+/+`).
pub fn build_validators(
    validator_builder: &ValidatorBuilder,
    topics: &[TopicDef],
) -> anyhow::Result<TopicMap<Validator>> {
    let validators: Vec<(String, Validator)> = topics
        .iter()
        .filter_map(|td| {
            let payload_schema_ref = td.payload_schema_ref.clone()?;
            match validator_builder.build_validator(&payload_schema_ref) {
                Ok(validator) => Some((td.topic.clone(), validator)),
                Err(e) => {
                    warn!(
                        "Failed to compile JSON Schema for topic '{}': {e} — skipping validation for this topic",
                        td.topic
                    );
                    None
                }
            }
        })
        .collect();
    if !validators.is_empty() {
        info!(
            "Compiled JSON Schema validators for {} topic(s)",
            validators.len()
        );
    }

    Ok(validators.into_iter().collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::{GraphqlType, GroupDef, TopicKind};
    use crate::roas_asyncapi::OperationAction;
    use serde_json::json;
    use std::collections::BTreeMap;

    fn group_with_schema(topic: &str, schema: Option<String>) -> TopicDef {
        TopicDef {
            topic: topic.to_string(),
            fields: BTreeMap::from_iter(vec![(
                "active_power_total".to_string(),
                GraphqlType::Float,
            )]),
            payload_schema_ref: schema,
            action: OperationAction::Send,
            ttl_secs: None,
            kind: TopicKind::Group(GroupDef {
                value_extensions: BTreeMap::new(),
                group_by: String::new(),
                topic_metadata: BTreeMap::new(),
            }),
        }
    }

    #[test_log::test]
    fn test_build_validators_compiles_topic_schema() {
        let validator_builder = ValidatorBuilder::new(
            json!({"validator":{"type": "object", "required": ["active_power_total"]}}),
        )
        .unwrap();

        let topics = vec![TopicDef {
            topic: "power-tags".to_string(),
            fields: BTreeMap::from_iter(vec![(
                "active_power_total".to_string(),
                GraphqlType::Float,
            )]),
            payload_schema_ref: Some("#/validator".to_string()),
            action: OperationAction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let validators = build_validators(&validator_builder, &topics).unwrap();

        let validator = validators.get("power-tags");
        assert!(validator.is_some());

        let validator = validator.unwrap();
        assert!(validator.validate(&json!({})).is_err());
        assert_eq!(
            validator
                .validate(&json!({"active_power_total": 0.0}))
                .unwrap(),
            ()
        );
    }

    #[test_log::test]
    fn test_build_validators_compiles_group_schema() {
        let validator_builder = ValidatorBuilder::new(
            json!({"validator":{"type": "object", "required": ["active_power_total"]}}),
        )
        .unwrap();

        let groups = vec![group_with_schema(
            "power-tags/+/+",
            Some("#/validator".to_string()),
        )];

        let validators = build_validators(&validator_builder, &groups).unwrap();

        let validator = &validators.get("power-tags/+/+");
        assert!(validator.is_some());

        let validator = validator.unwrap();
        assert!(validator.validate(&json!({})).is_err());
        assert_eq!(
            validator
                .validate(&json!({"active_power_total": 0.0}))
                .unwrap(),
            ()
        );
    }

    #[test_log::test]
    fn test_build_validators_skips_group_without_schema() {
        let validator_builder = ValidatorBuilder::new(json!({})).unwrap();

        let groups = vec![group_with_schema("power-tags/+/+", None)];

        let validators = build_validators(&validator_builder, &groups).unwrap();
        assert!(validators.is_empty());
    }

    #[test_log::test]
    fn test_complex_validator() {
        let validator_builder = ValidatorBuilder::new(json!({
            "schemas":{
                "message":{
                    "type": "object",
                    "required": ["active_power_total"],
                    "properties": {
                        "active_power_total": {"$ref": "#/schemas/fieldNumber"}
                    }
                },
                "fieldNumber": {"type": "number"}
            }
        }))
        .unwrap();

        let topics = vec![TopicDef {
            topic: "power-tags".to_string(),
            fields: BTreeMap::from_iter(vec![(
                "active_power_total".to_string(),
                GraphqlType::String,
            )]),
            payload_schema_ref: Some("#/schemas/message".to_string()),
            action: OperationAction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let validators = build_validators(&validator_builder, &topics).unwrap();
        let validator = validators.get("power-tags");
        assert!(validator.is_some());

        let validator = validator.unwrap();
        assert!(validator.validate(&json!({})).is_err());
        assert!(
            validator
                .validate(&json!({"active_power_total": "ss"}))
                .is_err()
        );
        assert_eq!(
            validator
                .validate(&json!({"active_power_total": 0.0}))
                .unwrap(),
            ()
        );
    }
}
