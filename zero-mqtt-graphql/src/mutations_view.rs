//! Write-path contract: GraphQL mutations that publish to MQTT. This is the
//! runtime model the resolvers work from, produced from the `x-mqtt-graphql`
//! extension by [`crate::extension`].
//!
//! zero-mqtt-graphql is read-only by default; when `ENABLE_MUTATIONS` is set
//! it serves every declared mutation. Each one names the `receive` operation
//! of the document it publishes to (the target) and, for the kinds that
//! modify a cached object, the `send` operation whose messages carry that
//! object (the state). Three kinds:
//!
//! * `setField`: read the cached state object, overwrite one key with the
//!   (bounds-checked) scalar argument, republish the whole object.
//! * `setComponent`: restamp a composite input into one component of the
//!   cached state object (`{WireKey: {Value, TimeStamp}}`), re-derive any
//!   mirror fields, republish the whole object.
//! * `setFlag`: publish a fresh `{payloadKey: trueValue|falseValue}` object
//!   from a Boolean argument; nothing is read.
//!
//! A mutation belongs to a view member (or a lifecycle member) and returns
//! the `object` section of that member named by `returns` (so read and
//! write share one type), or `Boolean!` when it names none.

use std::collections::BTreeMap;

use serde::Deserialize;

use crate::extension::OperationRef;

/// Single-field numeric bounds a `setField` value must satisfy.
#[derive(Debug, Clone, Deserialize, PartialEq, Default)]
#[serde(rename_all = "camelCase")]
pub struct Bounds {
    pub min: Option<f64>,
    pub max: Option<f64>,
    pub exclusive_min: Option<f64>,
    pub exclusive_max: Option<f64>,
}

/// One field of a `setComponent` mutation's composite input: an unstamped
/// leaf of the component (`dutypoint`, `on`, `setpoint`, `controlMode`, ...).
/// The server restamps it with `now()` and writes `{key: {Value,
/// TimeStamp}}`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct InputFieldDef {
    /// GraphQL input-field name, e.g. `dutypoint`.
    pub gql: String,
    /// By-alias wire key written into the component object, e.g. `Dutypoint`.
    pub key: String,
    /// GraphQL scalar: `Float`, `Int`, `Boolean`, or `String` for an enum leaf.
    pub r#type: String,
    /// For an enum leaf: wire-value -> member-name map. The input accepts the
    /// member name (a GraphQL enum); the wire stores the value. `None` for a
    /// plain scalar.
    pub enum_values: Option<BTreeMap<String, String>>,
    /// For an enum leaf: the enum type name (`PumpControlMode`), used as the
    /// input field's type. Present exactly when `enum_values` is.
    pub enum_type: Option<String>,
    /// Non-null in the API's input type.
    pub required: bool,
}

/// Where one leaf of a derived field comes from: copied from a component of
/// the same object and one of its stamped leaves (by-alias wire keys), or a
/// constant the model leaves at its default.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", untagged)]
pub enum DerivedLeaf {
    Source { component: String, leaf: String },
    Constant { constant: serde_json::Value },
}

/// A field of the whole object that is a plain mirror of other components'
/// stamped leaves (see [`MutationDef::derived`]).
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct DerivedFieldDef {
    /// By-alias key of the derived field in the whole object.
    pub key: String,
    /// By-alias leaf key -> where its value comes from.
    pub leaves: BTreeMap<String, DerivedLeaf>,
}

/// The comparison of an [`InvariantDef`].
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub enum Comparison {
    Lt,
    Le,
    Gt,
    Ge,
}

impl Comparison {
    pub fn holds(self, lhs: f64, rhs: f64) -> bool {
        match self {
            Comparison::Lt => lhs < rhs,
            Comparison::Le => lhs <= rhs,
            Comparison::Gt => lhs > rhs,
            Comparison::Ge => lhs >= rhs,
        }
    }
}

/// A cross-field invariant of the whole object a `setField` mutation
/// modifies (the schema's `x-invariants`): `object[lhs] <op> object[rhs]`
/// must hold, else the modified object is rejected with `error`.
#[derive(Debug, Clone, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct InvariantDef {
    pub lhs: String,
    pub op: Comparison,
    pub rhs: String,
    pub error: String,
}

impl InvariantDef {
    /// The invariant's error when it is violated by `object`; a key that is
    /// missing or not a number does not violate it.
    pub fn violation(&self, object: &serde_json::Map<String, serde_json::Value>) -> Option<&str> {
        let number = |key: &str| object.get(key).and_then(serde_json::Value::as_f64);
        match (number(&self.lhs), number(&self.rhs)) {
            (Some(lhs), Some(rhs)) if !self.op.holds(lhs, rhs) => Some(&self.error),
            _ => None,
        }
    }
}

