//! The mutations of the extension: what a document declares for a write,
//! and how it resolves to the runtime [`MutationDef`].
//!
//! A mutation names the `receive` operation it publishes to and, for the
//! kinds that modify a cached object, the `send` operation whose messages
//! carry that object. That object's declared type supplies the rest: the
//! argument's scalar type and bounds (`setField`), the component's input
//! fields (`setComponent`), and the `x-invariants` / `x-derived` the
//! republished object must honour.

use std::borrow::Cow;

use anyhow::Context;
use roas_asyncapi::v3_0::operation::OperationAction;
use serde::Deserialize;

use super::{OperationRef, Resolver};
use crate::mutations_view::{ConfirmDef, InputFieldDef, MutationDef, MutationKind};
use crate::schema::Property;

/// How a mutation is confirmed before it returns (see [`ConfirmDef`]).
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct ConfirmSpec {
    #[serde(default)]
    pub operation: Option<OperationRef>,
    #[serde(default)]
    pub key: Option<String>,
    #[serde(default)]
    pub presence: bool,
    pub timeout_s: f64,
    pub timeout_error: String,
}

/// One mutation as the document declares it.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct MutationSpec {
    /// GraphQL mutation field name, e.g. `thrustersParameterSetCoolingFlow`.
    pub gql: String,
    pub kind: MutationKind,
    /// Name of the GraphQL argument.
    pub arg_name: String,
    /// Wire key in the object to overwrite (`setField`/`setComponent`), or
    /// the key of the fresh object (`setFlag`).
    pub key: String,
    /// `setField`/`setComponent`: the `send` operation whose messages carry
    /// the object to modify.
    #[serde(default)]
    pub state: Option<OperationRef>,
    /// The `receive` operation the object is published to.
    pub target: OperationRef,
    /// The `object` section of the member the mutation returns. None returns
    /// `Boolean!`.
    #[serde(default)]
    pub returns: Option<String>,
    /// `setFlag`: the `key` value when the Boolean argument is true / false.
    #[serde(default)]
    pub true_value: Option<String>,
    #[serde(default)]
    pub false_value: Option<String>,
    /// `setComponent`: the GraphQL input type name (`PumpInputType`, shared
    /// wherever the component type is).
    #[serde(default)]
    pub input_type_name: Option<String>,
    /// The error when nothing is cached at the state topic to modify.
    #[serde(default)]
    pub missing_error: Option<String>,
    #[serde(default)]
    pub confirm: Option<ConfirmSpec>,
}

impl MutationSpec {
    /// Resolve against the member's `object` sections (GraphQL name -> type
    /// name): the object a mutation modifies is the section it returns, so
    /// that section's type supplies the argument and input shapes.
    pub fn resolve(
        &self,
        resolver: &Resolver<'_>,
        sections: &[(&str, &str)],
    ) -> anyhow::Result<MutationDef> {
        let context = |what: &str| format!("mutation '{}' {what}", self.gql);
        let set_topic = self
            .target
            .resolve(resolver.operations, OperationAction::Receive)
            .with_context(|| context("target"))?;

        let mut def = MutationDef {
            gql: self.gql.clone(),
            kind: self.kind,
            arg_type: String::new(),
            arg_name: self.arg_name.clone(),
            key: self.key.clone(),
            state: self.state.clone(),
            target: Some(self.target.clone()),
            state_topic: String::new(),
            set_topic,
            returns: self.returns.clone(),
            bounds: None,
            true_value: self.true_value.clone(),
            false_value: self.false_value.clone(),
            input_fields: Vec::new(),
            derived: Vec::new(),
            input_type_name: self.input_type_name.clone(),
            missing_error: self.missing_error.clone(),
            confirm: None,
            invariants: Vec::new(),
        };

        match self.kind {
            MutationKind::SetFlag => {
                if self.true_value.is_none() || self.false_value.is_none() {
                    anyhow::bail!("{}", context("needs both trueValue and falseValue"));
                }
                def.arg_type = "Boolean".to_string();
            }
            MutationKind::SetField | MutationKind::SetComponent => {
                let state = self
                    .state
                    .as_ref()
                    .with_context(|| context("names no state"))?;
                let operation = state
                    .operation(resolver.operations, OperationAction::Send)
                    .with_context(|| context("state"))?;
                def.state_topic = operation
                    .topic(&state.parameters)
                    .with_context(|| context("state"))?;
                let returned = self
                    .returns
                    .as_deref()
                    .and_then(|gql| sections.iter().find(|(name, _)| *name == gql))
                    .map(|(_, type_name)| type_name);
                let state_type = match returned {
                    Some(type_name) => Cow::Borrowed(resolver.types.get(type_name)?),
                    None => resolver
                        .types
                        .for_operation(operation, &state.parameters)
                        .with_context(|| context("state"))?,
                };
                let property = state_type
                    .property(&self.key)
                    .with_context(|| context("key"))?;
                match (self.kind, property) {
                    (MutationKind::SetField, Property::Scalar(scalar)) => {
                        def.arg_type = scalar.r#type.clone();
                        def.bounds = scalar.bounds.clone();
                        def.invariants = state_type.invariants.clone();
                    }
                    (MutationKind::SetField, _) => {
                        anyhow::bail!("{}", context("sets a key that is not a scalar"))
                    }
                    (MutationKind::SetComponent, Property::Object(_)) => {
                        if self.input_type_name.is_none() {
                            anyhow::bail!("{}", context("has no inputTypeName"));
                        }
                        let component = resolver
                            .types
                            .shape_of_property(&state_type.document, &self.key, property)
                            .with_context(|| context("key"))?;
                        def.input_fields = component
                            .leaves(&Default::default())
                            .into_iter()
                            .map(|leaf| InputFieldDef {
                                gql: leaf.gql,
                                key: leaf.key,
                                r#type: leaf.r#type,
                                enum_values: leaf.enum_values,
                                enum_type: leaf.enum_type,
                                required: !leaf.optional,
                            })
                            .collect();
                        if def.input_fields.is_empty() {
                            anyhow::bail!("{}", context("sets a component without stamped leaves"));
                        }
                        def.derived = state_type.derived.clone();
                    }
                    (MutationKind::SetComponent, _) => {
                        anyhow::bail!("{}", context("sets a key that is not a component"))
                    }
                    (MutationKind::SetFlag, _) => unreachable!(),
                }
            }
        }

        if let Some(confirm) = &self.confirm {
            let topic = match &confirm.operation {
                Some(operation) => operation
                    .resolve(resolver.operations, OperationAction::Send)
                    .with_context(|| context("confirm"))?,
                None if !def.state_topic.is_empty() => def.state_topic.clone(),
                None => anyhow::bail!(
                    "{}",
                    context("confirm names no operation and the mutation has no state")
                ),
            };
            def.confirm = Some(ConfirmDef {
                operation: confirm.operation.clone(),
                topic,
                key: confirm.key.clone(),
                presence: confirm.presence,
                timeout_s: confirm.timeout_s,
                timeout_error: confirm.timeout_error.clone(),
            });
        }
        Ok(def)
    }
}

