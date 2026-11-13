//! Topics from a document's operations and channels.

use std::collections::BTreeMap;
use std::path::Path;

use anyhow::{Context, anyhow};
use jsonschema::Validator;
use log::{debug, info, warn};
use roas_asyncapi::common::Resolution;

use super::roas::{Channel, Document, Operation, OperationAction};
use super::schema::{MessagePayload, message_payload};
use super::ttl::ttl_for_channel;
use super::unresolved_reason;
use super::validation::{ValidatorBuilder, payload_validator};
use crate::api_model::{Direction, GroupDef, MetadataByTopic, TopicDef, TopicKind};
use crate::topic_map::TopicMap;

/// The topics a document's operations define, and the validators of their
/// payloads. Skips, with a warning, channels without an address.
pub(super) fn document_topics(
    doc: &Document,
    validator_builder: &ValidatorBuilder,
    path: &Path,
) -> anyhow::Result<(Vec<TopicDef>, TopicMap<Validator>)> {
    let mut topics = Vec::new();
    let mut validators = Vec::new();
    for (operation, channel_ref, channel) in operation_channels(doc, path)? {
        let Some(address) = channel.address() else {
            warn!(
                "Channel '{}' in {} has no address, skipping",
                operation.channel.reference,
                path.display()
            );
            continue;
        };
        let message_payload = message_payload(&channel_ref, channel, doc);
        if let Some(validator) = message_payload
            .as_ref()
            .and_then(|m| payload_validator(validator_builder, address, &m.schema_ref))
        {
            validators.push((wildcard_from_address(address), validator));
        }
        topics.push(topic_from_channel(
            operation,
            &channel_ref,
            channel,
            address,
            message_payload,
            doc,
            path,
        )?);
    }
    Ok((topics, validators.into_iter().collect()))
}

/// The document's operations, each with the channel it points at and that
/// channel's own reference: where a `$ref` chain ends, so pointers into its
/// inline messages exist. Errors on unresolvable operation and channel
/// references.
fn operation_channels<'a>(
    doc: &'a Document,
    path: &Path,
) -> anyhow::Result<Vec<(&'a Operation, String, &'a Channel)>> {
    if doc.operations.is_empty() {
        info!("File {} has no operations, skipping", path.display());
    }

    doc.operations
        .iter()
        .map(|(operation_name, operation_ref)| {
            debug!("Parsing operation {operation_name} from {}", path.display());
            let operation = found(operation_ref.get_item(doc)).with_context(|| {
                format!(
                    "unresolvable operation $ref '{}' ({}) in {}",
                    operation_name,
                    operation_ref
                        .reference()
                        .map_or("<inline operation>", |r| r.reference.as_str()),
                    path.display()
                )
            })?;
            let channel = found(doc.resolve_channel(&operation.channel)).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' in {}",
                    operation.channel.reference,
                    path.display()
                )
            })?;
            let channel_ref = doc.resolved_channel_ref(&operation.channel).to_owned();
            Ok((operation, channel_ref, channel))
        })
        .collect()
}

/// The object a reference resolved to, or an error saying why there is
/// none.
fn found<T>(resolution: Resolution<'_, T>) -> anyhow::Result<&T> {
    let reason = unresolved_reason(&resolution);
    resolution
        .found()
        .ok_or_else(|| anyhow!("the reference {reason}"))
}

/// Convert the channel an operation points at, with its own reference (see
/// [`operation_channels`]), address and message payload, into a
/// [`TopicDef`]: a Group when its address is parametrized, a single topic
/// otherwise.
fn topic_from_channel(
    operation: &Operation,
    channel_ref: &str,
    channel: &Channel,
    address: &str,
    message_payload: Option<MessagePayload>,
    doc: &Document,
    path: &Path,
) -> anyhow::Result<TopicDef> {
    let name = &operation.channel.reference;
    if channel.messages.is_empty() {
        info!("Channel '{name}' (address: '{address}') has no messages");
    }
    debug!("Parsed channel {name} with payload {message_payload:?}");

    let kind = if is_parametrized_channel(Some(address)) {
        let field_attributes = message_payload
            .as_ref()
            .map(|m| m.field_attributes.clone())
            .unwrap_or_default();
        let group = group_from_channel(name, channel, field_attributes, path)?;
        info!("Loaded topic group '{address}' from {}", path.display());
        TopicKind::Group(group)
    } else {
        TopicKind::Single
    };

    Ok(TopicDef {
        topic: wildcard_from_address(address),
        operation: match operation.action {
            OperationAction::Send => Direction::Send,
            OperationAction::Receive => Direction::Receive,
        },
        payload: message_payload.map(|m| m.payload),
        ttl_secs: ttl_for_channel(channel_ref, channel, doc),
        kind,
        // Paired with its Receive topic when the Spec is built.
        setter: None,
    })
}

