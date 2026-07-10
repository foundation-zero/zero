use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct AppConfig {
    pub mqtt_host: String,
    pub mqtt_port: u16,
    pub mqtt_prefix: String,
    #[serde(default)]
    pub mqtt_username: Option<String>,
    #[serde(default)]
    pub mqtt_password: Option<String>,
}

impl AppConfig {
    pub fn load() -> Result<Self, config::ConfigError> {
        config::Config::builder()
            .set_default("mqtt_host", "localhost")?
            .set_default("mqtt_port", 1883_i64)?
            .set_default("mqtt_prefix", "telemetry")?
            .add_source(config::Environment::default())
            .build()?
            .try_deserialize()
    }
}
