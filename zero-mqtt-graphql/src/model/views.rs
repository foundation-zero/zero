use std::collections::BTreeMap;

use anyhow::Context;

use crate::extension::OperationRef;
use crate::model::mutations::{validate_mutation, MutationDef};

/// One `{value, timestamp}` leaf of a stamped component.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LeafDef {
    /// GraphQL subfield name, e.g. `positionRel`.
    pub gql: String,
    /// Wire key in the cached MQTT payload, e.g. `PositionRel`.
    pub key: String,
    /// Inner scalar of `Stamped<T>`; enum leaves carry `String`.
    pub r#type: String,
    /// Enum leaf: wire value -> member name (e.g. `"0" -> "LOCAL"`), applied to cached values.
    pub enum_values: Option<BTreeMap<String, String>>,
    /// Enum leaf: GraphQL enum type name. Present exactly when `enum_values` is.
    pub enum_type: Option<String>,
    /// Whether the leaf's value is nullable in the API schema.
    pub optional: bool,
    /// Device payload key when it differs from the alias (`CC_DutyPoint` for `Dutypoint`);
    /// re-keyed on read so reads and mutation returns share one component type.
    pub actuated_key: Option<String>,
    /// Wire-shaped default served when the payload lacks this leaf; `None` if required.
    pub default: Option<serde_json::Value>,
}

/// One field of a `stampedFields` section, resolved from a single topic.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct StampedFieldDef {
    /// GraphQL field name under the section, e.g. `thrustersFlowAft`.
    pub gql: String,
    /// The `send` operation whose messages back this field.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`.
    pub topic: String,
    pub leaves: Vec<LeafDef>,
    /// API type name of the component, e.g. `SensorFlowSensorType`.
    pub type_name: String,
    /// Producer-computed field; diagnostic only.
    pub computed: bool,
}

/// One field of an `object` section: a flat scalar (`type`) or a stamped-leaf component (`leaves`).
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ObjectFieldDef {
    /// GraphQL field name under the section, e.g. `coolingFlow`.
    pub gql: String,
    /// Key in the cached object payload, e.g. `CoolingFlow`.
    pub key: String,
    /// GraphQL scalar of a flat field, e.g. `Float` or `[Float!]`; `None` for a component.
    pub r#type: Option<String>,
    /// API type name of a component field, e.g. `ControlPumpType`.
    pub type_name: Option<String>,
    /// A flat field that is nullable in the API schema.
    pub optional: bool,
    /// Per-topic section only: the `send` operation backing this component.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`.
    pub topic: Option<String>,
    /// Stamped leaves of a component field; empty for a flat field.
    pub leaves: Vec<LeafDef>,
}

impl ObjectFieldDef {
    /// The component type name; panics on a flat field.
    pub fn component_type_name(&self) -> &str {
        self.type_name
            .as_deref()
            .expect("component field carries its type name (spec validated on load)")
    }
}

/// A section read from one whole-object topic, or (without an operation) one topic per component.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ObjectSectionDef {
    /// The `send` operation whose messages carry the whole section object.
    /// `None` for a per-topic section.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`; empty for a per-topic section.
    pub topic: String,
    /// The API's type name for the section (`ThrustersParametersType`).
    pub type_name: String,
    pub fields: Vec<ObjectFieldDef>,
}

impl ObjectSectionDef {
    /// Whether the section is assembled from one topic per component field.
    pub fn is_per_topic(&self) -> bool {
        self.topic.is_empty() && self.fields.iter().any(|f| f.topic.is_some())
    }

    /// Every stamped leaf of every component field.
    pub fn leaves(&self) -> impl Iterator<Item = &LeafDef> {
        self.fields.iter().flat_map(|f| f.leaves.iter())
    }

    /// The topics the section reads: its own, or its component fields'.
    pub fn topics(&self) -> impl Iterator<Item = &str> {
        std::iter::once(self.topic.as_str())
            .filter(|t| !t.is_empty())
            .chain(self.fields.iter().filter_map(|f| f.topic.as_deref()))
    }
}