/// The Group part of a parametrized channel, read from its
/// `x-group-topic-metadata` and `x-group-by` extensions.
fn group_from_channel(
    channel_name: &str,
    channel: &Channel,
    field_attributes: BTreeMap<String, BTreeMap<String, String>>,
    path: &Path,
) -> anyhow::Result<GroupDef> {
    let topic_metadata = serde_json::from_value::<MetadataByTopic>(
        channel
            .extensions
            .clone()
            .unwrap_or_default()
            .get("x-group-topic-metadata")
            .with_context(|| {
                format!(
                    "Missing x-group-topic-metadata extension for {channel_name} in {}",
                    path.display()
                )
            })?
            .clone(),
    )?;

    let group_by = serde_json::from_value::<String>(
        channel
            .extensions
            .clone()
            .with_context(|| format!("No extensions found on {channel_name}"))?
            .get("x-group-by")
            .with_context(|| {
                format!(
                    "Missing x-group-by extension for {channel_name} in {}",
                    path.display()
                )
            })?
            .clone(),
    )?;

    Ok(GroupDef {
        field_attributes,
        topic_metadata,
        group_by,
    })
}

/// Whether a channel describes a parametrized topic family rather than one
/// concrete topic: a `{placeholder}` segment in the address
fn is_parametrized_channel(address: Option<&str>) -> bool {
    address.is_some_and(|address| {
        address
            .split('/')
            .any(|segment| param_name(segment).is_some())
    })
}

/// Parameter name when an address segment is a `{placeholder}`, else
/// `None`: `{panel}` → `panel`.
fn param_name(segment: &str) -> Option<&str> {
    segment.strip_prefix('{')?.strip_suffix('}')
}

