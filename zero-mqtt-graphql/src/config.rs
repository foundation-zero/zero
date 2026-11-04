use serde::Deserialize;

/// Default TTL in seconds for cached topic values, used when neither the
/// config nor an AsyncAPI `x-ttl` extension specifies one.
pub const DEFAULT_TTL_SECS: u64 = 300;

/// Default time in seconds a Mutation waits for its State topic to confirm
/// the input.
pub const DEFAULT_MUTATION_TIMEOUT_SECS: u64 = 10;

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
    /// Expose Receive Topics as Mutations. Off by default: the bridge has no
    /// authorization, and these inputs actuate equipment.
    #[serde(default)]
    pub enable_mutations: bool,
    /// How long a Mutation waits for its State topic to confirm the input.
    #[serde(default = "default_mutation_timeout")]
    pub mutation_timeout_secs: u64,
}

// function indirect needed by serde
fn default_ttl() -> u64 {
    DEFAULT_TTL_SECS
}

fn default_mutation_timeout() -> u64 {
    DEFAULT_MUTATION_TIMEOUT_SECS
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
