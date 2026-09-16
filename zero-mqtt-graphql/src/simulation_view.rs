//! Simulation spec (`thrs-simulation.json`, from `print-simulation-view`).
//!
//! Lets zero-mqtt-graphql serve thrs-api's `simulation { status time inputs
//! outputs }` query, the `simulationPlay`/`simulationPause`/`simulationStep`
//! directives and the per-simulation `{sim}SimulationSet{Component}` input
//! mutations 1:1 (zero-ui `STATUS_QUERY`/`QUERY_ALL`/`useSimulationStore`).
//! Everything is an MQTT relay on the simulator prefix, mirroring thrs-api's
//! `SimulationApiChannels`/`DirectivesApiChannels` (see `build_simulation_view`
//! in `thrs.spec.asyncapi`): the retained status object, one whole inputs and
//! one whole outputs object (typed by whichever simulation's model matches),
//! directives that publish a message and wait for the status to change, and
//! input mutations that restamp a component into the cached inputs object.

use std::path::Path;

use anyhow::Context;
use serde::Deserialize;

use crate::modules_view::{validate_enum_leaves, ObjectSectionDef};
use crate::mutations_view::{validate_mutation, MutationDef};

/// File name of the simulation spec inside a spec directory.
pub const SIMULATION_VIEW_FILE: &str = "thrs-simulation.json";

/// By-alias keys of the fields read off the status object.
#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
pub struct StatusKeys {
    /// Key holding the status string (`available`/`running`/`stepping`).
    pub status: String,
    /// Key holding the simulation time (an ISO timestamp).
    pub time: String,
}

/// One simulation directive (play / pause / step): the message topic and
/// payload, the statuses it is allowed from, the status it waits for, and
/// thrs-api's exact error strings.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct DirectiveDef {
    /// thrs-api's mutation name (`simulationPlay`).
    pub gql_name: String,
    pub topic: String,
    /// GraphQL argument name (`playbackRate` / `seconds`); none for pause.
    #[serde(default)]
    pub arg_name: Option<String>,
    /// By-alias payload key of the argument (`PlaybackRate` / `Seconds`).
    #[serde(default)]
    pub payload_key: Option<String>,
    /// Whether the argument is non-null.
    #[serde(default)]
    pub arg_required: bool,
    /// Default used when a nullable argument is omitted.
    #[serde(default)]
    pub default: Option<f64>,
    /// Numeric bounds on the argument (thrs-api's message model validation).
    #[serde(default)]
    pub bounds: Option<crate::mutations_view::Bounds>,
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

/// One simulation (thrusters, pcm, ..., highTemperature, thrs). Its inputs and
/// outputs objects are sections (thrs-api's `ThrustersSimulationInputsType`
/// etc., component fields with Stamped leaves) without a topic of their own:
/// the whole inputs/outputs object lives on the [`SimulationView`]'s topics.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct SimulationDef {
    /// camelCase name, also the mutation prefix (`highTemperature`).
    pub name: String,
    #[serde(default)]
    pub inputs: ObjectSectionDef,
    #[serde(default)]
    pub outputs: ObjectSectionDef,
    /// The `simulation`-kind input mutations of this simulation.
    #[serde(default)]
    pub mutations: Vec<MutationDef>,
}

/// The simulation spec file.
#[derive(Debug, Clone, Default, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct SimulationView {
    /// thrs-api's type for the `simulation` query (`SimulationState`).
    pub state_type_name: String,
    pub status_topic: String,
    pub status_keys: StatusKeys,
    pub inputs_topic: String,
    pub outputs_topic: String,
    pub inputs_set_topic: String,
    /// thrs-api's union type names (`SimulationInputsType`/`SimulationOutputsType`).
    pub inputs_union_type: String,
    pub outputs_union_type: String,
    /// The directives (play / pause / step) thrs-api exposes as mutations.
    #[serde(default)]
    pub directives: Vec<DirectiveDef>,
    /// Seconds a directive waits for the expected status (thrs-api `WAIT_TIMEOUT`).
    pub wait_timeout_s: f64,
    #[serde(default)]
    pub simulations: Vec<SimulationDef>,
}

impl SimulationView {
    /// The topics the cache must subscribe to for the read side (status,
    /// inputs, outputs). Directive/set topics are publish-only.
    pub fn read_topics(&self) -> Vec<String> {
        vec![
            self.status_topic.clone(),
            self.inputs_topic.clone(),
            self.outputs_topic.clone(),
        ]
    }

    /// Every `simulation` mutation across all simulations.
    pub fn mutations(&self) -> impl Iterator<Item = (&SimulationDef, &MutationDef)> {
        self.simulations
            .iter()
            .flat_map(|s| s.mutations.iter().map(move |m| (s, m)))
    }
}

