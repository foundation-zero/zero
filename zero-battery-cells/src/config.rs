use anyhow::{Context, Result};
use serde::Deserialize;

/// Broker, topic and UDP-port settings used by every mode of the binary.
#[derive(Debug, Deserialize, Clone)]
pub struct AppConfig {
    pub mqtt_host: String,
    pub mqtt_port: u16,
    /// First topic path segment. Everything below it is `battery/{pack}/{string}/{module}`.
    pub mqtt_prefix: String,
    /// UDP port the CODESYS PLCs send their NetVar lists to.
    pub udp_port: u16,
    #[serde(default)]
    pub mqtt_username: Option<String>,
    #[serde(default)]
    pub mqtt_password: Option<String>,
}

impl AppConfig {
    /// Environment variables: `MQTT_HOST`, `MQTT_PORT`, `MQTT_PREFIX`, `UDP_PORT`,
    /// and the optional `MQTT_USERNAME`/`MQTT_PASSWORD` pair.
    pub fn load() -> Result<Self, config::ConfigError> {
        config::Config::builder()
            .set_default("mqtt_host", "localhost")?
            .set_default("mqtt_port", 1883_i64)?
            .set_default("mqtt_prefix", "battery")?
            .set_default("udp_port", 50000_i64)?
            .add_source(config::Environment::default())
            .build()?
            .try_deserialize()
    }

    /// Username and password, present only when both are set to non-empty values.
    ///
    /// Empty strings (as produced by an unset `MQTT_USERNAME=`/`MQTT_PASSWORD=`)
    /// mean "no credentials", not "credentials that happen to be empty".
    pub fn credentials(&self) -> Option<(&str, &str)> {
        match (self.mqtt_username.as_deref(), self.mqtt_password.as_deref()) {
            (Some(username), Some(password)) if !username.is_empty() && !password.is_empty() => {
                Some((username, password))
            }
            _ => None,
        }
    }
}

/// Everything needed to link the UDP stream to MQTT: the shared app settings,
/// the declaration template and which lists this replica owns.
#[derive(Debug, Clone)]
pub struct PipelineConfig {
    pub app: AppConfig,
    /// Path of the template NetVar declaration; every known pack shares its layout.
    pub nvl_file: String,
    /// Restrict decoding to these list ids when set; unset means every known list id.
    pub owned_list_ids: Option<Vec<u16>>,
}

impl PipelineConfig {
    /// Environment variables: `NVL_FILE` and the optional `OWN_LIST_IDS`,
    /// on top of the [`AppConfig`] set.
    pub fn load() -> Result<Self> {
        let app = AppConfig::load().context("Failed to load environment configuration")?;
        let nvl_file = env_string("NVL_FILE")?;
        let owned_list_ids: Option<Vec<u16>> = env_string_opt("OWN_LIST_IDS")
            .map(|raw| crate::mapping::parse_owned_list_ids(&raw))
            .transpose()?;
        Ok(Self {
            app,
            nvl_file,
            owned_list_ids,
        })
    }
}

/// Read one environment variable, failing when it is unset.
fn env_string(name: &str) -> Result<String> {
    std::env::var(name).with_context(|| format!("Environment variable {} is required", name))
}

/// Read one environment variable, treating unset or empty as absent.
fn env_string_opt(name: &str) -> Option<String> {
    match std::env::var(name) {
        Ok(raw) if !raw.is_empty() => Some(raw),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn credentials_require_both_username_and_password() {
        let mut config = AppConfig {
            mqtt_host: "localhost".to_string(),
            mqtt_port: 1883,
            mqtt_prefix: "battery".to_string(),
            udp_port: 50000,
            mqtt_username: None,
            mqtt_password: None,
        };
        assert_eq!(config.credentials(), None);

        config.mqtt_username = Some("user".to_string());
        assert_eq!(config.credentials(), None);

        config.mqtt_password = Some("".to_string());
        assert_eq!(config.credentials(), None);

        config.mqtt_password = Some("pass".to_string());
        assert_eq!(config.credentials(), Some(("user", "pass")));
    }
}
