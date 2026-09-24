mod lifecycles;
mod mutations;
mod views;

use std::borrow::Cow;
use std::collections::BTreeMap;

use anyhow::Context;
use roas_asyncapi::v3_0::operation::OperationAction;
use serde::Deserialize;
use serde_json::Value;

use crate::asyncapi::{OperationDef, OperationIndex, TopicGroupDef};
use crate::metadata::{MetadataFile, TopicMetadataEntry};
use crate::model::lifecycle::LifecycleDef;
use crate::model::mutations::{DerivedFieldDef, InvariantDef};
use crate::model::views::{LeafDef, ViewDef};
use crate::model_validation::ModelSchema;
use crate::naming::field_name;
use crate::schema::{schema_ref, Components, Property};

pub use lifecycles::LifecycleSpec;
pub use mutations::MutationSpec;
pub use views::ViewSpec;

/// Root key of the extension in an AsyncAPI document.
pub const EXTENSION_KEY: &str = "x-mqtt-graphql";

/// The extension version this bridge reads.
pub const EXTENSION_VERSION: u64 = 2;

/// A binding to one operation plus a value for every `{parameter}` in its address.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct OperationRef {
    pub operation: String,
    #[serde(default)]
    pub parameters: BTreeMap<String, String>,
}

impl OperationRef {
    /// The concrete topic, provided the operation exists and has the expected direction.
    pub fn resolve(
        &self,
        operations: &OperationIndex,
        action: OperationAction,
    ) -> anyhow::Result<String> {
        let operation = self.operation(operations, action)?;
        operation
            .topic(&self.parameters)
            .with_context(|| format!("operation '{}'", self.operation))
    }

    /// The operation, provided it has the expected direction.
    pub fn operation<'a>(
        &self,
        operations: &'a OperationIndex,
        action: OperationAction,
    ) -> anyhow::Result<&'a OperationDef> {
        let operation = operations
            .get(&self.operation)
            .with_context(|| format!("unknown operation '{}'", self.operation))?;
        if operation.action != action {
            anyhow::bail!(
                "operation '{}' is a {} operation, expected {}",
                self.operation,
                action_name(operation.action),
                action_name(action)
            );
        }
        Ok(operation)
    }
}

fn action_name(action: OperationAction) -> &'static str {
    match action {
        OperationAction::Send => "send",
        OperationAction::Receive => "receive",
    }
}

/// One GraphQL object type as the document declares it.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct TypeSpec {
    /// The payload schema (`$ref` or inline) whose properties are the type's fields.
    pub schema: Value,
}

/// A declared type with its schema read, including its `x-invariants` / `x-derived`.
#[derive(Debug, Clone, PartialEq)]
pub struct ResolvedType {
    pub name: String,
    /// The document the schema belongs to.
    pub document: String,
    pub reference: Option<String>,
    /// Classified properties in document order.
    pub properties: Vec<(String, Property)>,
    pub invariants: Vec<InvariantDef>,
    pub derived: Vec<DerivedFieldDef>,
    /// Validates writes as the producer does.
    pub model: ModelSchema,
}

impl ResolvedType {
    /// One `{value, timestamp}` leaf per stamped property; other properties are ignored.
    pub fn leaves(&self, wire_keys: &BTreeMap<String, String>) -> Vec<LeafDef> {
        self.properties
            .iter()
            .filter_map(|(key, property)| match property {
                Property::Stamped(leaf) => Some(LeafDef {
                    gql: field_name(key),
                    key: key.clone(),
                    r#type: leaf.r#type.clone(),
                    enum_values: leaf.r#enum.as_ref().map(|e| e.values.clone()),
                    enum_type: leaf.r#enum.as_ref().map(|e| e.name.clone()),
                    optional: leaf.optional,
                    actuated_key: wire_keys.get(key).cloned(),
                    default: leaf.default.clone(),
                }),
                _ => None,
            })
            .collect()
    }

    /// The property with the given wire key.
    pub fn property(&self, key: &str) -> anyhow::Result<&Property> {
        self.properties
            .iter()
            .find(|(k, _)| k == key)
            .map(|(_, p)| p)
            .with_context(|| format!("type '{}' has no property '{key}'", self.name))
    }
}

/// Declared types by name and by schema `$ref`, plus each document's `components`
/// for payloads that are no declared type.
#[derive(Debug, Clone, Default, PartialEq)]
pub struct TypeIndex {
    types: BTreeMap<String, ResolvedType>,
    by_reference: BTreeMap<(String, String), String>,
    components: BTreeMap<String, Value>,
}