/// One field of a plain (non-stamped) object: a scalar `type` or a nested `object`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlainFieldDef {
    pub gql: String,
    /// By-alias key in the payload object, e.g. `BoostingMode`.
    pub key: String,
    pub r#type: Option<String>,
    pub object: Option<PlainObjectDef>,
    /// Nullable in the API schema (optional field or default).
    pub optional: bool,
}

/// A plain object type; without fields it renders an `Empty: Void` placeholder.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PlainObjectDef {
    pub type_name: String,
    pub fields: Vec<PlainFieldDef>,
}

/// A section whose `key` holds an object or null, exposed as a Boolean flag plus the object.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SwitchSectionDef {
    /// The `send` operation whose messages carry the switch object.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`.
    pub topic: String,
    /// The API's type name for the section.
    pub type_name: String,
    /// The by-alias key of the switched object inside the payload.
    pub key: String,
    /// GraphQL name of the derived Boolean field.
    pub flag_field: String,
    /// GraphQL name of the object field.
    pub object_field: String,
    pub object: PlainObjectDef,
}

/// One named section of a view member (`<view> { <member> { <section> } }`).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SectionDef {
    StampedFields(StampedFieldsSection),
    Object(ObjectSection),
    Switch(SwitchSection),
}

/// A section of one topic per stamped field.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct StampedFieldsSection {
    /// GraphQL field name of the section under the member, e.g. `sensorValues`.
    pub gql: String,
    /// The API's type name for the section object.
    pub type_name: String,
    pub fields: Vec<StampedFieldDef>,
}

/// A whole-object (or per-topic) section under its GraphQL field name.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ObjectSection {
    pub gql: String,
    pub section: ObjectSectionDef,
}

/// A switch section under its GraphQL field name.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct SwitchSection {
    pub gql: String,
    pub section: SwitchSectionDef,
}

impl SectionDef {
    /// The GraphQL field name of the section under its member.
    pub fn gql(&self) -> &str {
        match self {
            SectionDef::StampedFields(s) => &s.gql,
            SectionDef::Object(s) => &s.gql,
            SectionDef::Switch(s) => &s.gql,
        }
    }

    /// Every stamped leaf the section declares.
    pub fn leaves(&self) -> Box<dyn Iterator<Item = &LeafDef> + '_> {
        match self {
            SectionDef::StampedFields(s) => Box::new(s.fields.iter().flat_map(|f| f.leaves.iter())),
            SectionDef::Object(s) => Box::new(s.section.leaves()),
            SectionDef::Switch(_) => Box::new(std::iter::empty()),
        }
    }

    /// The topics the section reads.
    pub fn topics(&self) -> Vec<String> {
        match self {
            SectionDef::StampedFields(s) => s.fields.iter().map(|f| f.topic.clone()).collect(),
            SectionDef::Object(s) => s.section.topics().map(str::to_string).collect(),
            SectionDef::Switch(s) => vec![s.section.topic.clone()],
        }
    }

    /// Rewrite every resolved topic in place (runtime prefix strategy).
    pub fn rewrite_topics(&mut self, rewrite: &dyn Fn(&str) -> String) {
        match self {
            SectionDef::StampedFields(s) => {
                for f in &mut s.fields {
                    f.topic = rewrite(&f.topic);
                }
            }
            SectionDef::Object(s) => {
                if !s.section.topic.is_empty() {
                    s.section.topic = rewrite(&s.section.topic);
                }
                for f in &mut s.section.fields {
                    if let Some(t) = &f.topic {
                        f.topic = Some(rewrite(t));
                    }
                }
            }
            SectionDef::Switch(s) => s.section.topic = rewrite(&s.section.topic),
        }
    }
}

