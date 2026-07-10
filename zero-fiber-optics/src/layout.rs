use heck::ToKebabCase;
use serde_json::{Map, Number, Value};
use std::collections::{HashMap, HashSet};

use crate::config::Port;

/// Holds the ordered list of variable (and bit) names for a port.
/// Variables borrow keys from this structure during parsing/publishing.
#[derive(Debug, Clone)]
pub struct Layout {
    pub channel: String,
    keys: HashSet<String>,
}

/// A single parsed measurement with a key borrowed from `Layout`.
#[derive(Debug, Clone)]
pub enum VariableValue {
    Number(f64),
    Boolean(bool),
}

/// A single parsed measurement with a key borrowed from `Layout`.
#[derive(Debug, Clone)]
pub struct Variable<'a> {
    pub key: &'a str,
    pub value: VariableValue,
}

/// Maps variable names to MQTT topic-segment overrides.
/// If a name is absent the variable name itself is used as the topic segment.
pub type TopicMap = HashMap<String, String>;

/// Resolve the MQTT topic segment for a variable or bit name.
/// Uses the override from `topic_map` if present; otherwise converts the name to kebab-case.
pub fn topic_segment(topic_map: &TopicMap, name: &str) -> String {
    topic_map
        .get(name)
        .cloned()
        .unwrap_or_else(|| name.to_kebab_case())
}

/// Build a JSON object payload for one parsed packet.
///
/// Keys follow the same topic-segment resolution used for MQTT variables:
/// topic-map override first, then kebab-case fallback.
pub fn packet_payload(
    variables: &[Variable<'_>],
    topic_map: &TopicMap,
) -> anyhow::Result<Map<String, Value>> {
    variables
        .iter()
        .map(|var| {
            let key = topic_segment(topic_map, var.key);
            let value = match &var.value {
                VariableValue::Number(v) => {
                    let n = Number::from_f64(*v)
                        .ok_or_else(|| anyhow::anyhow!("non-finite numeric value for '{}'", key))?;
                    Value::Number(n)
                }
                VariableValue::Boolean(v) => Value::Bool(*v),
            };
            Ok((key, value))
        })
        .collect()
}

impl Layout {
    /// Build a `Layout` from a `Port` definition.
    /// Top-level variable names and individual bit names are all registered.
    pub fn from_port(port: &Port) -> Self {
        let keys = port
            .variables
            .iter()
            .flat_map(|var| {
                let main = std::iter::once(var.name.clone());
                let bits: Vec<String> = if var.var_type.ends_with("BitBoolRegister") {
                    var.bits.iter().map(|b| b.name.clone()).collect()
                } else {
                    vec![]
                };
                main.chain(bits)
            })
            .collect::<HashSet<_>>();

        Layout {
            channel: port.channel.clone(),
            keys,
        }
    }

    /// Return the key borrowed from this layout.
    /// Panics if the name does not exist in the layout.
    pub fn key<'a>(&'a self, name: &str) -> &'a str {
        self.keys
            .get(name)
            .unwrap_or_else(|| panic!("missing key '{}' in layout", name))
            .as_str()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Bit, Port, Var};

    fn make_var(name: &str, var_type: &str, bits: Vec<Bit>) -> Var {
        Var {
            num: None,
            var_type: var_type.to_string(),
            units: None,
            factor: None,
            offset: None,
            decimals: None,
            class: None,
            tags: None,
            description: None,
            name: name.to_string(),
            bits,
        }
    }

    #[test]
    fn from_port_registers_variables_and_bits_in_order() {
        let port = Port {
            numport: 50000,
            channel: "FiberA".to_string(),
            frequency: None,
            mode: None,
            variables: vec![
                make_var("Power", "UnSignedInt16", vec![]),
                make_var(
                    "Flags",
                    "8BitBoolRegister",
                    vec![
                        Bit {
                            num: 0,
                            name: "Alarm".to_string(),
                        },
                        Bit {
                            num: 3,
                            name: "LinkUp".to_string(),
                        },
                    ],
                ),
            ],
        };

        let layout = Layout::from_port(&port);
        assert_eq!(layout.channel, "FiberA");
        assert_eq!(layout.key("Power"), "Power");
        assert_eq!(layout.key("Flags"), "Flags");
        assert_eq!(layout.key("Alarm"), "Alarm");
        assert_eq!(layout.key("LinkUp"), "LinkUp");
    }

    #[test]
    fn key_returns_expected_name() {
        let port = Port {
            numport: 50001,
            channel: "FiberB".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Temperature", "SignedInt16", vec![])],
        };

        let layout = Layout::from_port(&port);
        assert_eq!(layout.key("Temperature"), "Temperature");
    }

    #[test]
    #[should_panic(expected = "missing key 'Unknown' in layout")]
    fn key_panics_for_missing_name() {
        let port = Port {
            numport: 50002,
            channel: "FiberC".to_string(),
            frequency: None,
            mode: None,
            variables: vec![make_var("Voltage", "UnSignedInt16", vec![])],
        };

        let layout = Layout::from_port(&port);
        let _ = layout.key("Unknown");
    }

    #[test]
    fn packet_payload_uses_topic_segments_and_values() {
        let mut topic_map = TopicMap::new();
        topic_map.insert("PacketCounter".to_string(), "packet-counter".to_string());

        let variables = vec![
            Variable {
                key: "PacketCounter",
                value: VariableValue::Number(5.0),
            },
            Variable {
                key: "LinkUp",
                value: VariableValue::Boolean(true),
            },
        ];

        let payload = packet_payload(&variables, &topic_map).expect("payload should serialize");
        assert_eq!(payload["packet-counter"].as_f64(), Some(5.0));
        assert_eq!(payload["link-up"], Value::Bool(true));
    }

    #[test]
    fn packet_payload_rejects_non_finite_numbers() {
        let topic_map = TopicMap::new();
        let variables = vec![Variable {
            key: "Value",
            value: VariableValue::Number(f64::NAN),
        }];

        assert!(packet_payload(&variables, &topic_map).is_err());
    }
}
