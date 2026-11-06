use jsonschema::{Registry, Resource, Validator};
use log::warn;
use roas_asyncapi::common::reference::Reference;
use serde_json::{Value, json};

use super::channels::wildcard_from_address;
use super::roas::{Channel, Document};
use super::schema::message_payload;

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

/// The JSON Schema validator of a channel's payload, keyed by its topic: an
/// exact topic, or a wildcard filter for a Group (e.g. `power-tags/+/+`).
/// `None` for a channel without an address or payload, or whose schema does
/// not compile.
pub(super) fn validator_from_channel(
    validator_builder: &ValidatorBuilder,
    channel_ref: &Reference,
    channel: &Channel,
    doc: &Document,
) -> Option<(String, Validator)> {
    let topic = wildcard_from_address(channel.address()?);
    let schema_ref = message_payload(channel_ref, channel, doc)?.schema_ref;
    match validator_builder.build_validator(&schema_ref) {
        Ok(validator) => Some((topic, validator)),
        Err(e) => {
            warn!(
                "Failed to compile JSON Schema for topic '{topic}': {e} — skipping validation for this topic"
            );
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    use super::*;
    use crate::asyncapi::channels::channels_from_document;
    use serde_json::json;

    #[test_log::test]
    fn test_build_validator_compiles_schema() {
        let validator_builder = ValidatorBuilder::new(
            json!({"validator":{"type": "object", "required": ["active_power_total"]}}),
        )
        .unwrap();

        let validator = validator_builder.build_validator("#/validator").unwrap();

        assert!(validator.validate(&json!({})).is_err());
        assert_eq!(
            validator
                .validate(&json!({"active_power_total": 0.0}))
                .unwrap(),
            ()
        );
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

        let validator = validator_builder
            .build_validator("#/schemas/message")
            .unwrap();

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

    #[test_log::test]
    fn test_validators_are_keyed_by_topic_and_skip_channels_without_payload() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "power": {
                    "address": "power/{panel}",
                    "messages": {"Message": {"payload": {"type": "object"}}}
                },
                "bare": {"address": "bare/channel"}
            },
            "operations": {
                "power": {"action": "send", "channel": {"$ref": "#/channels/power"}},
                "bare": {"action": "send", "channel": {"$ref": "#/channels/bare"}}
            }
        });
        let document = serde_json::from_value::<Document>(spec.clone()).unwrap();
        let validator_builder = ValidatorBuilder::new(spec).unwrap();

        let validators = channels_from_document(
            &document,
            Path::new("test"),
            |channel_ref, _, _, channel, doc, _| {
                Ok(validator_from_channel(
                    &validator_builder,
                    channel_ref,
                    channel,
                    doc,
                ))
            },
        )
        .unwrap();

        let topics: Vec<&str> = validators.iter().map(|(topic, _)| topic.as_str()).collect();
        assert_eq!(topics, ["power/+"]);
    }
}