#[cfg(test)]
mod tests {
    use super::super::fixtures::*;
    use super::*;
    use crate::mutations_view::Bounds;
    use serde_json::json;

    fn mutations() -> Vec<MutationDef> {
        resolved(extension_json())
            .unwrap()
            .views
            .remove(0)
            .members
            .remove(0)
            .mutations
    }

    #[test]
    fn test_set_field_reads_scalar_bounds_and_invariants_off_the_state_type() {
        let m = &mutations()[0];
        assert_eq!(m.arg_type, "Float");
        assert_eq!(m.state_topic, "ctl/thrusters/parameters");
        assert_eq!(m.set_topic, "ctl/thrusters/parameters/set");
        assert_eq!(
            m.bounds,
            Some(Bounds {
                min: Some(0.0),
                ..Bounds::default()
            })
        );
        assert_eq!(m.invariants.len(), 1);
        assert_eq!(m.confirm_topic(), Some("ctl/thrusters/parameters"));
    }

    #[test]
    fn test_set_component_reads_input_fields_and_derived_off_the_component_type() {
        let m = &mutations()[1];
        assert_eq!(m.input_type_name(), "PumpInputType");
        let names: Vec<(&str, bool)> = m
            .input_fields
            .iter()
            .map(|f| (f.gql.as_str(), f.required))
            .collect();
        assert_eq!(names, vec![("dutypoint", true), ("controlMode", true)]);
        assert_eq!(m.input_fields[1].enum_type.as_deref(), Some("Mode"));
        assert_eq!(m.derived.len(), 1);
        assert!(m.confirm.is_none());
    }

    #[test]
    fn test_set_flag_needs_no_state_and_confirms_on_its_own_operation() {
        let m = &mutations()[2];
        assert_eq!(m.arg_type, "Boolean");
        assert!(m.state_topic.is_empty());
        assert_eq!(m.confirm_topic(), Some("ctl/thrusters/control-mode"));
        assert!(m.confirm.as_ref().unwrap().presence);
    }

    #[test]
    fn test_target_must_be_a_receive_operation() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["mutations"][0]["target"]["operation"] =
            json!("ctl.parameters.send");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("expected receive"), "{err:#}");
    }

    #[test]
    fn test_kind_and_key_must_agree_with_the_state_type() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["mutations"][0]["key"] = json!("Nope");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("no property 'Nope'"), "{err:#}");

        let mut json = extension_json();
        json["views"][0]["members"][0]["mutations"][1]["kind"] = json!("setField");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("not a scalar"), "{err:#}");

        let mut json = extension_json();
        json["views"][0]["members"][0]["mutations"][1]
            .as_object_mut()
            .unwrap()
            .remove("inputTypeName");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("inputTypeName"), "{err:#}");
    }

    #[test]
    fn test_returns_must_name_an_object_section_of_the_member() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["mutations"][0]["returns"] = json!("sensorValues");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("unknown section"), "{err:#}");
    }
}