/// Whether this path is the simulation spec file.
pub fn is_simulation_view_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|n| n.to_str())
        .map(|n| n == SIMULATION_VIEW_FILE)
        .unwrap_or(false)
}

/// Load the simulation spec from `spec_dir`, or `None` when the file is absent.
pub fn load_simulation_view(spec_dir: &str) -> anyhow::Result<Option<SimulationView>> {
    let path = Path::new(spec_dir).join(SIMULATION_VIEW_FILE);
    if !path.exists() {
        return Ok(None);
    }
    let raw = std::fs::read_to_string(&path)
        .with_context(|| format!("failed to read {}", path.display()))?;
    let view: SimulationView = serde_json::from_str(&raw)
        .with_context(|| format!("failed to parse simulation view {}", path.display()))?;
    validate_enum_leaves(
        view.simulations
            .iter()
            .flat_map(|s| s.inputs.fields.iter().chain(s.outputs.fields.iter()))
            .flat_map(|f| f.leaves.iter()),
    )
    .with_context(|| format!("invalid simulation view {}", path.display()))?;
    for (_, def) in view.mutations() {
        validate_mutation(def)
            .with_context(|| format!("invalid simulation view {}", path.display()))?;
    }
    Ok(Some(view))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_minimal_simulation_view() {
        let json = r#"{
            "stateTypeName": "SimulationState",
            "statusTopic": "sim/status",
            "statusKeys": {"status": "Status", "time": "SimulationTime"},
            "inputsTopic": "sim/simulation-inputs",
            "outputsTopic": "sim/simulation-outputs",
            "inputsSetTopic": "sim/simulation-inputs/set",
            "inputsUnionType": "SimulationInputsType",
            "outputsUnionType": "SimulationOutputsType",
            "waitTimeoutS": 5,
            "directives": [
                {"gqlName": "simulationPlay", "topic": "sim/play", "argName": "playbackRate",
                 "payloadKey": "PlaybackRate", "default": 1.0,
                 "allowedFrom": ["available", "running"], "expectStatus": "running"},
                {"gqlName": "simulationPause", "topic": "sim/pause",
                 "allowedFrom": ["running"], "expectStatus": "available"},
                {"gqlName": "simulationStep", "topic": "sim/step", "argName": "seconds",
                 "payloadKey": "Seconds", "argRequired": true,
                 "allowedFrom": ["available"], "expectStatus": "stepping"}
            ],
            "simulations": [{
                "name": "thrusters",
                "inputs": {"typeName": "ThrustersSimulationInputsType", "fields": [
                    {"gqlField": "thrustersPcs", "key": "ThrustersPcs", "typeName": "SimulationPcsType", "leaves": [
                        {"gql": "mode", "raw": "Mode", "type": "String", "enumType": "PcsMode",
                         "enumValues": {"0": "OFF"}}]}]},
                "outputs": {"typeName": "ThrustersSimulationOutputsType", "fields": []},
                "mutations": [{"gqlName": "thrustersSimulationSetThrustersPcs", "kind": "simulation",
                    "argName": "value", "payloadKey": "ThrustersPcs",
                    "inputTypeName": "PcsInputType",
                    "inputFields": [{"argName": "mode", "wireKey": "Mode", "type": "String",
                        "enumType": "PcsMode", "enumValues": {"0": "OFF"}}],
                    "stateTopic": "sim/simulation-inputs", "setTopic": "sim/simulation-inputs/set"}]
            }]
        }"#;
        let view: SimulationView = serde_json::from_str(json).unwrap();
        assert_eq!(view.status_keys.time, "SimulationTime");
        assert_eq!(view.wait_timeout_s, 5.0);
        assert_eq!(view.inputs_union_type, "SimulationInputsType");
        assert_eq!(view.read_topics().len(), 3);
        let (sim, m) = view.mutations().next().unwrap();
        assert_eq!(sim.name, "thrusters");
        assert_eq!(m.input_type_name.as_deref(), Some("PcsInputType"));
        assert!(m.input_fields[0].required);
        assert_eq!(m.input_fields[0].enum_type.as_deref(), Some("PcsMode"));
        assert_eq!(view.directives[0].default, Some(1.0));
        assert!(view.directives[2].arg_required);
    }

    #[test]
    fn test_is_simulation_view_file() {
        assert!(is_simulation_view_file(Path::new(
            "/specs/thrs-simulation.json"
        )));
        assert!(!is_simulation_view_file(Path::new(
            "/specs/thrs-thrusters-module.json"
        )));
    }
}