/// Read one schema as a type.
fn read_type(
    name: &str,
    schema: &Value,
    components: Components<'_>,
    document: &str,
) -> anyhow::Result<ResolvedType> {
    let properties = components
        .properties(schema)?
        .into_iter()
        .map(|(key, schema)| {
            let property = components
                .property(schema)
                .with_context(|| format!("property '{key}'"))?;
            Ok((key, property))
        })
        .collect::<anyhow::Result<Vec<_>>>()?;
    Ok(ResolvedType {
        name: name.to_string(),
        document: document.to_string(),
        reference: schema_ref(schema).map(str::to_string),
        properties,
        invariants: components.invariants(schema)?,
        derived: components.derived(schema)?,
        model: ModelSchema::read(schema, components)?,
    })
}

impl TypeIndex {
    /// Read every declared type's schema against the document's components.
    fn resolve(
        declared: &BTreeMap<String, TypeSpec>,
        components: Option<&Value>,
        document: &str,
    ) -> anyhow::Result<Self> {
        let mut index = TypeIndex::default();
        let resolver = Components::new(components);
        for (name, spec) in declared {
            let resolved = read_type(name, &spec.schema, resolver, document)
                .with_context(|| format!("type '{name}'"))?;
            if let Some(reference) = &resolved.reference {
                let key = (document.to_string(), reference.clone());
                if let Some(other) = index.by_reference.insert(key, name.clone()) {
                    anyhow::bail!(
                        "types '{other}' and '{name}' are both served from '{reference}'"
                    );
                }
            }
            index.types.insert(name.clone(), resolved);
        }
        if let Some(components) = components {
            index
                .components
                .insert(document.to_string(), components.clone());
        }
        Ok(index)
    }

    fn merge(&mut self, other: TypeIndex) -> anyhow::Result<()> {
        for (name, resolved) in other.types {
            if let Some(existing) = self.types.get(&name) {
                if *existing != resolved {
                    anyhow::bail!("type '{name}' is declared differently by two documents");
                }
                continue;
            }
            self.types.insert(name, resolved);
        }
        self.by_reference.extend(other.by_reference);
        self.components.extend(other.components);
        Ok(())
    }

    /// The declared type with this name.
    pub fn get(&self, name: &str) -> anyhow::Result<&ResolvedType> {
        self.types.get(name).with_context(|| {
            format!("unknown type '{name}' (not declared in {EXTENSION_KEY}.types)")
        })
    }

    /// The type served from a schema of `document`, by its `$ref`.
    pub fn for_reference(&self, document: &str, reference: &str) -> Option<&ResolvedType> {
        self.by_reference
            .get(&(document.to_string(), reference.to_string()))
            .and_then(|name| self.types.get(name))
    }

    /// The declared type whose schema an operation's payload `$ref`s.
    pub fn declared_for_operation(
        &self,
        operation: &OperationDef,
        parameters: &BTreeMap<String, String>,
    ) -> anyhow::Result<&ResolvedType> {
        let schema = operation.schema(parameters).with_context(|| {
            format!("operation on '{}' has no payload schema", operation.address)
        })?;
        let reference = schema_ref(schema).with_context(|| {
            format!(
                "the payload of operation on '{}' is not a reference to a declared type's schema",
                operation.address
            )
        })?;
        self.for_reference(&operation.document, reference)
            .with_context(|| format!("no declared type is served from '{reference}'"))
    }

