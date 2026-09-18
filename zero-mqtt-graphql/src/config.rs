use serde::Deserialize;

/// Default TTL in seconds for cached topic values, used when neither the
/// config nor an AsyncAPI `x-ttl` extension specifies one.
pub const DEFAULT_TTL_SECS: u64 = 300;

#[derive(Debug, Deserialize, Clone)]
pub struct AppConfig {
    #[serde(default = "default_host")]
    pub mqtt_host: String,
    #[serde(default = "default_port")]
    pub mqtt_port: u16,
    #[serde(default)]
    pub mqtt_username: Option<String>,
    #[serde(default)]
    pub mqtt_password: Option<String>,
    #[serde(default = "default_listen_port")]
    pub listen_port: u16,
    /// Default TTL in seconds for cached topic values. Each AsyncAPI schema
    /// may override this with an `x-ttl` extension.
    #[serde(default = "default_ttl")]
    pub default_ttl_secs: u64,
    /// When true, serve mode drops payloads that fail JSON Schema validation
    /// instead of caching them, so the last valid value survives, like thrs-api
    /// rejecting out-of-bounds sensor values. Off by default: an incomplete
    /// spec would otherwise drop valid live data. Env: `STRICT_VALIDATION`.
    #[serde(default)]
    pub strict_validation: bool,
    /// When true, `modules { <m> { sensorValues { … } } }` serves each sensor
    /// field independently: a field whose topic is cached (and carries every
    /// required leaf) resolves, the others resolve null, so a query for one
    /// field answers as soon as that one topic has arrived. Off by default:
    /// thrs-api serves `sensorValues` all-or-nothing (null until its whole
    /// pydantic model validates) and the 1:1 parity mirrors that. Changes the
    /// schema: the sensor fields become nullable. Env: `ENABLE_OPTIONAL_SENSOR_VALUES`.
    #[serde(default)]
    pub enable_optional_sensor_values: bool,
    /// When true, expose thrs-api's parameter mutations (from
    /// `*-mutations.json`) and publish their changes to MQTT. Off by default:
    /// zero-mqtt-graphql is read-only until the write-path is switched on.
    /// Env: `ENABLE_MUTATIONS`.
    #[serde(default)]
    pub enable_mutations: bool,
    /// How the MQTT topic prefixes in the specs are reconciled with the live
    /// broker. `build_time` (default) trusts the prefix baked into each spec by
    /// spec generation (aggregate-specs.sh `--devices-prefix`/
    /// `--controller-prefix`). `runtime` rewrites the spec prefix at load using
    /// `runtime_devices_prefix`/`runtime_controller_prefix`, so the same spec
    /// can target a differently-prefixed broker without regeneration.
    /// Env: `PREFIX_STRATEGY`.
    #[serde(default)]
    pub prefix_strategy: PrefixStrategy,
    /// The devices-topic prefix the specs were generated with (the "from" side
    /// of a `runtime` rewrite). Matches THRS `mqtt_devices_topic_prefix`
    /// default. Env: `SPEC_DEVICES_PREFIX`.
    #[serde(default = "default_spec_devices_prefix")]
    pub spec_devices_prefix: String,
    /// The controller-topic prefix the specs were generated with (the "from"
    /// side of a `runtime` rewrite). Matches THRS `mqtt_controller_topic_prefix`
    /// default. Env: `SPEC_CONTROLLER_PREFIX`.
    #[serde(default = "default_spec_controller_prefix")]
    pub spec_controller_prefix: String,
    /// The devices-topic prefix the live broker actually uses (the "to" side of
    /// a `runtime` rewrite). Only consulted when `prefix_strategy = runtime`.
    /// Env: `RUNTIME_DEVICES_PREFIX`.
    #[serde(default)]
    pub runtime_devices_prefix: Option<String>,
    /// The controller-topic prefix the live broker actually uses (the "to" side
    /// of a `runtime` rewrite). Only consulted when `prefix_strategy = runtime`.
    /// Env: `RUNTIME_CONTROLLER_PREFIX`.
    #[serde(default)]
    pub runtime_controller_prefix: Option<String>,
    /// The simulator-topic prefix the specs were generated with (the "from"
    /// side of a `runtime` rewrite). Matches THRS `mqtt_simulator_topic_prefix`
    /// default. Env: `SPEC_SIMULATOR_PREFIX`.
    #[serde(default = "default_spec_simulator_prefix")]
    pub spec_simulator_prefix: String,
    /// The simulator-topic prefix the live broker actually uses (the "to" side
    /// of a `runtime` rewrite). Only consulted when `prefix_strategy = runtime`.
    /// Env: `RUNTIME_SIMULATOR_PREFIX`.
    #[serde(default)]
    pub runtime_simulator_prefix: Option<String>,
    /// How computed sensor fields (thrs-api pydantic `computed_field`s) are
    /// served. `relay` (default) relays whatever the control loop publishes to
    /// the field's controller topic. `recompute` derives the value in-process
    /// from the raw sensor topics with the same formula thrs-api uses, so it
    /// matches thrs-api's live-computed value (which the loop's published value
    /// can lag). Env: `COMPUTED_MODE`.
    #[serde(default)]
    pub computed_mode: ComputedMode,
}

/// See [`AppConfig::computed_mode`].
#[derive(Debug, Deserialize, Clone, Copy, PartialEq, Eq, Default)]
#[serde(rename_all = "snake_case")]
pub enum ComputedMode {
    /// Relay the control loop's published computed value.
    #[default]
    Relay,
    /// Recompute from raw sensors with thrs-api's formula.
    Recompute,
}

/// See [`AppConfig::prefix_strategy`].
#[derive(Debug, Deserialize, Clone, Copy, PartialEq, Eq, Default)]
#[serde(rename_all = "snake_case")]
pub enum PrefixStrategy {
    /// Trust the prefix baked into the spec at generation time.
    #[default]
    BuildTime,
    /// Rewrite the spec prefix at load time from config.
    Runtime,
}

// function indirect needed by serde
fn default_ttl() -> u64 {
    DEFAULT_TTL_SECS
}

fn default_host() -> String {
    "localhost".into()
}

fn default_port() -> u16 {
    1883
}

fn default_listen_port() -> u16 {
    5103
}

fn default_spec_devices_prefix() -> String {
    "simulation".into()
}

fn default_spec_controller_prefix() -> String {
    "thrs/controller".into()
}

fn default_spec_simulator_prefix() -> String {
    "thrs/simulator".into()
}

impl AppConfig {
    pub fn load() -> Result<Self, config::ConfigError> {
        config::Config::builder()
            .add_source(config::Environment::default())
            .build()?
            .try_deserialize()
    }
}
