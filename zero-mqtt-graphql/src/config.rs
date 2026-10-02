use serde::Deserialize;

/// Default TTL in seconds for cached topic values, used when neither the
/// config nor an AsyncAPI `x-ttl` extension specifies one.
pub const DEFAULT_TTL_SECS: u64 = 300;

/// The TTL of a value that never expires (`x-ttl: "unbounded"`).
pub const TTL_UNBOUNDED_SECS: u64 = u64::MAX;

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
    /// Serve mode drops schema-invalid payloads instead of caching them.
    /// Env: `STRICT_VALIDATION`.
    #[serde(default)]
    pub strict_validation: bool,
    /// Serve each `stampedFields` field independently (nullable) instead of
    /// all-or-nothing. Env: `ENABLE_OPTIONAL_SENSOR_VALUES`.
    #[serde(default)]
    pub enable_optional_sensor_values: bool,
    /// Expose the extension's mutations and lifecycle directives. Env: `ENABLE_MUTATIONS`.
    #[serde(default)]
    pub enable_mutations: bool,
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

impl AppConfig {
    pub fn load() -> Result<Self, config::ConfigError> {
        config::Config::builder()
            .add_source(config::Environment::default())
            .build()?
            .try_deserialize()
    }
}
