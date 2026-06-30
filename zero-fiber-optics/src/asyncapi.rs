use asyncapi_rust::{
    indexmap::IndexMap, AsyncApiSpec, Channel, ChannelRef, Components, Info, Message,
    MessageRef, Operation, OperationAction, Schema, SchemaObject,
};
use crate::config::UdpChannels;
use crate::layout::{topic_segment, TopicMap};

/// Dynamically build an AsyncAPI 3.0.0 schema from the loaded configuration.
///
/// Each port channel publishes one packet object under `{prefix}/{channel_name}`.
/// Object properties are keyed by resolved topic segment (override first, kebab-case fallback).
pub fn build_schema(config: &UdpChannels, prefix: &str, topic_map: &TopicMap) -> AsyncApiSpec {
    let mut channels = IndexMap::new();
    let mut operations = IndexMap::new();
    let mut messages = IndexMap::new();

    for port in &config.ports {
        let topic = format!("{}/{}", prefix, port.channel);
        let message_id = message_name(&port.channel, "packet");
        let mut properties = IndexMap::new();
        let mut required = Vec::new();

        for var in &port.variables {
            let topic_seg = topic_segment(topic_map, &var.name);
            if !required.contains(&topic_seg) {
                required.push(topic_seg.clone());
            }
            properties.insert(
                topic_seg,
                Box::new(scalar_schema(
                    var_type_to_schema_type(&var.var_type),
                    payload_description(var.units.as_deref()),
                )),
            );

            // Expand individual bits for bit-register variables
            if var.var_type.ends_with("BitBoolRegister") {
                for bit in &var.bits {
                    let bit_seg = topic_segment(topic_map, &bit.name);
                    if !required.contains(&bit_seg) {
                        required.push(bit_seg.clone());
                    }
                    properties.insert(
                        bit_seg,
                        Box::new(scalar_schema(
                            "boolean",
                            Some(format!("Bit {} of {}", bit.num, var.name)),
                        )),
                    );
                }
            }
        }

        channels.insert(
            topic.clone(),
            Channel {
                address: Some(topic.clone()),
                messages: Some(IndexMap::from([(
                    message_id.clone(),
                    MessageRef::Reference {
                        reference: format!("#/components/messages/{}", message_id),
                    },
                )])),
                parameters: None,
            },
        );
        operations.insert(
            operation_name("receive", &port.channel, "packet"),
            receive_operation(&topic, &message_id),
        );
        messages.insert(
            message_id.clone(),
            Message {
                name: Some(message_id),
                title: None,
                summary: None,
                description: Some(format!("Packet payload for channel {}", port.channel)),
                content_type: Some("application/json".to_string()),
                payload: Some(object_schema(
                    properties,
                    required,
                    Some(format!("Packet payload for channel {}", port.channel)),
                )),
            },
        );
    }

    AsyncApiSpec {
        asyncapi: "3.0.0".to_string(),
        info: Info {
            title: "Zero Fiber Optics".to_string(),
            version: "0.1.0".to_string(),
            description: Some("Auto-generated AsyncAPI schema from port configuration".to_string()),
        },
        servers: None,
        channels: Some(channels),
        operations: Some(operations),
        components: Some(Components {
            messages: Some(messages),
            schemas: None,
        }),
    }
}

fn receive_operation(topic: &str, message_name: &str) -> Operation {
    Operation {
        action: OperationAction::Receive,
        channel: ChannelRef {
            reference: format!("#/channels/{}", topic),
        },
        messages: Some(vec![MessageRef::Reference {
            reference: format!("#/components/messages/{}", message_name),
        }]),
    }
}

fn scalar_schema(schema_type: &str, description: Option<String>) -> Schema {
    Schema::Object(Box::new(SchemaObject {
        schema_type: Some(serde_json::json!(schema_type)),
        properties: None,
        required: None,
        description,
        title: None,
        enum_values: None,
        const_value: None,
        items: None,
        additional_properties: None,
        one_of: None,
        any_of: None,
        all_of: None,
        additional: IndexMap::new(),
    }))
}

fn object_schema(
    properties: IndexMap<String, Box<Schema>>,
    required: Vec<String>,
    description: Option<String>,
) -> Schema {
    Schema::Object(Box::new(SchemaObject {
        schema_type: Some(serde_json::json!("object")),
        properties: Some(properties),
        required: Some(required),
        description,
        title: None,
        enum_values: None,
        const_value: None,
        items: None,
        additional_properties: None,
        one_of: None,
        any_of: None,
        all_of: None,
        additional: IndexMap::new(),
    }))
}