    /// An operation payload's declared type, else its schema read on its own.
    pub fn for_operation(
        &self,
        operation: &OperationDef,
        parameters: &BTreeMap<String, String>,
    ) -> anyhow::Result<Cow<'_, ResolvedType>> {
        if let Ok(declared) = self.declared_for_operation(operation, parameters) {
            return Ok(Cow::Borrowed(declared));
        }
        let schema = operation.schema(parameters).with_context(|| {
            format!("operation on '{}' has no payload schema", operation.address)
        })?;
        let components = Components::new(self.components.get(&operation.document));
        read_type("", schema, components, &operation.document)
            .map(Cow::Owned)
            .with_context(|| format!("payload of operation on '{}'", operation.address))
    }

    /// A nested property's own schema shape: a component served as its base's type
    /// still carries its own fields on the wire, which a write must supply.
    pub fn shape_of_property(
        &self,
        document: &str,
        key: &str,
        property: &Property,
    ) -> anyhow::Result<Cow<'_, ResolvedType>> {
        let Property::Object(object) = property else {
            anyhow::bail!("property '{key}' is not an object");
        };
        let reference = object.reference.as_deref().with_context(|| {
            format!("object property '{key}' has an inline schema; declare its type")
        })?;
        if let Some(declared) = self.for_reference(document, reference) {
            return Ok(Cow::Borrowed(declared));
        }
        let components = Components::new(self.components.get(document));
        read_type(
            "",
            &serde_json::json!({"$ref": reference}),
            components,
            document,
        )
        .map(Cow::Owned)
        .with_context(|| format!("property '{key}'"))
    }

    /// The type a nested-object property is served from.
    pub fn for_property(
        &self,
        document: &str,
        key: &str,
        property: &Property,
    ) -> anyhow::Result<&ResolvedType> {
        let Property::Object(object) = property else {
            anyhow::bail!("property '{key}' is not an object");
        };
        let reference = object.reference.as_deref().with_context(|| {
            format!("object property '{key}' has an inline schema; declare its type")
        })?;
        self.for_reference(document, reference).with_context(|| {
            format!("property '{key}': no declared type is served from '{reference}'")
        })
    }
}

/// What every resolve step needs.
pub struct Resolver<'a> {
    pub operations: &'a OperationIndex,
    pub types: &'a TypeIndex,
    pub validation_error_url: &'a str,
}

/// Static attributes per instance of a one-parameter `send` channel; resolves to a [`MetadataFile`].
#[derive(Debug, Clone, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InstancesDef {
    pub operation: String,
    #[serde(default)]
    pub instances: BTreeMap<String, BTreeMap<String, Value>>,
}

