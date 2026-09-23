use anyhow::Context;

use crate::extension::OperationRef;
use crate::model::mutations::{validate_mutation, MutationDef};
use crate::model::views::{LeafDef, ObjectSection, ObjectSectionDef};
use crate::model_validation::ModelSchema;

/// One field of the status object.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StatusFieldDef {
    /// GraphQL field name, e.g. `status` or `time`.
    pub gql: String,
    /// By-alias key in the status payload, e.g. `Status`.
    pub key: String,
    /// GraphQL scalar: `String`, `Float`, `Int`, `Boolean`, or `DateTime` (an
    /// RFC 3339 timestamp, served as the wire carries it).
    pub r#type: String,
}

/// The retained status object; `key` holds the status string directives check.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct StatusDef {
    /// The `send` operation whose messages carry the status object.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`.
    pub topic: String,
    /// By-alias key of the status string (`available`/`running`/...).
    pub key: String,
    pub fields: Vec<StatusFieldDef>,
}

/// A whole object relayed next to the status, typed by a union of the members' objects.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct LifecycleObjectDef {
    /// GraphQL field name on the state object, e.g. `inputs`.
    pub gql: String,
    /// The `send` operation whose messages carry the object.
    pub operation: Option<OperationRef>,
    /// The resolved topic of `operation`.
    pub topic: String,
    /// The union type name, e.g. `SimulationInputsType`.
    pub union_type: String,
    /// Which `object` section of each member forms this union, e.g. `inputs`.
    pub member_section: String,
}

/// One directive (play / pause / step) that transitions the status.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct DirectiveDef {
    /// GraphQL mutation name (`simulationPlay`).
    pub gql: String,
    /// The `receive` operation the directive message is published to.
    pub target: Option<OperationRef>,
    /// The resolved topic of `target`.
    pub topic: String,
    /// GraphQL argument name (`playbackRate` / `seconds`); none for pause.
    pub arg_name: Option<String>,
    /// By-alias payload key of the argument (`PlaybackRate` / `Seconds`).
    pub key: Option<String>,
    /// Whether the argument is non-null.
    pub arg_required: bool,
    /// Default used when a nullable argument is omitted.
    pub default: Option<f64>,
    /// The directive message's [`ModelSchema`], used to validate the argument.
    pub model: Option<ModelSchema>,
    /// Statuses the directive is accepted from.
    pub allowed_from: Vec<String>,
    /// Status the directive waits for after publishing.
    pub expect_status: String,
    /// Error when the current status is not in `allowed_from`.
    pub precondition_error: String,
    /// Error when no status is cached.
    pub missing_error: String,
}

/// One member (thrusters, pcm, ...); its sections are read off the relayed objects, not own topics.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct LifecycleMemberDef {
    /// camelCase name, e.g. `highTemperature`.
    pub name: String,
    pub sections: Vec<ObjectSection>,
    pub mutations: Vec<MutationDef>,
}

impl LifecycleMemberDef {
    /// The section with the given GraphQL name, if any.
    pub fn section(&self, gql: &str) -> Option<&ObjectSectionDef> {
        self.sections
            .iter()
            .find(|s| s.gql == gql)
            .map(|s| &s.section)
    }

    fn section_names(&self) -> Vec<&str> {
        self.sections.iter().map(|s| s.gql.as_str()).collect()
    }
}

/// A retained status object with directives that transition it, plus relayed objects.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct LifecycleDef {
    /// The query field, e.g. `simulation`.
    pub gql: String,
    /// The API's type for the query (`SimulationState`).
    pub state_type_name: String,
    pub status: StatusDef,
    pub objects: Vec<LifecycleObjectDef>,
    pub directives: Vec<DirectiveDef>,
    /// Seconds a directive waits for the expected status.
    pub wait_timeout_s: f64,
    pub members: Vec<LifecycleMemberDef>,
}

impl LifecycleDef {
    /// The topics the cache subscribes to; directive topics are publish-only.
    pub fn read_topics(&self) -> Vec<String> {
        std::iter::once(self.status.topic.clone())
            .chain(self.objects.iter().map(|o| o.topic.clone()))
            .collect()
    }

    /// Every mutation across all members, with its member.
    pub fn mutations(&self) -> impl Iterator<Item = (&LifecycleMemberDef, &MutationDef)> {
        self.members
            .iter()
            .flat_map(|m| m.mutations.iter().map(move |d| (m, d)))
    }

    /// Every stamped leaf of every member object.
    pub fn leaves(&self) -> impl Iterator<Item = &LeafDef> {
        self.members
            .iter()
            .flat_map(|m| m.sections.iter())
            .flat_map(|s| s.section.leaves())
    }

    /// Checks every relayed object names an existing member section and every mutation's return.
    pub fn validate(&self) -> anyhow::Result<()> {
        let context = |what: &str| format!("lifecycle '{}' {what}", self.gql);
        if self.status.fields.is_empty() {
            anyhow::bail!("{}", context("status has no fields"));
        }
        for object in &self.objects {
            for member in &self.members {
                if member.section(&object.member_section).is_none() {
                    anyhow::bail!(
                        "{}",
                        context(&format!(
                            "object '{}' needs member section '{}', which member '{}' lacks",
                            object.gql, object.member_section, member.name
                        ))
                    );
                }
            }
        }
        for (member, def) in self.mutations() {
            validate_mutation(def, &member.section_names())
                .with_context(|| context(&format!("member '{}'", member.name)))?;
        }
        Ok(())
    }

    /// Rewrite every resolved topic in place (runtime prefix strategy).
    pub fn rewrite_topics(&mut self, rewrite: &dyn Fn(&str) -> String) {
        self.status.topic = rewrite(&self.status.topic);
        for object in &mut self.objects {
            object.topic = rewrite(&object.topic);
        }
        for directive in &mut self.directives {
            directive.topic = rewrite(&directive.topic);
        }
        for def in self.members.iter_mut().flat_map(|m| m.mutations.iter_mut()) {
            def.rewrite_topics(rewrite);
        }
    }
}
