//! The `views` of the extension: what a document declares for a composite
//! read view, and how it resolves to the runtime [`ViewDef`].
//!
//! A section names its GraphQL type; that type's declared schema (see
//! [`super::TypeIndex`]) supplies the fields. The document only adds what the
//! schema cannot say: which operation feeds a field, and — where the rule
//! does not hold — a field's GraphQL name, its type, or the wire keys a
//! device payload uses instead of the type's own.

use std::collections::BTreeMap;

use anyhow::Context;
use roas_asyncapi::v3_0::operation::OperationAction;
use serde::Deserialize;

use super::{MutationSpec, OperationRef, ResolvedType, Resolver};
use crate::naming::field_name;
use crate::schema::Property;
use crate::views::{
    MemberDef, ObjectFieldDef, ObjectSection, ObjectSectionDef, PlainFieldDef, PlainObjectDef,
    SectionDef, StampedFieldDef, StampedFieldsSection, SwitchSection, SwitchSectionDef, ViewDef,
};

/// One field of a `stampedFields` section: fed by one `send` operation.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StampedFieldSpec {
    /// GraphQL field name under the section, e.g. `thrustersFlowAft`.
    pub gql: String,
    /// The `send` operation whose messages back this field.
    pub operation: OperationRef,
    /// The component's GraphQL type. Default: the type served from the
    /// operation's payload schema.
    #[serde(default)]
    pub type_name: Option<String>,
    /// Whether the producer derives this field from others (a computed value
    /// it publishes like any other). Diagnostic only.
    #[serde(default)]
    pub computed: bool,
}

/// What a document adds to one property of an `object` section's type.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectFieldSpec {
    /// The property's wire key in the section object.
    pub key: String,
    /// GraphQL field name. Default: [`field_name`] of the key.
    #[serde(default)]
    pub gql: Option<String>,
    /// For a component: its GraphQL type. Default: the type served from the
    /// property's schema.
    #[serde(default)]
    pub type_name: Option<String>,
    /// For a component of a per-topic section: the `send` operation whose
    /// messages carry this component alone.
    #[serde(default)]
    pub operation: Option<OperationRef>,
    /// For a component read off a device payload that keys a leaf differently
    /// than the type's schema: type key -> device key (`Dutypoint` ->
    /// `CC_DutyPoint`).
    #[serde(default)]
    pub wire_keys: BTreeMap<String, String>,
}

/// One named section of a view member.
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

/// A section of one topic per stamped field.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct StampedFieldsSpec {
    /// GraphQL field name of the section under the member, e.g. `sensorValues`.
    pub gql: String,
    /// GraphQL type name of the section object (a container: its fields are
    /// the ones listed here, so it needs no schema).
    pub type_name: String,
    #[serde(default)]
    pub fields: Vec<StampedFieldSpec>,
}

/// A whole-object section (one `send` operation carrying the whole object)
/// or, without an operation, a per-topic section whose component fields
/// each name their own.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct ObjectSectionSpec {
    pub gql: String,
    /// The declared type the section object is served as.
    pub type_name: String,
    #[serde(default)]
    pub operation: Option<OperationRef>,
    #[serde(default)]
    pub fields: Vec<ObjectFieldSpec>,
}

/// A `switch` section: one object on a topic whose `key` holds a plain
/// object or null, exposed as a flag plus the object.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct SwitchSectionSpec {
    pub gql: String,
    /// GraphQL type name of the section object.
    pub type_name: String,
    pub operation: OperationRef,
    /// The wire key of the switched object inside the payload.
    pub key: String,
    /// GraphQL name of the derived Boolean field.
    pub flag_field: String,
    /// GraphQL name of the object field.
    pub object_field: String,
    /// The declared type of the switched object.
    pub object_type_name: String,
}

/// One member of a view.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct MemberSpec {
    /// GraphQL field name under the view object, e.g. `thrusters`.
    pub gql: String,
    /// GraphQL type name of the member object (a container).
    pub type_name: String,
    #[serde(default)]
    pub sections: Vec<SectionSpec>,
    #[serde(default)]
    pub mutations: Vec<MutationSpec>,
}

/// A composite read view: a query field whose object has one field per
/// member.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct ViewSpec {
    /// The query field, e.g. `modules`.
    pub gql: String,
    /// GraphQL type name of the view object (a container).
    pub type_name: String,
    #[serde(default)]
    pub members: Vec<MemberSpec>,
}

impl ViewSpec {
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
    /// Resolve the section: every property of the section's type becomes a
    /// field (a scalar, or a component with the leaves of its own type), with
    /// the document's per-field additions applied by key. A `per_topic`
    /// section has no operation of its own: every component names one.
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

/// One property of a section type as a field. A scalar property is a flat
/// field; an object property is a component whose leaves come from its own
/// declared type (found by its schema, or named by `spec`). A component
/// without stamped leaves (an empty controller state) is no field, like the
/// producer's API. In a per-topic section every component names the
/// operation that carries it.
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

/// A plain (non-stamped) object type as the runtime describes it: scalar
/// fields and nested objects, each nested one found by its schema.
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
