//! The `lifecycles` of the extension: what a document declares for a
//! retained status object with directives, and how it resolves to the
//! runtime [`LifecycleDef`].

use anyhow::Context;
use roas_asyncapi::v3_0::operation::OperationAction;
use serde::Deserialize;

use super::views::ObjectSectionSpec;
use super::{MutationSpec, OperationRef, Resolver};
use crate::lifecycle_view::{
    DirectiveDef, LifecycleDef, LifecycleMemberDef, LifecycleObjectDef, StatusDef, StatusFieldDef,
};
use crate::naming::field_name;
use crate::schema::Property;
use crate::views::ObjectSection;

/// One field exposed off the status object. Its scalar type comes from the
/// status operation's schema.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StatusFieldSpec {
    /// Wire key in the status payload, e.g. `Status`.
    pub key: String,
    /// GraphQL field name. Default: [`field_name`] of the key.
    #[serde(default)]
    pub gql: Option<String>,
}

/// The retained status object.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StatusSpec {
    /// The `send` operation whose messages carry the status object.
    pub operation: OperationRef,
    /// Wire key of the status string (`available`/`running`/...).
    pub key: String,
    #[serde(default)]
    pub fields: Vec<StatusFieldSpec>,
}

/// One whole object relayed next to the status, typed by a union of the
/// members' objects.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct LifecycleObjectSpec {
    /// GraphQL field name on the state object, e.g. `inputs`.
    pub gql: String,
    /// The `send` operation whose messages carry the object.
    pub operation: OperationRef,
    /// The union type name, e.g. `SimulationInputsType`.
    pub union_type: String,
    /// Which `object` section of each member forms this union, e.g. `inputs`.
    pub member_section: String,
}

/// One directive (play / pause / step). Its argument, when it has one, is
/// the `key` property of the target operation's schema: that supplies the
/// scalar type, whether it is required, its default and its bounds.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct DirectiveSpec {
    /// GraphQL mutation name (`simulationPlay`).
    pub gql: String,
    /// The `receive` operation the directive message is published to.
    pub target: OperationRef,
    /// Wire key of the argument in the published message; none for a
    /// directive without an argument.
    #[serde(default)]
    pub key: Option<String>,
    /// GraphQL argument name. Default: [`field_name`] of the key.
    #[serde(default)]
    pub arg_name: Option<String>,
    /// Statuses the directive is accepted from.
    #[serde(default)]
    pub allowed_from: Vec<String>,
    /// Status the directive waits for after publishing.
    #[serde(default)]
    pub expect_status: String,
    /// Error when the current status is not in `allowed_from`.
    #[serde(default)]
    pub precondition_error: String,
    /// Error when no status is cached.
    #[serde(default)]
    pub missing_error: String,
}

/// One member: its `object` sections (whole objects that live on the
/// lifecycle's relayed topics, so they name no operation of their own) and
/// the `setComponent` mutations on them.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct LifecycleMemberSpec {
    /// camelCase name, e.g. `highTemperature`.
    pub name: String,
    #[serde(default)]
    pub sections: Vec<LifecycleSectionSpec>,
    #[serde(default)]
    pub mutations: Vec<MutationSpec>,
}

/// A member section: an `object` section without an operation.
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(tag = "kind", rename_all = "camelCase")]
pub enum LifecycleSectionSpec {
    Object(ObjectSectionSpec),
}

/// The lifecycle contract.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct LifecycleSpec {
    /// The query field, e.g. `simulation`.
    pub gql: String,
    /// GraphQL type name of the query object (a container).
    pub state_type_name: String,
    pub status: StatusSpec,
    #[serde(default)]
    pub objects: Vec<LifecycleObjectSpec>,
    #[serde(default)]
    pub directives: Vec<DirectiveSpec>,
    /// Seconds a directive waits for the expected status.
    pub wait_timeout_s: f64,
    #[serde(default)]
    pub members: Vec<LifecycleMemberSpec>,
}

