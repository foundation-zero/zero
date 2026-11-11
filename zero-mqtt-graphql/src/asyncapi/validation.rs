use jsonschema::{Registry, Resource, Validator};
use log::warn;
use serde_json::{Value, json};

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

/// The validator of a topic's payload schema; `None`, with a warning, when
/// the schema does not compile.
pub(super) fn payload_validator(
    validator_builder: &ValidatorBuilder,
    topic: &str,
    schema_ref: &str,
) -> Option<Validator> {
    validator_builder
        .build_validator(schema_ref)
        .inspect_err(|e| {
            warn!(
                "Failed to compile JSON Schema for topic '{topic}': {e} — skipping validation for this topic"
            );
        })
        .ok()
}

#[cfg(test)]
mod tests {
    use super::*;
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
}