/// MQTT subscription pattern derived from the address.
fn wildcard_from_address(address: &str) -> String {
    address
        .split('/')
        .map(|segment| {
            if param_name(segment).is_some() {
                "+"
            } else {
                segment
            }
        })
        .collect::<Vec<_>>()
        .join("/")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::FieldType;
    use serde_json::{Value, json};

    /// The topics `load_spec` reads from a document, before they go into a
    /// Spec's Query tree.
    fn loaded_topics(spec: &Value) -> anyhow::Result<Vec<TopicDef>> {
        let document = serde_json::from_value::<Document>(spec.clone())?;
        let validator_builder = ValidatorBuilder::new(spec.clone())?;
        let (topics, _) = document_topics(&document, &validator_builder, Path::new("test"))?;
        Ok(topics)
    }

    /// The payload fields of a topic that must have a payload.
    fn fields(topic: &TopicDef) -> &BTreeMap<String, FieldType> {
        &topic.payload.as_ref().unwrap().fields
    }

    #[test_log::test]
    fn test_load_specs_from_json() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "termodinamica.compressor.temperature:Publisher": {
                    "address": "termodinamica/compressor/temperature:Publisher",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/termodinamica.compressor.temperature:Publisher:Message"
                        }
                    }
                }
            },
            "operations": {
                "termodinamica.compressor.temperature:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/termodinamica.compressor.temperature:Publisher"
                    }
                },
            },
            "components": {
                "messages": {
                    "termodinamica.compressor.temperature:Publisher:Message": {
                        "payload": { "$ref": "#/components/schemas/Temperature" }
                    }
                },
                "schemas": {
                    "Temperature": {
                        "type": "object",
                        "properties": {
                            "celsius": { "type": "number" },
                            "sensor_id": { "type": "integer" },
                            "ok": { "type": "boolean" }
                        },
                        "required": ["celsius", "sensor_id", "ok"]
                    }
                }
            }
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 1);
        assert_eq!(
            topics[0].topic,
            "termodinamica/compressor/temperature:Publisher"
        );
        assert_eq!(fields(&topics[0]).len(), 3);
        assert_eq!(fields(&topics[0]).get("celsius"), Some(&FieldType::Float));
    }

    #[test_log::test]
    fn test_load_specs_from_json_groups() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "power-tags": {
                    "address": "power-tags/{panel}/{slug}",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/power-tags:Message"
                        }
                    },
                    "x-group-topic-metadata": {},
                    "x-group-by": "panel"
                }
            },
            "operations": {
                "power-tags": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/power-tags"
                    }
                },
            },
            "components": {
                "messages": {
                    "power-tags:Message": {
                        "payload": { "$ref": "#/components/schemas/Temperature" }
                    }
                },
                "schemas": {
                    "Temperature": {
                        "type": "object",
                        "properties": {
                            "celsius": { "type": "number" },
                            "sensor_id": { "type": "integer" },
                            "ok": { "type": "boolean" }
                        },
                        "required": ["celsius", "sensor_id", "ok"]
                    }
                }
            }
        });

        let groups: Vec<_> = loaded_topics(&spec)
            .unwrap()
            .into_iter()
            .filter(|t| t.as_group().is_some())
            .collect();

        assert_eq!(groups.len(), 1);
        assert_eq!(groups[0].topic, "power-tags/+/+");
        assert_eq!(fields(&groups[0]).len(), 3);
        assert_eq!(fields(&groups[0]).get("celsius"), Some(&FieldType::Float));
    }

    #[test_log::test]
    fn test_inline_payload_without_ref() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "test.channel:Publisher": {
                    "address": "test/channel:Publisher",
                    "messages": {
                        "Message": {
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "value": { "type": "number" }
                                }
                            }
                        }
                    },
                }
            },
            "operations": {
                "test.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/test.channel:Publisher"
                    }
                },
            }
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "test/channel:Publisher");
        assert_eq!(fields(&topics[0]).len(), 1);
        assert_eq!(fields(&topics[0]).get("value"), Some(&FieldType::Float));
    }

    #[test_log::test]
    fn test_load_specs_multiple_channels() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "one.channel:Publisher": {
                    "address": "one/channel",
                    "messages": {
                        "Message": {
                            "payload": {
                                "type": "object",
                                "properties": { "a": { "type": "number" } }
                            }
                        }
                    },
                },
                "two.channel:Publisher": {
                    "address": "two/channel",
                    "messages": {
                        "Message": {
                            "payload": {
                                "type": "object",
                                "properties": { "b": { "type": "boolean" } }
                            }
                        }
                    },
                }
            },
            "operations": {
                "one.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/one.channel:Publisher"
                    }
                },
                "two.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/two.channel:Publisher"
                    }
                },
            }
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 2);
        // BTreeMap ordering
        assert!(topics.iter().any(|t| t.topic == "one/channel"));
        assert!(topics.iter().any(|t| t.topic == "two/channel"));
    }

    #[test_log::test]
    fn test_channel_ref_is_resolved() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "referenced.channel:Publisher": {
                    "$ref": "#/components/channels/referenced.channel:Publisher"
                }
            },
            "operations": {
                "referenced.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/referenced.channel:Publisher"
                    }
                },
            },
            "components": {
                "channels": {
                    "referenced.channel:Publisher": {
                        "address": "ref/channel",
                        "messages": {
                            "Message": {
                                "payload": {
                                    "type": "object",
                                    "properties": { "x": { "type": "integer" } }
                                }
                            }
                        },
                    }
                }
            }
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "ref/channel");
        assert_eq!(fields(&topics[0]).get("x"), Some(&FieldType::Int));
    }

    #[test_log::test]
    fn test_no_resolvable_payload_yields_empty_fields() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "bare.channel:Publisher": {
                    "address": "bare/channel",
                    "messages": {
                        "Message": { "summary": "no payload" }
                    },
                }
            },
            "operations": {
                "bare.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/bare.channel:Publisher"
                    }
                },
            },
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "bare/channel");
        assert!(topics[0].payload.is_none());
    }

    #[test_log::test]
    fn test_no_resolvable_channel() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "operations": {
                "bare.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/does-not-exist"
                    }
                },
            },
        });

        let err = loaded_topics(&spec).unwrap_err();

        assert_eq!(
            err.to_string(),
            "unresolvable channel $ref '#/channels/does-not-exist' in test",
            "{err}"
        );
    }

    #[test_log::test]
    fn test_no_resolvable_operation() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "operations": {
                "bare.channel:Publisher": {
                     "$ref": "#/operations/does-not-exist"
                },
            },
        });

        let err = loaded_topics(&spec).unwrap_err();

        assert_eq!(
            err.to_string(),
            "unresolvable operation $ref 'bare.channel:Publisher' (#/operations/does-not-exist) in test",
            "{err}"
        );
    }

    #[test_log::test]
    fn test_no_resolvable_message_yields_empty_fields() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "channel": {
                    "address": "bare/channel",
                    "messages": {
                        "Message": { "$ref": "#/channels/does-not-exist" }
                    },
                }
            },
            "operations": {
                "bare.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/channel"
                    }
                },
            },
        });

        let topics = loaded_topics(&spec).unwrap();

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "bare/channel");
        assert!(topics[0].payload.is_none());
    }
}