impl LifecycleSpec {
    pub fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<LifecycleDef> {
        let context = |what: &str| format!("lifecycle '{}' {what}", self.gql);

        let status_operation = self
            .status
            .operation
            .operation(resolver.operations, OperationAction::Send)
            .with_context(|| context("status"))?;
        let status_type = resolver
            .types
            .for_operation(status_operation, &self.status.operation.parameters)
            .with_context(|| context("status"))?;
        let status_fields = self
            .status
            .fields
            .iter()
            .map(|field| {
                let Property::Scalar(scalar) = status_type.property(&field.key)? else {
                    anyhow::bail!("status field '{}' is not a scalar", field.key);
                };
                Ok(StatusFieldDef {
                    gql: field.gql.clone().unwrap_or_else(|| field_name(&field.key)),
                    key: field.key.clone(),
                    r#type: scalar.r#type.clone(),
                })
            })
            .collect::<anyhow::Result<Vec<_>>>()
            .with_context(|| context("status"))?;
        let status = StatusDef {
            operation: Some(self.status.operation.clone()),
            topic: status_operation
                .topic(&self.status.operation.parameters)
                .with_context(|| context("status"))?,
            key: self.status.key.clone(),
            fields: status_fields,
        };

        let objects = self
            .objects
            .iter()
            .map(|object| {
                Ok(LifecycleObjectDef {
                    gql: object.gql.clone(),
                    operation: Some(object.operation.clone()),
                    topic: object
                        .operation
                        .resolve(resolver.operations, OperationAction::Send)
                        .with_context(|| context(&format!("object '{}'", object.gql)))?,
                    union_type: object.union_type.clone(),
                    member_section: object.member_section.clone(),
                })
            })
            .collect::<anyhow::Result<Vec<_>>>()?;

        let directives = self
            .directives
            .iter()
            .map(|directive| {
                directive
                    .resolve(resolver)
                    .with_context(|| context(&format!("directive '{}'", directive.gql)))
            })
            .collect::<anyhow::Result<Vec<_>>>()?;

        let members = self
            .members
            .iter()
            .map(|member| {
                member
                    .resolve(resolver)
                    .with_context(|| context(&format!("member '{}'", member.name)))
            })
            .collect::<anyhow::Result<Vec<_>>>()?;

        Ok(LifecycleDef {
            gql: self.gql.clone(),
            state_type_name: self.state_type_name.clone(),
            status,
            objects,
            directives,
            wait_timeout_s: self.wait_timeout_s,
            members,
        })
    }
}

impl DirectiveSpec {
    fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<DirectiveDef> {
        let operation = self
            .target
            .operation(resolver.operations, OperationAction::Receive)?;
        let topic = operation.topic(&self.target.parameters)?;
        let mut def = DirectiveDef {
            gql: self.gql.clone(),
            target: Some(self.target.clone()),
            topic,
            arg_name: None,
            key: self.key.clone(),
            arg_required: false,
            default: None,
            model: None,
            allowed_from: self.allowed_from.clone(),
            expect_status: self.expect_status.clone(),
            precondition_error: self.precondition_error.clone(),
            missing_error: self.missing_error.clone(),
        };
        if let Some(key) = &self.key {
            let message_type = resolver
                .types
                .for_operation(operation, &self.target.parameters)?;
            let Property::Scalar(scalar) = message_type.property(key)? else {
                anyhow::bail!("argument '{key}' is not a scalar");
            };
            def.arg_name = Some(self.arg_name.clone().unwrap_or_else(|| field_name(key)));
            // Directive args are numeric (`DirectiveDef.default` is `Option<f64>`).
            // A present-but-non-numeric default would otherwise be silently
            // dropped while `arg_required` stays false, publishing no value for
            // `key`; fail the load instead.
            def.default = match scalar.default.as_ref() {
                Some(value) => Some(value.as_f64().ok_or_else(|| {
                    anyhow::anyhow!("directive argument '{key}' default {value} is not numeric")
                })?),
                None => None,
            };
            def.arg_required = scalar.default.is_none() && !scalar.optional;
            def.model = Some(
                message_type
                    .model
                    .clone()
                    .with_error_url(resolver.validation_error_url),
            );
        }
        Ok(def)
    }
}

