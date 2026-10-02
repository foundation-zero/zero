use std::collections::BTreeMap;

use anyhow::Context;
use roas_asyncapi::v3_0::operation::OperationAction;
use serde::Deserialize;

use super::{MutationSpec, OperationRef, ResolvedType, Resolver};
use crate::model::views::{
    MemberDef, ObjectFieldDef, ObjectSection, ObjectSectionDef, PlainFieldDef, PlainObjectDef,
    SectionDef, StampedFieldDef, StampedFieldsSection, SwitchSection, SwitchSectionDef, ViewDef,
};
use crate::naming::field_name;
use crate::schema::Property;

/// Input for a [`StampedFieldDef`].
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StampedFieldSpec {
    pub gql: String,
    pub operation: OperationRef,
    /// Default: the type of the operation's payload schema.
    #[serde(default)]
    pub type_name: Option<String>,
    #[serde(default)]
    pub computed: bool,
}

/// Overrides for one property of an `object` section's type; the fields themselves come from the schema.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectFieldSpec {
    pub key: String,
    /// Default: [`field_name`] of the key.
    #[serde(default)]
    pub gql: Option<String>,
    /// Default: the type of the property's schema.
    #[serde(default)]
    pub type_name: Option<String>,
    #[serde(default)]
    pub operation: Option<OperationRef>,
    /// Type key -> device payload key, e.g. `Dutypoint` -> `CC_DutyPoint`.
    #[serde(default)]
    pub wire_keys: BTreeMap<String, String>,
}

/// Input for a [`SectionDef`].
#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(tag = "kind", rename_all = "camelCase")]
pub enum SectionSpec {
    StampedFields(StampedFieldsSpec),
    Object(ObjectSectionSpec),
    Switch(SwitchSectionSpec),
}

impl SectionSpec {
    fn gql(&self) -> &str {
        match self {
            SectionSpec::StampedFields(s) => &s.gql,
            SectionSpec::Object(s) => &s.gql,
            SectionSpec::Switch(s) => &s.gql,
        }
    }
}

/// Input for a [`StampedFieldsSection`].
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StampedFieldsSpec {
    pub gql: String,
    /// A container type: its fields are listed here, so it needs no schema.
    pub type_name: String,
    #[serde(default)]
    pub fields: Vec<StampedFieldSpec>,
}

/// Input for an [`ObjectSectionDef`]; without an operation, each component names its own.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectSectionSpec {
    pub gql: String,
    /// The declared type whose schema supplies the fields.
    pub type_name: String,
    #[serde(default)]
    pub operation: Option<OperationRef>,
    #[serde(default)]
    pub fields: Vec<ObjectFieldSpec>,
}

/// Input for a [`SwitchSectionDef`].
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct SwitchSectionSpec {
    pub gql: String,
    pub type_name: String,
    pub operation: OperationRef,
    pub key: String,
    pub flag_field: String,
    pub object_field: String,
    /// The declared type of the switched object.
    pub object_type_name: String,
}

/// Input for a [`MemberDef`].
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct MemberSpec {
    pub gql: String,
    /// A container type; needs no schema.
    pub type_name: String,
    #[serde(default)]
    pub sections: Vec<SectionSpec>,
    #[serde(default)]
    pub mutations: Vec<MutationSpec>,
}

/// Input for a [`ViewDef`].
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct ViewSpec {
    pub gql: String,
    /// A container type; needs no schema.
    pub type_name: String,
    #[serde(default)]
    pub members: Vec<MemberSpec>,
}