/// One member of a view.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct MemberDef {
    /// GraphQL field name under the view object, e.g. `thrusters`.
    pub gql: String,
    /// The API's type name for this member's object.
    pub type_name: String,
    pub sections: Vec<SectionDef>,
    /// Mutations on this member; each returns one of its `object` sections or Boolean.
    pub mutations: Vec<MutationDef>,
}

impl MemberDef {
    /// The `object` section with the given GraphQL name, if any.
    pub fn object_section(&self, gql: &str) -> Option<&ObjectSectionDef> {
        self.sections.iter().find_map(|s| match s {
            SectionDef::Object(o) if o.gql == gql => Some(&o.section),
            _ => None,
        })
    }

    /// The GraphQL names of the `object` sections.
    pub fn object_section_names(&self) -> Vec<&str> {
        self.sections
            .iter()
            .filter_map(|s| match s {
                SectionDef::Object(o) => Some(o.gql.as_str()),
                _ => None,
            })
            .collect()
    }

    /// The sections of one topic per stamped field.
    pub fn stamped_sections(&self) -> impl Iterator<Item = &StampedFieldsSection> {
        self.sections.iter().filter_map(|s| match s {
            SectionDef::StampedFields(s) => Some(s),
            _ => None,
        })
    }

    /// Every stamped leaf of every section.
    pub fn leaves(&self) -> impl Iterator<Item = &LeafDef> {
        self.sections.iter().flat_map(|s| s.leaves())
    }
}

/// A composite read view: a query field with one field per member.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct ViewDef {
    /// The query field, e.g. `modules`.
    pub gql: String,
    /// The API's type name for the view object, e.g. `ControlModules`.
    pub type_name: String,
    pub members: Vec<MemberDef>,
}

impl ViewDef {
    /// Every stamped leaf of every member.
    pub fn leaves(&self) -> impl Iterator<Item = &LeafDef> {
        self.members.iter().flat_map(|m| m.leaves())
    }

    /// The distinct topics the view reads, in order of first use.
    pub fn topics(&self) -> Vec<String> {
        let mut topics: Vec<String> = Vec::new();
        for topic in self
            .members
            .iter()
            .flat_map(|m| m.sections.iter())
            .flat_map(|s| s.topics())
        {
            if !topic.is_empty() && !topics.contains(&topic) {
                topics.push(topic);
            }
        }
        topics
    }

    /// Rewrite every resolved topic in place (runtime prefix strategy).
    pub fn rewrite_topics(&mut self, rewrite: &dyn Fn(&str) -> String) {
        for member in &mut self.members {
            for section in &mut member.sections {
                section.rewrite_topics(rewrite);
            }
            for def in &mut member.mutations {
                def.rewrite_topics(rewrite);
            }
        }
    }

    /// Every mutation of every member, with its member.
    pub fn mutations(&self) -> impl Iterator<Item = (&MemberDef, &MutationDef)> {
        self.members
            .iter()
            .flat_map(|m| m.mutations.iter().map(move |d| (m, d)))
    }

    /// Checks distinct member/section names and that every mutation returns an existing section.
    pub fn validate(&self) -> anyhow::Result<()> {
        let mut members: Vec<&str> = Vec::new();
        for member in &self.members {
            if members.contains(&member.gql.as_str()) {
                anyhow::bail!("view '{}' declares member '{}' twice", self.gql, member.gql);
            }
            members.push(&member.gql);
            let mut names: Vec<&str> = Vec::new();
            for section in &member.sections {
                if names.contains(&section.gql()) {
                    anyhow::bail!(
                        "view '{}' member '{}' declares section '{}' twice",
                        self.gql,
                        member.gql,
                        section.gql()
                    );
                }
                names.push(section.gql());
            }
            for def in &member.mutations {
                validate_mutation(def, &member.object_section_names())
                    .with_context(|| format!("view '{}' member '{}'", self.gql, member.gql))?;
            }
        }
        Ok(())
    }
}
