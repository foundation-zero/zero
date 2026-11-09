//! Loading Specs from a directory of AsyncAPI 3.x documents.

use std::path::{Path, PathBuf};

use anyhow::Context;
use log::{info, warn};
use serde_json::Value;

use crate::api_model::{Api, Direction, Spec};
use crate::topic_map::TopicMap;
use channels::{operation_channels, topic_from_channel};
use roas::Document;
use schema::message_payload;
use validation::{ValidatorBuilder, payload_validator};

mod channels;
mod refs;
mod schema;
mod ttl;
mod validation;

/// The AsyncAPI version specific types this module reads.
mod roas {
    pub use roas_asyncapi::v3_0::channel::Channel;
    pub use roas_asyncapi::v3_0::message::Message;
    pub use roas_asyncapi::v3_0::schema::{Schema, SchemaOrMultiFormat, SchemaType, SubSchema};
    pub use roas_asyncapi::v3_0::{Document, Operation, OperationAction};
}

/// The paths of the AsyncAPI documents in `spec_dir`: every `.json` file,
/// sorted. A spec directory holds only AsyncAPI documents, so a `.json`
/// file that is not one fails when it is read — see
/// [`read_asyncapi_document`].
fn spec_documents(spec_dir: &str) -> anyhow::Result<Vec<PathBuf>> {
    let dir = Path::new(spec_dir);
    if !dir.is_dir() {
        anyhow::bail!("spec_dir does not exist or is not a directory: {spec_dir}");
    }

    let mut files = std::fs::read_dir(dir)?
        .map(|entry| {
            let path = entry?.path();
            Ok(path)
        })
        .collect::<anyhow::Result<Vec<_>>>()?;
    files.sort();

    Ok(files
        .into_iter()
        .filter(|path| path.extension().and_then(|e| e.to_str()) == Some("json"))
        .collect())
}

/// Read and parse one file into an AsyncAPI 3.x `Document`.
///
/// Errors when the file is unreadable, not valid JSON, lacks an `asyncapi`
/// version, or is not an AsyncAPI 3.x document — a spec directory is
/// expected to contain only loadable specs.
fn read_asyncapi_document(path: &Path) -> anyhow::Result<Value> {
    let content =
        std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;

    let spec_value: Value = serde_json::from_str(&content)
        .with_context(|| format!("parsing JSON of {}", path.display()))?;

    let asyncapi_version = spec_value
        .get("asyncapi")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if asyncapi_version.is_empty() {
        anyhow::bail!("{} has no 'asyncapi' field", path.display());
    }
    if !asyncapi_version.starts_with("3.") {
        anyhow::bail!(
            "{} has asyncapi version '{}' (only 3.x is supported)",
            path.display(),
            asyncapi_version
        );
    }

    Ok(spec_value)
}

fn load_spec(path: &Path, document_json: &Value) -> anyhow::Result<Spec> {
    let validator_builder = ValidatorBuilder::new(document_json.clone())?;

    let document = serde_json::from_value::<Document>(document_json.clone())
        .with_context(|| format!("parsing AsyncAPI document {}", path.display()))?;

    let mut topics = Vec::new();
    let mut subscribe_topics = TopicMap::new();
    let mut validators = Vec::new();
    for (operation, channel_ref, channel) in operation_channels(&document, path)? {
        let Some(address) = channel.address() else {
            warn!(
                "Channel '{}' in {} has no address, skipping",
                operation.channel.reference,
                path.display()
            );
            continue;
        };
        let message_payload = message_payload(&channel_ref, channel, &document);
        let validator = message_payload
            .as_ref()
            .and_then(|m| payload_validator(&validator_builder, address, &m.schema_ref));
        let topic = topic_from_channel(
            operation,
            &channel_ref,
            channel,
            address,
            message_payload,
            &document,
            path,
        )?;

        if let Some(validator) = validator {
            validators.push((topic.topic.clone(), validator));
        }
        // Subscribe only to Send topics, and only to the broadest filter
        // covering each.
        if topic.operation == Direction::Send && !subscribe_topics.covers_topic(&topic.topic) {
            subscribe_topics.insert_with_replace(topic.topic.clone(), ());
        }
        topics.push(topic);
    }

    info!(
        "Parsed: {} topic(s) from '{}'.",
        topics.len(),
        path.display()
    );

    Spec::new(
        path.file_prefix()
            .ok_or(anyhow::anyhow!("File prefix is not valid as name"))?
            .to_string_lossy()
            .into_owned(),
        subscribe_topics,
        topics,
        validators.into_iter().collect(),
    )
    .with_context(|| format!("building the Query tree of {}", path.display()))
}