impl ViewSpec {
    /// Resolve operations and types into the runtime view.
    pub fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<ViewDef> {
        let members = self
            .members
            .iter()
            .map(|member| {
                member
                    .resolve(resolver)
                    .with_context(|| format!("view '{}' member '{}'", self.gql, member.gql))
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        Ok(ViewDef {
            gql: self.gql.clone(),
            type_name: self.type_name.clone(),
            members,
        })
    }
}

impl MemberSpec {
    fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<MemberDef> {
        let sections = self
            .sections
            .iter()
            .map(|section| {
                section
                    .resolve(resolver)
                    .with_context(|| format!("section '{}'", section.gql()))
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        let object_sections: Vec<(&str, &str)> = self
            .sections
            .iter()
            .filter_map(|section| match section {
                SectionSpec::Object(s) => Some((s.gql.as_str(), s.type_name.as_str())),
                _ => None,
            })
            .collect();
        let mutations = self
            .mutations
            .iter()
            .map(|mutation| mutation.resolve(resolver, &object_sections))
            .collect::<anyhow::Result<Vec<_>>>()?;
        Ok(MemberDef {
            gql: self.gql.clone(),
            type_name: self.type_name.clone(),
            sections,
            mutations,
        })
    }
}

impl SectionSpec {
    fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<SectionDef> {
        Ok(match self {
            SectionSpec::StampedFields(s) => SectionDef::StampedFields(StampedFieldsSection {
                gql: s.gql.clone(),
                type_name: s.type_name.clone(),
                fields: s
                    .fields
                    .iter()
                    .map(|field| {
                        field
                            .resolve(resolver)
                            .with_context(|| format!("field '{}'", field.gql))
                    })
                    .collect::<anyhow::Result<Vec<_>>>()?,
            }),
            SectionSpec::Object(s) => SectionDef::Object(ObjectSection {
                gql: s.gql.clone(),
                section: s.resolve(resolver, s.operation.is_none())?,
            }),
            SectionSpec::Switch(s) => SectionDef::Switch(SwitchSection {
                gql: s.gql.clone(),
                section: SwitchSectionDef {
                    operation: Some(s.operation.clone()),
                    topic: s
                        .operation
                        .resolve(resolver.operations, OperationAction::Send)?,
                    type_name: s.type_name.clone(),
                    key: s.key.clone(),
                    flag_field: s.flag_field.clone(),
                    object_field: s.object_field.clone(),
                    object: plain_object(resolver.types.get(&s.object_type_name)?, resolver)?,
                },
            }),
        })
    }
}

impl StampedFieldSpec {
    fn resolve(&self, resolver: &Resolver<'_>) -> anyhow::Result<StampedFieldDef> {
        let operation = self
            .operation
            .operation(resolver.operations, OperationAction::Send)?;
        let topic = operation
            .topic(&self.operation.parameters)
            .with_context(|| format!("operation '{}'", self.operation.operation))?;
        let component = match &self.type_name {
            Some(name) => resolver.types.get(name)?,
            None => resolver
                .types
                .declared_for_operation(operation, &self.operation.parameters)?,
        };
        let leaves = component.leaves(&BTreeMap::new());
        if leaves.is_empty() {
            anyhow::bail!("type '{}' has no stamped leaves", component.name);
        }
        Ok(StampedFieldDef {
            gql: self.gql.clone(),
            operation: Some(self.operation.clone()),
            topic,
            leaves,
            type_name: component.name.clone(),
            computed: self.computed,
        })
    }
}

impl ObjectSectionSpec {
    /// Every property of the section's type becomes a field, with `fields` overrides applied by key.
    pub fn resolve(
        &self,
        resolver: &Resolver<'_>,
        per_topic: bool,
    ) -> anyhow::Result<ObjectSectionDef> {
        let section_type = resolver.types.get(&self.type_name)?;
        let topic = match &self.operation {
            Some(operation) => operation.resolve(resolver.operations, OperationAction::Send)?,
            None => String::new(),
        };
        for spec in &self.fields {
            section_type
                .property(&spec.key)
                .with_context(|| format!("field '{}'", spec.key))?;
        }
        let mut fields = Vec::new();
        for (key, property) in &section_type.properties {
            let spec = self.fields.iter().find(|f| f.key == *key);
            let field = object_field(key, property, spec, section_type, per_topic, resolver)
                .with_context(|| format!("field '{key}'"))?;
            if let Some(field) = field {
                fields.push(field);
            }
        }
        fields.sort_by(|a, b| a.gql.cmp(&b.gql));
        Ok(ObjectSectionDef {
            operation: self.operation.clone(),
            topic,
            type_name: self.type_name.clone(),
            fields,
        })
    }
}

/// One property as a field; a component without stamped leaves is skipped, as the producer's API does.
fn object_field(
    key: &str,
    property: &Property,
    spec: Option<&ObjectFieldSpec>,
    section_type: &ResolvedType,
    per_topic: bool,
    resolver: &Resolver<'_>,
) -> anyhow::Result<Option<ObjectFieldDef>> {
    let gql = spec
        .and_then(|s| s.gql.clone())
        .unwrap_or_else(|| field_name(key));
    match property {
        Property::Scalar(scalar) => Ok(Some(ObjectFieldDef {
            gql,
            key: key.to_string(),
            r#type: Some(scalar.r#type.clone()),
            type_name: None,
            optional: scalar.optional,
            operation: None,
            topic: None,
            leaves: Vec::new(),
        })),
        Property::Object(object) => {
            let component = match spec.and_then(|s| s.type_name.as_deref()) {
                Some(name) => resolver.types.get(name)?,
                None => resolver
                    .types
                    .for_property(&section_type.document, key, property)?,
            };
            let wire_keys = spec.map(|s| &s.wire_keys).cloned().unwrap_or_default();
            for type_key in wire_keys.keys() {
                component.property(type_key)?;
            }
            let leaves = component.leaves(&wire_keys);
            if leaves.is_empty() {
                return Ok(None);
            }
            let operation = spec.and_then(|s| s.operation.clone());
            let topic = match &operation {
                Some(operation) => Some(operation.resolve(resolver.operations, OperationAction::Send)?),
                None if per_topic => {
                    anyhow::bail!("component '{key}' of a per-topic section names no operation")
                }
                None => None,
            };
            Ok(Some(ObjectFieldDef {
                gql,
                key: key.to_string(),
                r#type: None,
                type_name: Some(component.name.clone()),
                optional: object.optional,
                operation,
                topic,
                leaves,
            }))
        }
        Property::Stamped(_) => anyhow::bail!(
            "property '{key}' of type '{}' is a stamped leaf; a section object holds scalars and components",
            section_type.name
        ),
    }
}

/// A plain (non-stamped) object type, nested objects resolved by their schema.
pub fn plain_object(
    plain_type: &ResolvedType,
    resolver: &Resolver<'_>,
) -> anyhow::Result<PlainObjectDef> {
    let fields = plain_type
        .properties
        .iter()
        .map(|(key, property)| {
            let gql = field_name(key);
            Ok(match property {
                Property::Scalar(scalar) => PlainFieldDef {
                    gql,
                    key: key.clone(),
                    r#type: Some(scalar.r#type.clone()),
                    object: None,
                    optional: scalar.optional,
                },
                Property::Object(object) => PlainFieldDef {
                    gql,
                    key: key.clone(),
                    r#type: None,
                    object: Some(plain_object(
                        resolver
                            .types
                            .for_property(&plain_type.document, key, property)?,
                        resolver,
                    )?),
                    optional: object.optional,
                },
                Property::Stamped(_) => anyhow::bail!(
                    "property '{key}' of plain type '{}' is a stamped leaf",
                    plain_type.name
                ),
            })
        })
        .collect::<anyhow::Result<Vec<_>>>()
        .with_context(|| format!("type '{}'", plain_type.name))?;
    Ok(PlainObjectDef {
        type_name: plain_type.name.clone(),
        fields,
    })
}

#[cfg(test)]
mod tests {
    use super::super::fixtures::*;
    use super::*;
    use serde_json::json;

    fn view() -> ViewDef {
        resolved(extension_json()).unwrap().views.remove(0)
    }

    #[test]
    fn test_sections_get_their_fields_from_the_types() {
        let view = view();
        let member = &view.members[0];
        assert_eq!(
            member.object_section_names(),
            vec!["parameters", "controlValues"]
        );

        let stamped = member.stamped_sections().next().unwrap();
        assert_eq!(stamped.fields[0].topic, "dev/thrusters/thrusters-flow-aft");
        assert_eq!(stamped.fields[0].type_name, "SensorFlowSensorType");
        assert_eq!(stamped.fields[0].leaves[0].gql, "flow");

        let parameters = member.object_section("parameters").unwrap();
        assert_eq!(parameters.topic, "ctl/thrusters/parameters");
        let names: Vec<&str> = parameters.fields.iter().map(|f| f.gql.as_str()).collect();
        assert_eq!(names, vec!["coolingFlow", "maxFlow", "tuning"]);
        assert_eq!(parameters.fields[2].r#type.as_deref(), Some("[Float!]"));

        let control = member.object_section("controlValues").unwrap();
        assert!(control.is_per_topic());
        let pump = &control.fields[0];
        assert_eq!(pump.gql, "pump1");
        assert_eq!(pump.topic.as_deref(), Some("dev/thrusters/thrusters-pump1"));
        assert_eq!(pump.component_type_name(), "ControlPumpType");
        assert_eq!(pump.leaves[0].actuated_key.as_deref(), Some("CC_DutyPoint"));
        assert_eq!(pump.leaves[1].enum_type.as_deref(), Some("Mode"));

        let SectionDef::Switch(switch) = &member.sections[3] else {
            panic!("switch section");
        };
        assert_eq!(switch.section.topic, "ctl/thrusters/control-mode");
        assert_eq!(switch.section.object.type_name, "ThrustersControlModeType");
        assert_eq!(switch.section.object.fields[0].gql, "mode");
        assert_eq!(view.topics().len(), 4);
    }

    #[test]
    fn test_read_must_name_a_send_operation() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][1]["operation"]["operation"] =
            json!("ctl.parameters.set.receive");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("receive"), "{err:#}");
    }

    #[test]
    fn test_per_topic_component_needs_an_operation_and_a_known_key() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][2]["fields"] = json!([]);
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("names no operation"), "{err:#}");

        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][2]["fields"][0]["key"] = json!("pump9");
        let err = resolved(json).unwrap_err();
        assert!(
            format!("{err:#}").contains("no property 'pump9'"),
            "{err:#}"
        );
    }

    #[test]
    fn test_gql_and_type_overrides_apply() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][1]["fields"] =
            json!([{"key": "CoolingFlow", "gql": "flow"}]);
        json["views"][0]["members"][0]["sections"][0]["fields"][0]["typeName"] =
            json!("ControlPumpType");
        let view = resolved(json).unwrap().views.remove(0);
        let parameters = view.members[0].object_section("parameters").unwrap();
        assert!(parameters.fields.iter().any(|f| f.gql == "flow"));
        let stamped = view.members[0].stamped_sections().next().unwrap();
        assert_eq!(stamped.fields[0].type_name, "ControlPumpType");
    }

    #[test]
    fn test_validate_rejects_duplicate_section() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][1]["gql"] = json!("sensorValues");
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("twice"), "{err:#}");
    }
}