impl LifecycleMemberSpec {
    fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<LifecycleMemberDef> {
        let sections = self
            .sections
            .iter()
            .map(|LifecycleSectionSpec::Object(section)| {
                if section.operation.is_some() {
                    anyhow::bail!(
                        "section '{}' names an operation; a member object lives on the lifecycle's relayed topics",
                        section.gql
                    );
                }
                Ok(ObjectSection {
                    gql: section.gql.clone(),
                    section: section
                        .resolve(resolver, false)
                        .with_context(|| format!("section '{}'", section.gql))?,
                })
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        let object_sections: Vec<(&str, &str)> = self
            .sections
            .iter()
            .map(|LifecycleSectionSpec::Object(s)| (s.gql.as_str(), s.type_name.as_str()))
            .collect();
        let mutations = self
            .mutations
            .iter()
            .map(|mutation| mutation.resolve(resolver, &object_sections))
            .collect::<anyhow::Result<Vec<_>>>()?;
        Ok(LifecycleMemberDef {
            name: self.name.clone(),
            sections,
            mutations,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::super::fixtures::*;
    use super::*;
    use serde_json::json;

    fn lifecycle() -> LifecycleDef {
        resolved(extension_json()).unwrap().lifecycles.remove(0)
    }

    #[test]
    fn test_status_directive_and_members_read_their_shapes_off_the_types() {
        let lifecycle = lifecycle();
        assert_eq!(lifecycle.status.topic, "sim/status");
        let fields: Vec<(&str, &str, &str)> = lifecycle
            .status
            .fields
            .iter()
            .map(|f| (f.gql.as_str(), f.key.as_str(), f.r#type.as_str()))
            .collect();
        assert_eq!(
            fields,
            vec![
                ("status", "Status", "String"),
                ("time", "SimulationTime", "DateTime")
            ]
        );
        assert_eq!(lifecycle.read_topics(), vec!["sim/status", "sim/inputs"]);

        let play = &lifecycle.directives[0];
        assert_eq!(play.topic, "sim/play");
        assert_eq!(play.arg_name.as_deref(), Some("playbackRate"));
        assert_eq!(play.default, Some(1.0));
        assert!(!play.arg_required);
        let rejected = play
            .model
            .as_ref()
            .unwrap()
            .validate_model(json!({"PlaybackRate": -1.0}).as_object().unwrap().clone());
        assert!(rejected
            .unwrap_err()
            .contains("Input should be greater than or equal to 0 [type=greater_than_equal"));

        let member = &lifecycle.members[0];
        let inputs = member.section("inputs").unwrap();
        assert!(inputs.topic.is_empty());
        assert_eq!(inputs.fields[0].component_type_name(), "ControlPumpType");
        assert_eq!(member.mutations[0].state_topic, "sim/inputs");
        assert_eq!(member.mutations[0].input_fields.len(), 2);
    }

    #[test]
    fn test_directive_target_must_be_a_receive_operation() {
        let mut json = extension_json();
        json["lifecycles"][0]["directives"][0]["target"]["operation"] = json!("sim.status.send");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("expected receive"), "{err:#}");
    }

    #[test]
    fn test_member_section_must_not_name_an_operation_and_objects_need_it() {
        let mut json = extension_json();
        json["lifecycles"][0]["members"][0]["sections"][0]["operation"] =
            json!({"operation": "sim.inputs.send"});
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("relayed topics"), "{err:#}");

        let mut json = extension_json();
        json["lifecycles"][0]["members"][0]["sections"][0]["gql"] = json!("outputs");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("lacks"), "{err:#}");
    }
}
