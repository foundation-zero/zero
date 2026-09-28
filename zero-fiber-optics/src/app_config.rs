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

    /// Username and password, present only when both are set to non-empty values.
    ///
    /// Empty strings (as produced by an unset `MQTT_USERNAME=`/`MQTT_PASSWORD=`)
    /// mean "no credentials", not "credentials that happen to be empty". The
    /// broker sees an anonymous connection either way, but logging needs to say
    /// so explicitly instead of reporting a username that was never sent.
    pub fn credentials(&self) -> Option<(&str, &str)> {
        match (self.mqtt_username.as_deref(), self.mqtt_password.as_deref()) {
            (Some(username), Some(password)) if !username.is_empty() && !password.is_empty() => {
                Some((username, password))
            }
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn config_with(username: Option<&str>, password: Option<&str>) -> AppConfig {
        AppConfig {
            mqtt_host: "localhost".to_string(),
            mqtt_port: 1883,
            mqtt_prefix: "telemetry".to_string(),
            mqtt_username: username.map(str::to_string),
            mqtt_password: password.map(str::to_string),
        }
    }

    #[test]
    fn credentials_require_both_username_and_password() {
        assert_eq!(
            config_with(Some("user"), Some("pass")).credentials(),
            Some(("user", "pass"))
        );
        assert_eq!(config_with(Some("user"), None).credentials(), None);
        assert_eq!(config_with(None, Some("pass")).credentials(), None);
        assert_eq!(config_with(None, None).credentials(), None);
    }

    #[test]
    fn credentials_reject_empty_values() {
        assert_eq!(config_with(Some("user"), Some("")).credentials(), None);
        assert_eq!(config_with(Some(""), Some("pass")).credentials(), None);
        assert_eq!(config_with(Some(""), Some("")).credentials(), None);
    }
}