/// Load AsyncAPI 3.0.0 spec files from a directory in a single pass over the
/// spec directory, extracting both concrete topics and parametrized groups.
///
/// Consumers that only need one of the two should still use this loader and
/// ignore the other half, so each spec file is read exactly once.
pub fn load_specs(spec_dir: &str, ignore_failures: bool) -> anyhow::Result<Api> {
    let specs = spec_documents(spec_dir)?;

    let api_models = specs
        .iter()
        .filter_map(|path| {
            let spec = read_asyncapi_document(path)
                .and_then(|document_json| load_spec(path, &document_json));

            if ignore_failures && let Err(error) = spec {
                warn!("Skipping AsyncAPI spec '{}': {:#}", path.display(), error);
                None
            } else {
                Some(spec)
            }
        })
        .collect::<anyhow::Result<Vec<_>>>()?;

    info!("Loaded {} api's from {spec_dir} ", api_models.len());

    Ok(Api::new(api_models))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test_log::test]
    fn test_load_specs_skips_non_json_files() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-nonjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("readme.txt"), "not a spec").unwrap();

        let topics = load_specs(dir.to_str().unwrap(), false).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(topics.is_empty());
    }

    #[test_log::test]
    fn test_load_specs_rejects_invalid_json() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-invalidjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("broken.json"), "{ not json }").unwrap();

        let err = load_specs(dir.to_str().unwrap(), false).unwrap_err();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(err.to_string().contains("parsing JSON"), "{err}");
    }

    #[test_log::test]
    fn test_load_specs_rejects_missing_asyncapi_field() {
        let spec = json!({
            "info": { "title": "no version" },
            "channels": {}
        });

        let dir = std::env::temp_dir().join("mqtt-graphql-test-no-asyncapi");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let err = load_specs(dir.to_str().unwrap(), false).unwrap_err();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(err.to_string().contains("no 'asyncapi' field"), "{err}");
    }

    #[test_log::test]
    fn test_load_specs_rejects_non_v3_spec() {
        let spec = json!({
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "test.channel:Publisher": {
                    "address": "test/channel"
                }
            }
        });

        let dir = std::env::temp_dir().join("mqtt-graphql-test-v2");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let err = load_specs(dir.to_str().unwrap(), false).unwrap_err();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(err.to_string().contains("only 3.x is supported"), "{err}");
    }

    #[test_log::test]
    fn test_load_specs_subscribe_topics() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "receive_channel": {
                    "address": "one/channel",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/Message"
                        }
                    },
                },
                "send_channel": {
                    "address": "two/channel",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/Message"
                        }
                    },
                },
                "send_channel_broader": {
                    "address": "two/#",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/Message"
                        }
                    },
                }
            },
            "operations": {
                "receive_channel": {
                    "action": "receive",
                    "channel": {
                        "$ref": "#/channels/receive_channel"
                    }
                },
                "send_channel": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/send_channel"
                    }
                },
                "send_channel_broader": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/send_channel_broader"
                    }
                },
            },
            "components": {
                "messages": {
                    "Message": {
                        "payload": {
                            "type": "object",
                            "properties": { "a": { "type": "number" } }
                        }
                    }
                }
            }
        });

        let api = Api::new(vec![load_spec(Path::new("test"), &spec).unwrap()]);
        let subscribed_topics = api.subscribe_topics();

        // We expect one topic that is not receive and the broadest
        assert_eq!(subscribed_topics.len(), 1);
        assert!(subscribed_topics.contains(&"two/#".to_string()));
    }

    #[test_log::test]
    fn test_inline_payload_at_the_end_of_a_message_ref_chain_is_validated() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "chained": {
                    "address": "chained/channel",
                    "messages": {"Message": {"$ref": "#/components/messages/Alias"}}
                }
            },
            "operations": {
                "chained": {"action": "send", "channel": {"$ref": "#/channels/chained"}}
            },
            "components": {
                "messages": {
                    "Alias": {"$ref": "#/components/messages/Real"},
                    "Real": {
                        "payload": {
                            "type": "object",
                            "properties": {"x": {"type": "integer"}}
                        }
                    }
                }
            }
        });

        let api = Api::new(vec![load_spec(Path::new("test"), &spec).unwrap()]);

        let validators = api.validators();
        let topics: Vec<&String> = validators.keys().collect();
        assert_eq!(topics, ["chained/channel"]);
    }

    #[test_log::test]
    fn test_validators_are_keyed_by_topic_and_skip_channels_without_payload() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "power": {
                    "address": "power/{panel}",
                    "messages": {"Message": {"payload": {"type": "object"}}},
                    "x-group-topic-metadata": {},
                    "x-group-by": "panel"
                },
                "bare": {"address": "bare/channel"}
            },
            "operations": {
                "power": {"action": "send", "channel": {"$ref": "#/channels/power"}},
                "bare": {"action": "send", "channel": {"$ref": "#/channels/bare"}}
            }
        });

        let api = Api::new(vec![load_spec(Path::new("test"), &spec).unwrap()]);

        let validators = api.validators();
        let topics: Vec<&String> = validators.keys().collect();
        assert_eq!(topics, ["power/+"]);
    }

    #[test_log::test]
    fn test_inline_message_of_a_referenced_channel_is_validated() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "referenced": {"$ref": "#/components/channels/referenced"}
            },
            "operations": {
                "referenced": {"action": "send", "channel": {"$ref": "#/channels/referenced"}}
            },
            "components": {
                "channels": {
                    "referenced": {
                        "address": "ref/channel",
                        "messages": {
                            "Message": {
                                "payload": {
                                    "type": "object",
                                    "properties": {"x": {"type": "integer"}}
                                }
                            }
                        }
                    }
                }
            }
        });

        let api = Api::new(vec![load_spec(Path::new("test"), &spec).unwrap()]);

        let validators = api.validators();
        let topics: Vec<&String> = validators.keys().collect();
        assert_eq!(topics, ["ref/channel"]);
    }
}