/// How a mutation is confirmed before it returns: the published change must
/// show up on the confirm topic (the `send` operation `operation`, default
/// the mutation's state) under `key` (default the mutation's key) within
/// `timeout_s`, else the mutation fails with `timeout_error`. With
/// `presence` the Boolean argument is compared with whether `key` holds a
/// value (a switch whose object is null when off) instead of the written
/// value.
#[derive(Debug, Clone, PartialEq)]
pub struct ConfirmDef {
    pub operation: Option<OperationRef>,
    pub topic: String,
    pub key: Option<String>,
    pub presence: bool,
    pub timeout_s: f64,
    pub timeout_error: String,
}

/// The mutation families (see the module docs).
#[derive(Debug, Clone, Copy, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub enum MutationKind {
    SetField,
    SetComponent,
    SetFlag,
}

/// One mutation.
#[derive(Debug, Clone, PartialEq)]
pub struct MutationDef {
    /// GraphQL mutation field name, e.g. `thrustersParameterSetCoolingFlow`.
    pub gql: String,
    pub kind: MutationKind,
    /// `setField`: GraphQL type of the argument: `Float`, `Int`, `Boolean`, or
    /// a list like `[Float!]` (a non-null list argument). Empty otherwise.
    pub arg_type: String,
    /// Name of the GraphQL argument.
    pub arg_name: String,
    /// By-alias key in the object to overwrite (`setField`/`setComponent`), or
    /// the key of the fresh object (`setFlag`).
    pub key: String,
    /// `setField`/`setComponent`: the `send` operation whose messages carry
    /// the object to modify.
    pub state: Option<OperationRef>,
    /// The `receive` operation the object is published to.
    pub target: Option<OperationRef>,
    /// The resolved topic of `state` (empty for `setFlag`).
    pub state_topic: String,
    /// The resolved topic of `target`.
    pub set_topic: String,
    /// The `object` section of the member the mutation returns. None returns
    /// `Boolean!`.
    pub returns: Option<String>,
    /// `setField`: per-field numeric bounds; `None` when unconstrained.
    pub bounds: Option<Bounds>,
    /// `setFlag`: the `key` value when the Boolean argument is true.
    pub true_value: Option<String>,
    /// `setFlag`: the `key` value when the Boolean argument is false.
    pub false_value: Option<String>,
    /// `setComponent`: the composite input leaves to restamp into the
    /// component.
    pub input_fields: Vec<InputFieldDef>,
    /// `setComponent`: fields of the whole object the producer's model derives
    /// from other components (mirrors of a component's stamped leaves). The
    /// republish mirrors them the same way so the payload is identical to what
    /// the producer's own API would publish.
    pub derived: Vec<DerivedFieldDef>,
    /// `setComponent`: the composite input type name (`PumpInputType`, shared
    /// across groups). `None` for the other kinds.
    pub input_type_name: Option<String>,
    /// The error when nothing is cached at the state topic to modify.
    pub missing_error: Option<String>,
    /// How the change is confirmed before the mutation returns; `None`
    /// returns right after the publish.
    pub confirm: Option<ConfirmDef>,
    /// `setField`: cross-field invariants of the modified object.
    pub invariants: Vec<InvariantDef>,
}

impl MutationDef {
    /// Whether this kind takes a composite component input.
    pub fn has_composite_input(&self) -> bool {
        self.kind == MutationKind::SetComponent
    }

    /// Whether this kind reads a cached state object.
    pub fn reads_state(&self) -> bool {
        self.kind != MutationKind::SetFlag
    }

    /// The composite input type name of a `setComponent` mutation. Panics for
    /// other kinds, which the resolvers never ask.
    pub fn input_type_name(&self) -> &str {
        self.input_type_name
            .as_deref()
            .expect("composite mutation carries its input type name (spec validated on load)")
    }

    /// The topic a confirmation is awaited on, if any.
    pub fn confirm_topic(&self) -> Option<&str> {
        self.confirm.as_ref().map(|c| c.topic.as_str())
    }

    /// Rewrite the resolved topics in place (runtime prefix strategy).
    pub fn rewrite_topics(&mut self, rewrite: &dyn Fn(&str) -> String) {
        if !self.state_topic.is_empty() {
            self.state_topic = rewrite(&self.state_topic);
        }
        self.set_topic = rewrite(&self.set_topic);
        if let Some(confirm) = &mut self.confirm {
            confirm.topic = rewrite(&confirm.topic);
        }
    }
}

/// `returns` must name one of the member's `object` sections.
pub fn validate_mutation(def: &MutationDef, sections: &[&str]) -> anyhow::Result<()> {
    if let Some(returns) = &def.returns {
        if !sections.contains(&returns.as_str()) {
            anyhow::bail!("mutation '{}' returns unknown section '{returns}'", def.gql);
        }
    }
    Ok(())
}