impl InstancesDef {
    fn resolve(
        &self,
        operations: &OperationIndex,
        groups: &[TopicGroupDef],
    ) -> anyhow::Result<MetadataFile> {
        let operation = operations
            .get(&self.operation)
            .with_context(|| format!("unknown operation '{}'", self.operation))?;
        if operation.action != OperationAction::Send {
            anyhow::bail!("operation '{}' is not a send operation", self.operation);
        }
        let segments: Vec<&str> = operation.address.split('/').collect();
        let params: Vec<&str> = segments
            .iter()
            .filter_map(|s| s.strip_prefix('{').and_then(|s| s.strip_suffix('}')))
            .collect();
        let [param] = params[..] else {
            anyhow::bail!(
                "operation '{}' has {} parameters; instances need exactly one",
                self.operation,
                params.len()
            );
        };
        // Must match the loader's `group_identity`.
        let group = segments
            .iter()
            .filter(|s| !s.starts_with('{'))
            .copied()
            .collect::<Vec<_>>()
            .join("/");
        if !groups.iter().any(|g| g.group == group) {
            anyhow::bail!(
                "operation '{}' is not a subscribed topic group of the document",
                self.operation
            );
        }
        let topics = self
            .instances
            .iter()
            .map(|(value, metadata)| {
                let parameters = BTreeMap::from([(param.to_string(), value.clone())]);
                Ok(TopicMetadataEntry {
                    topic: operation.topic(&parameters)?,
                    metadata: metadata.clone(),
                })
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        Ok(MetadataFile {
            group,
            group_by: None,
            topics,
        })
    }
}

/// The extension as one document declares it.
#[derive(Debug, Clone, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ExtensionDocument {
    #[serde(default)]
    version: u64,
    #[serde(default)]
    validation_error_url: String,
    #[serde(default)]
    types: BTreeMap<String, TypeSpec>,
    #[serde(default)]
    views: Vec<ViewSpec>,
    #[serde(default)]
    metadata: Vec<InstancesDef>,
    #[serde(default)]
    lifecycles: Vec<LifecycleSpec>,
}

/// The `x-mqtt-graphql` extension of every document, unresolved until [`GraphqlExtension::resolve`].
/// Reads bind to `send` and writes to `receive` operations; names and types all come from the schemas.
#[derive(Debug, Clone, Default)]
pub struct GraphqlExtension {
    pub version: u64,
    /// Documentation link base the producer's validation errors carry.
    pub validation_error_url: String,
    pub types: TypeIndex,
    declared_views: Vec<ViewSpec>,
    declared_lifecycles: Vec<LifecycleSpec>,
    pub metadata: Vec<InstancesDef>,
    /// Filled by `resolve`.
    pub views: Vec<ViewDef>,
    /// Filled by `resolve`.
    pub lifecycles: Vec<LifecycleDef>,
    /// Filled by `resolve`.
    pub metadata_files: Vec<MetadataFile>,
}

impl GraphqlExtension {
    /// Resolve bindings to topics and types to fields, and validate. Each metadata entry
    /// must enumerate one of `groups`.
    pub fn resolve(
        &mut self,
        operations: &OperationIndex,
        groups: &[TopicGroupDef],
    ) -> anyhow::Result<()> {
        if self.version != EXTENSION_VERSION {
            anyhow::bail!(
                "{EXTENSION_KEY} version {} is not supported (this bridge reads version {EXTENSION_VERSION})",
                self.version
            );
        }
        let resolver = Resolver {
            operations,
            types: &self.types,
            validation_error_url: &self.validation_error_url,
        };
        self.views = self
            .declared_views
            .iter()
            .map(|view| {
                let resolved = view.resolve(&resolver)?;
                resolved.validate()?;
                Ok(resolved)
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        self.lifecycles = self
            .declared_lifecycles
            .iter()
            .map(|lifecycle| {
                let resolved = lifecycle.resolve(&resolver)?;
                resolved.validate()?;
                Ok(resolved)
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        self.metadata_files = self
            .metadata
            .iter()
            .map(|instances| instances.resolve(operations, groups))
            .collect::<anyhow::Result<Vec<_>>>()
            .context("metadata")?;
        Ok(())
    }

    /// Fold another document's extension into this one; versions must match.
    pub fn merge(&mut self, other: GraphqlExtension) -> anyhow::Result<()> {
        if self.version == 0 {
            self.version = other.version;
        } else if other.version != self.version {
            anyhow::bail!(
                "{EXTENSION_KEY} version {} does not match version {} of another document",
                other.version,
                self.version
            );
        }
        if self.validation_error_url.is_empty() {
            self.validation_error_url = other.validation_error_url;
        } else if !other.validation_error_url.is_empty()
            && other.validation_error_url != self.validation_error_url
        {
            anyhow::bail!("documents disagree on {EXTENSION_KEY}.validationErrorUrl");
        }
        self.types.merge(other.types)?;
        self.declared_views.extend(other.declared_views);
        self.metadata.extend(other.metadata);
        self.declared_lifecycles.extend(other.declared_lifecycles);
        Ok(())
    }

    /// The distinct topics the read side caches, including mutation state topics when mutations are served.
    pub fn read_topics(&self, with_mutations: bool) -> Vec<String> {
        let mut topics: Vec<String> = Vec::new();
        let mut push = |topic: String| {
            if !topic.is_empty() && !topics.contains(&topic) {
                topics.push(topic);
            }
        };
        for view in &self.views {
            view.topics().into_iter().for_each(&mut push);
            if with_mutations {
                for (_, def) in view.mutations() {
                    push(def.state_topic.clone());
                    push(def.confirm_topic().unwrap_or_default().to_string());
                }
            }
        }
        for lifecycle in &self.lifecycles {
            lifecycle.read_topics().into_iter().for_each(&mut push);
            if with_mutations {
                for (_, def) in lifecycle.mutations() {
                    push(def.state_topic.clone());
                    push(def.confirm_topic().unwrap_or_default().to_string());
                }
            }
        }
        topics
    }

    /// Number of mutations across views and lifecycles (directives included).
    pub fn mutation_count(&self) -> usize {
        self.views
            .iter()
            .map(|v| v.mutations().count())
            .sum::<usize>()
            + self
                .lifecycles
                .iter()
                .map(|l| l.mutations().count() + l.directives.len())
                .sum::<usize>()
    }
}

/// Parse the unresolved extension from a document's root extensions; `None` when it has none.
pub fn parse_extension(
    extensions: Option<&BTreeMap<String, Value>>,
    components: Option<&Value>,
    document: &str,
) -> anyhow::Result<Option<GraphqlExtension>> {
    let Some(raw) = extensions.and_then(|e| e.get(EXTENSION_KEY)) else {
        return Ok(None);
    };
    let declared: ExtensionDocument = serde_json::from_value(raw.clone())
        .with_context(|| format!("failed to parse {EXTENSION_KEY}"))?;
    let types = TypeIndex::resolve(&declared.types, components, document)
        .with_context(|| format!("{EXTENSION_KEY}.types"))?;
    Ok(Some(GraphqlExtension {
        version: declared.version,
        validation_error_url: declared.validation_error_url,
        types,
        declared_views: declared.views,
        declared_lifecycles: declared.lifecycles,
        metadata: declared.metadata,
        views: Vec::new(),
        lifecycles: Vec::new(),
        metadata_files: Vec::new(),
    }))
}

#[cfg(test)]
pub(crate) mod fixtures {
    // One small document shared by the extension tests.

    use super::*;
    use serde_json::json;

    pub const DOCUMENT: &str = "thrs.json";

    pub fn op(
        action: OperationAction,
        address: &str,
        pattern: &str,
        payload: Value,
    ) -> OperationDef {
        OperationDef {
            action,
            address: address.to_string(),
            pattern: pattern.to_string(),
            document: DOCUMENT.to_string(),
            payload: Some(payload),
            parameter_schemas: BTreeMap::new(),
        }
    }

    pub fn components() -> Value {
        json!({"schemas": {
            "Mode": {"title": "Mode", "type": "integer", "enum": [0, 1], "x-enum-varnames": ["OFF", "ON"]},
            "StampedFloat": {"type": "object", "properties": {
                "Value": {"type": "number"}, "TimeStamp": {"type": "string", "format": "date-time"}}},
            "StampedMode": {"type": "object", "properties": {
                "Value": {"$ref": "#/components/schemas/Mode"}, "TimeStamp": {"type": "string"}}},
            "FlowSensor": {"title": "FlowSensor", "type": "object",
                "properties": {"Flow": {"$ref": "#/components/schemas/StampedFloat"}}},
            "Pump": {"title": "Pump", "type": "object", "properties": {
                "Dutypoint": {"$ref": "#/components/schemas/StampedFloat"},
                "ControlMode": {"$ref": "#/components/schemas/StampedMode"}}},
            "ControlValues": {"title": "ControlValues", "type": "object",
                "properties": {"pump1": {"$ref": "#/components/schemas/Pump"}},
                "x-derived": [{"key": "PumpMirror", "leaves": {"Dutypoint": {"component": "pump1", "leaf": "Dutypoint"}}}]},
            "Parameters": {"title": "Parameters", "type": "object", "properties": {
                "CoolingFlow": {"type": "number", "minimum": 0, "default": 25},
                "MaxFlow": {"type": "number"},
                "Tuning": {"type": "array", "prefixItems": [{"type": "number"}]}},
                "x-invariants": [{"lhs": "CoolingFlow", "op": "le", "rhs": "MaxFlow", "error": "cooling flow above max"}]},
            "AutomationMode": {"title": "AutomationMode", "type": "object",
                "properties": {"Mode": {"type": "string"}}},
            "ControlMode": {"title": "ControlMode", "type": "object",
                "properties": {"Mode": {"type": "string"}}},
            "SwitchingControlMode": {"title": "SwitchingControlMode", "type": "object", "properties": {
                "AutomaticMode": {"anyOf": [{"$ref": "#/components/schemas/ControlMode"}, {"type": "null"}]}}},
            "Status": {"title": "Status", "type": "object", "properties": {
                "Status": {"type": "string"}, "SimulationTime": {"type": "string", "format": "date-time"}}},
            "Play": {"title": "Play", "type": "object",
                "properties": {"PlaybackRate": {"type": "number", "minimum": 0, "default": 1.0}}},
            "Inputs": {"title": "Inputs", "type": "object",
                "properties": {"pump": {"$ref": "#/components/schemas/Pump"}}}
        }})
    }

    fn reference(name: &str) -> Value {
        json!({"$ref": format!("#/components/schemas/{name}")})
    }

    pub fn operations() -> OperationIndex {
        let mut sensors = op(
            OperationAction::Send,
            "dev/thrusters/{field}",
            "dev/thrusters/+",
            json!({"anyOf": [reference("FlowSensor"), reference("Pump")]}),
        );
        sensors.parameter_schemas = BTreeMap::from([
            ("thrusters-flow-aft".to_string(), reference("FlowSensor")),
            ("thrusters-pump1".to_string(), reference("Pump")),
        ]);
        OperationIndex::from([
            ("dev.thrusters.send".to_string(), sensors),
            (
                "ctl.parameters.send".to_string(),
                op(
                    OperationAction::Send,
                    "ctl/{module}/parameters",
                    "ctl/+/parameters",
                    reference("Parameters"),
                ),
            ),
            (
                "ctl.parameters.set.receive".to_string(),
                op(
                    OperationAction::Receive,
                    "ctl/{module}/parameters/set",
                    "ctl/+/parameters/set",
                    reference("Parameters"),
                ),
            ),
            (
                "ctl.manual-values.send".to_string(),
                op(
                    OperationAction::Send,
                    "ctl/{module}/manual-values",
                    "ctl/+/manual-values",
                    reference("ControlValues"),
                ),
            ),
            (
                "ctl.manual-values.set.receive".to_string(),
                op(
                    OperationAction::Receive,
                    "ctl/{module}/manual-values/set",
                    "ctl/+/manual-values/set",
                    reference("ControlValues"),
                ),
            ),
            (
                "ctl.control-mode.send".to_string(),
                op(
                    OperationAction::Send,
                    "ctl/{module}/control-mode",
                    "ctl/+/control-mode",
                    reference("SwitchingControlMode"),
                ),
            ),
            (
                "ctl.automation-mode.set.receive".to_string(),
                op(
                    OperationAction::Receive,
                    "ctl/{module}/automation-mode/set",
                    "ctl/+/automation-mode/set",
                    reference("AutomationMode"),
                ),
            ),
            (
                "sim.status.send".to_string(),
                op(
                    OperationAction::Send,
                    "sim/status",
                    "sim/status",
                    reference("Status"),
                ),
            ),
            (
                "sim.play.receive".to_string(),
                op(
                    OperationAction::Receive,
                    "sim/play",
                    "sim/play",
                    reference("Play"),
                ),
            ),
            (
                "sim.inputs.send".to_string(),
                op(
                    OperationAction::Send,
                    "sim/inputs",
                    "sim/inputs",
                    reference("Inputs"),
                ),
            ),
            (
                "sim.inputs.set.receive".to_string(),
                op(
                    OperationAction::Receive,
                    "sim/inputs/set",
                    "sim/inputs/set",
                    reference("Inputs"),
                ),
            ),
        ])
    }

    pub fn types() -> Value {
        json!({
            "SensorFlowSensorType": {"schema": reference("FlowSensor")},
            "ControlPumpType": {"schema": reference("Pump")},
            "ThrustersControlValuesType": {"schema": reference("ControlValues")},
            "ThrustersParametersType": {"schema": reference("Parameters")},
            "ThrustersControlModeType": {"schema": reference("ControlMode")},
            "SwitchingControlModeType": {"schema": reference("SwitchingControlMode")},
            "ThrustersSimulationInputsType": {"schema": reference("Inputs")}
        })
    }

    pub fn type_index() -> TypeIndex {
        let declared: BTreeMap<String, TypeSpec> = serde_json::from_value(types()).unwrap();
        TypeIndex::resolve(&declared, Some(&components()), DOCUMENT).unwrap()
    }

    pub fn groups() -> Vec<TopicGroupDef> {
        vec![TopicGroupDef {
            group: "dev/thrusters".into(),
            pattern: "dev/thrusters/+".into(),
            params: vec!["field".into()],
            fields: Vec::new(),
            payload_schema: None,
            field_schemas: BTreeMap::new(),
            value_extensions: BTreeMap::new(),
            ttl_secs: 0,
        }]
    }

    pub fn extension_json() -> Value {
        json!({
            "version": EXTENSION_VERSION,
            "types": types(),
            "views": [{
                "gql": "modules", "typeName": "ControlModules",
                "members": [{"gql": "thrusters", "typeName": "ThrustersControlModule",
                    "sections": [
                        {"kind": "stampedFields", "gql": "sensorValues", "typeName": "ThrustersSensorValuesType",
                         "fields": [{"gql": "thrustersFlowAft",
                                     "operation": {"operation": "dev.thrusters.send", "parameters": {"field": "thrusters-flow-aft"}}}]},
                        {"kind": "object", "gql": "parameters", "typeName": "ThrustersParametersType",
                         "operation": {"operation": "ctl.parameters.send", "parameters": {"module": "thrusters"}}},
                        {"kind": "object", "gql": "controlValues", "typeName": "ThrustersControlValuesType",
                         "fields": [{"key": "pump1",
                                     "operation": {"operation": "dev.thrusters.send", "parameters": {"field": "thrusters-pump1"}},
                                     "wireKeys": {"Dutypoint": "CC_DutyPoint"}}]},
                        {"kind": "switch", "gql": "controlMode", "typeName": "SwitchingControlModeType",
                         "operation": {"operation": "ctl.control-mode.send", "parameters": {"module": "thrusters"}},
                         "key": "AutomaticMode", "flagField": "automatic", "objectField": "automaticMode",
                         "objectTypeName": "ThrustersControlModeType"}
                    ],
                    "mutations": [
                        {"gql": "thrustersParameterSetCoolingFlow", "kind": "setField",
                         "argName": "value", "key": "CoolingFlow", "returns": "parameters",
                         "state": {"operation": "ctl.parameters.send", "parameters": {"module": "thrusters"}},
                         "target": {"operation": "ctl.parameters.set.receive", "parameters": {"module": "thrusters"}},
                         "missingError": "No parameters available to update",
                         "confirm": {"timeoutS": 5, "timeoutError": "Timeout when setting parameters"}},
                        {"gql": "thrustersControlSetPump1", "kind": "setComponent",
                         "argName": "value", "key": "pump1", "inputTypeName": "PumpInputType", "returns": "controlValues",
                         "state": {"operation": "ctl.manual-values.send", "parameters": {"module": "thrusters"}},
                         "target": {"operation": "ctl.manual-values.set.receive", "parameters": {"module": "thrusters"}}},
                        {"gql": "thrustersSetAutomationMode", "kind": "setFlag",
                         "argName": "automatic", "key": "Mode", "trueValue": "automatic", "falseValue": "manual",
                         "target": {"operation": "ctl.automation-mode.set.receive", "parameters": {"module": "thrusters"}},
                         "confirm": {"operation": {"operation": "ctl.control-mode.send", "parameters": {"module": "thrusters"}},
                                     "key": "AutomaticMode", "presence": true, "timeoutS": 5, "timeoutError": "Timeout when setting automation mode"}}
                    ]
                }]
            }],
            "metadata": [{"operation": "dev.thrusters.send", "instances": {
                "thrusters-flow-aft": {"field": "thrusters_flow_aft"}}}],
            "lifecycles": [{
                "gql": "simulation", "stateTypeName": "SimulationState", "waitTimeoutS": 5,
                "status": {"operation": {"operation": "sim.status.send"}, "key": "Status",
                           "fields": [{"key": "Status"}, {"key": "SimulationTime", "gql": "time"}]},
                "objects": [{"gql": "inputs", "operation": {"operation": "sim.inputs.send"},
                             "unionType": "SimulationInputsType", "memberSection": "inputs"}],
                "directives": [{"gql": "simulationPlay", "target": {"operation": "sim.play.receive"},
                                "key": "PlaybackRate", "allowedFrom": ["available"], "expectStatus": "running",
                                "preconditionError": "Can only play an available simulation",
                                "missingError": "No simulation status available, cannot play"}],
                "members": [{"name": "thrusters",
                    "sections": [{"kind": "object", "gql": "inputs", "typeName": "ThrustersSimulationInputsType"}],
                    "mutations": [{"gql": "thrustersSimulationSetPump", "kind": "setComponent",
                                   "argName": "value", "key": "pump", "inputTypeName": "PumpInputType", "returns": "inputs",
                                   "state": {"operation": "sim.inputs.send"}, "target": {"operation": "sim.inputs.set.receive"}}]}]
            }]
        })
    }

    pub fn root(x: Value) -> BTreeMap<String, Value> {
        BTreeMap::from([(EXTENSION_KEY.to_string(), x)])
    }

    /// Parse and resolve `json` as this document's extension.
    pub fn resolved(json: Value) -> anyhow::Result<GraphqlExtension> {
        let components = components();
        let mut ext = parse_extension(Some(&root(json)), Some(&components), DOCUMENT)?
            .expect("extension present");
        ext.resolve(&operations(), &groups())?;
        Ok(ext)
    }
}

#[cfg(test)]
mod tests {
    use super::fixtures::*;
    use super::*;
    use serde_json::json;

    #[test]
    fn test_parse_resolve_and_read_topics() {
        let ext = resolved(extension_json()).unwrap();
        assert_eq!(ext.views[0].members[0].gql, "thrusters");
        assert_eq!(
            ext.views[0].members[0].mutations[0].set_topic,
            "ctl/thrusters/parameters/set"
        );
        let files = &ext.metadata_files;
        assert_eq!(files.len(), 1);
        assert_eq!(files[0].group, "dev/thrusters");
        assert_eq!(files[0].topics[0].topic, "dev/thrusters/thrusters-flow-aft");
        assert_eq!(
            files[0].topics[0].metadata["field"],
            json!("thrusters_flow_aft")
        );
        assert_eq!(
            ext.read_topics(false),
            vec![
                "dev/thrusters/thrusters-flow-aft".to_string(),
                "ctl/thrusters/parameters".to_string(),
                "dev/thrusters/thrusters-pump1".to_string(),
                "ctl/thrusters/control-mode".to_string(),
                "sim/status".to_string(),
                "sim/inputs".to_string(),
            ]
        );
        assert!(ext
            .read_topics(true)
            .contains(&"ctl/thrusters/manual-values".to_string()));
        assert_eq!(ext.mutation_count(), 5);
    }

    #[test]
    fn test_document_without_extension_is_none() {
        assert!(parse_extension(None, None, DOCUMENT).unwrap().is_none());
        let other = BTreeMap::from([("x-other".to_string(), json!(1))]);
        assert!(parse_extension(Some(&other), None, DOCUMENT)
            .unwrap()
            .is_none());
    }

    #[test]
    fn test_unsupported_version_is_rejected() {
        let mut json = extension_json();
        json["version"] = json!(1);
        let err = resolved(json).unwrap_err();
        assert!(err.to_string().contains("version 1"), "{err}");
    }

    #[test]
    fn test_types_are_read_against_the_components() {
        let index = type_index();
        let pump = index.get("ControlPumpType").unwrap();
        let leaves = pump.leaves(&BTreeMap::from([(
            "Dutypoint".to_string(),
            "CC_DutyPoint".to_string(),
        )]));
        assert_eq!(leaves.len(), 2);
        assert_eq!(leaves[0].gql, "dutypoint");
        assert_eq!(leaves[0].actuated_key.as_deref(), Some("CC_DutyPoint"));
        assert_eq!(leaves[1].enum_type.as_deref(), Some("Mode"));
        assert_eq!(leaves[1].enum_values.as_ref().unwrap()["1"], "ON");
        assert_eq!(
            index
                .for_reference(DOCUMENT, "#/components/schemas/Pump")
                .unwrap()
                .name,
            "ControlPumpType"
        );
        assert_eq!(
            index
                .get("ThrustersParametersType")
                .unwrap()
                .invariants
                .len(),
            1
        );
        assert_eq!(
            index
                .get("ThrustersControlValuesType")
                .unwrap()
                .derived
                .len(),
            1
        );
        assert!(index.get("Nope").is_err());
    }

    #[test]
    fn test_two_types_from_one_schema_and_an_unknown_ref_are_errors() {
        let mut json = extension_json();
        json["types"]["OtherPumpType"] = json!({"schema": {"$ref": "#/components/schemas/Pump"}});
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("both served from"), "{err:#}");

        let mut json = extension_json();
        json["types"]["Nope"] = json!({"schema": {"$ref": "#/components/schemas/Nope"}});
        let err = resolved(json).unwrap_err();
        assert!(format!("{err:#}").contains("does not resolve"), "{err:#}");
    }

    #[test]
    fn test_metadata_must_enumerate_a_declared_send_operation() {
        let mut json = extension_json();
        json["metadata"][0]["operation"] = json!("ctl.parameters.set.receive");
        let err = resolved(json).unwrap_err();
        assert!(
            format!("{err:#}").contains("not a send operation"),
            "{err:#}"
        );

        let mut json = extension_json();
        json["metadata"][0]["operation"] = json!("ctl.parameters.send");
        let err = resolved(json).unwrap_err();
        assert!(
            format!("{err:#}").contains("not a subscribed topic group"),
            "{err:#}"
        );
    }

    #[test]
    fn test_unknown_operation_is_a_load_error() {
        let mut json = extension_json();
        json["views"][0]["members"][0]["sections"][0]["fields"][0]["operation"]["operation"] =
            json!("nope");
        let err = resolved(json).unwrap_err();
        assert!(
            format!("{err:#}").contains("unknown operation 'nope'"),
            "{err:#}"
        );
    }

    #[test]
    fn test_merge_appends_views() {
        let components = components();
        let mut ext = parse_extension(Some(&root(extension_json())), Some(&components), DOCUMENT)
            .unwrap()
            .unwrap();
        let other = parse_extension(
            Some(&root(json!({"version": EXTENSION_VERSION, "views": [
                {"gql": "other", "typeName": "Other", "members": []}]}))),
            None,
            "other.json",
        )
        .unwrap()
        .unwrap();
        ext.merge(other).unwrap();
        ext.resolve(&operations(), &groups()).unwrap();
        assert_eq!(ext.views.len(), 2);
        assert_eq!(
            ext.read_topics(true)[..2],
            [
                "dev/thrusters/thrusters-flow-aft".to_string(),
                "ctl/thrusters/parameters".to_string()
            ]
        );
    }
}