fn payload_description(units: Option<&str>) -> Option<String> {
    units.map(|value| format!("Units: {}", value))
}

fn message_name(channel: &str, variable: &str) -> String {
    let raw = format!("{}_{}", channel, variable);
    raw.chars()
        .map(|ch| if ch.is_ascii_alphanumeric() { ch } else { '_' })
        .collect()
}

fn operation_name(action: &str, channel: &str, variable: &str) -> String {
    message_name(&format!("{}_{}", action, channel), variable)
}

fn var_type_to_schema_type(var_type: &str) -> &'static str {
    match var_type {
        "CounterU32" | "SignedInt8" | "SignedInt16" | "SignedInt32" | "SignedInt64"
        | "UnSignedInt8" | "UnSignedInt16" | "UnSignedInt32" | "UnSignedInt64" => "integer",
        "Float" | "Double" => "number",
        "8BitBoolRegister" | "16BitBoolRegister" | "32BitBoolRegister" => "integer",
        _ => "string",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{Bit, Port, UdpChannels, Var};
    use serde_json::Value;

    fn make_var(name: &str, var_type: &str, units: Option<&str>, bits: Vec<Bit>) -> Var {
        Var {
            num: None,
            var_type: var_type.to_string(),
            units: units.map(str::to_string),
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
    fn build_schema_creates_packet_channel_with_object_payload() {
        let cfg = UdpChannels {
            ip: "127.0.0.1".to_string(),
            ports: vec![Port {
                numport: 50000,
                channel: "FiberA".to_string(),
                frequency: None,
                mode: None,
                variables: vec![
                    make_var("Power", "Float", Some("W"), vec![]),
                    make_var(
                        "Flags",
                        "8BitBoolRegister",
                        None,
                        vec![
                            Bit {
                                num: 0,
                                name: "Alarm".to_string(),
                            },
                            Bit {
                                num: 2,
                                name: "LinkUp".to_string(),
                            },
                        ],
                    ),
                ],
            }],
        };

        let mut topic_map = TopicMap::new();
        topic_map.insert("Power".to_string(), "power-watts".to_string());
        topic_map.insert("Alarm".to_string(), "alarm-active".to_string());

        let schema = build_schema(&cfg, "telemetry", &topic_map);
        let channels = schema.channels.expect("schema should contain channels");
        assert!(channels.contains_key("telemetry/FiberA"));
        assert_eq!(channels.len(), 1);

        let components = schema.components.expect("schema should contain components");
        let messages = components.messages.expect("schema should contain messages");
        let packet_msg = messages
            .get("FiberA_packet")
            .expect("packet message should exist");
        let payload = serde_json::to_value(packet_msg.payload.as_ref().expect("payload expected"))
            .expect("payload should serialize");

        assert_eq!(payload["type"], Value::String("object".to_string()));
        assert_eq!(
            payload["properties"]["power-watts"]["type"],
            Value::String("number".to_string())
        );
        assert_eq!(
            payload["properties"]["flags"]["type"],
            Value::String("integer".to_string())
        );
        assert_eq!(
            payload["properties"]["alarm-active"]["type"],
            Value::String("boolean".to_string())
        );
        assert_eq!(
            payload["properties"]["link-up"]["type"],
            Value::String("boolean".to_string())
        );
        assert_eq!(
            payload["properties"]["power-watts"]["description"],
            Value::String("Units: W".to_string())
        );

        let operations = schema.operations.expect("schema should contain operations");
        assert!(operations.contains_key("receive_FiberA_packet"));
    }

    #[test]
    fn var_type_to_schema_type_maps_expected_types() {
        assert_eq!(var_type_to_schema_type("SignedInt16"), "integer");
        assert_eq!(var_type_to_schema_type("UnSignedInt64"), "integer");
        assert_eq!(var_type_to_schema_type("Float"), "number");
        assert_eq!(var_type_to_schema_type("Double"), "number");
        assert_eq!(var_type_to_schema_type("8BitBoolRegister"), "integer");
        assert_eq!(var_type_to_schema_type("UnknownType"), "string");
    }
}
