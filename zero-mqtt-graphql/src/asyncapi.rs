use std::collections::BTreeMap;
use std::fmt::Debug;
use std::path::{Path, PathBuf};

use crate::metadata::MetadataByTopic;
use crate::roas_asyncapi::{
    Channel, Document, Message, Operation, OperationAction, Schema, SchemaOrMultiFormat,
};
use anyhow::Context;
use log::{debug, info, warn};
use roas_asyncapi::common::reference::{RefOr, Reference};
use serde_json::Value;

use crate::api_model::{Api, ApiModel, FieldDef, TopicDef, TopicGroupDef};
use crate::graphql::graphql_type_for_subschema;
use crate::message_validation::{ValidatorBuilder, build_validators};
use crate::naming::sanitize_to_graphql_name;
use crate::topic_map::TopicMap;

/// Read and parse every AsyncAPI document in `spec_dir` once, returning
/// `(file name, path, document)` for each. Non-JSON files and topic-metadata
/// files are skipped; unreadable or invalid `.json` files are an error —
/// see [`read_asyncapi_document`].
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
        .filter(|path| !crate::metadata::is_metadata_file(path))
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

fn load_spec(path: &Path) -> anyhow::Result<ApiModel> {
    let document_json = read_asyncapi_document(path)?;

    let validator_builder = ValidatorBuilder::new(document_json.clone())?;

    let document = serde_json::from_value::<Document>(document_json.clone())
        .with_context(|| format!("parsing AsyncAPI document {}", path.display()))?;

    let topics: Vec<TopicDef> = channels_from_document(&document, path, topic_from_channel)?;
    let groups: Vec<TopicGroupDef> = channels_from_document(&document, path, group_from_channel)?;
    let subscribe_topics = channels_from_document(&document, path, channel_addresses_from_channel)?
        .into_iter()
        .fold(TopicMap::new(), |mut acc, topic| {
            if !acc.covers_topic(&topic) {
                acc.insert_with_replace(topic, ());
            }
            acc
        });

    let validators = build_validators(&validator_builder, &topics, &groups)?;

    info!(
        "Parsed: {} topic(s), {} group(s) from '{}'.",
        topics.len(),
        groups.len(),
        path.display()
    );

    Ok(ApiModel::new(
        path.file_prefix()
            .ok_or(anyhow::anyhow!("File prefix is not valid as name"))?
            .to_string_lossy()
            .into_owned(),
        subscribe_topics,
        topics,
        groups,
        validators,
    ))
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
            let spec = load_spec(path);
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

/// Extract channels and create relevant datastructure from one document, erroring on unresolvable
/// channel and operation references.
fn channels_from_document<
    T,
    U: Fn(&Reference, &str, OperationAction, &Channel, &Document, &Path) -> anyhow::Result<Option<T>>,
>(
    doc: &Document,
    path: &Path,
    resolve_func: U,
) -> anyhow::Result<Vec<T>> {
    if doc.operations.is_empty() {
        info!("File {} has no operations, skipping", path.display());
        return Ok(Vec::new());
    }

    let operations: Vec<_> = doc
        .operations
        .iter()
        .map(|(operation_name, operation_ref)| {
            debug!("Parsing operation {operation_name} from {}", path.display());

            let operation = resolve_operation(operation_ref, doc).with_context(|| {
                format!(
                    "unresolvable operation $ref '{}' in {}",
                    operation_name,
                    path.display()
                )
            })?;

            Ok::<(OperationAction, String, RefOr<Channel>), anyhow::Error>((
                operation.action,
                operation
                    .channel
                    .local_key()
                    .with_context(|| "Can't find operation key")?,
                RefOr::Reference(operation.channel.clone()),
            ))
        })
        .collect::<anyhow::Result<Vec<(_, _, _)>>>()?;
    operations
        .into_iter()
        .map(|(action, channel_name, channel_ref)| {
            debug!("Parsing channel {channel_name} from {}", path.display());
            let channel = resolve_channel(&channel_ref, doc).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' ({}) in {}",
                    channel_name,
                    channel_ref
                        .reference()
                        .map_or("<inline channel>", |r| r.reference.as_str()),
                    path.display()
                )
            })?;
            resolve_func(
                channel_ref
                    .reference()
                    .with_context(|| "Channel is wrongly embedded in the operation")?,
                &channel_name,
                action,
                channel,
                doc,
                path,
            )
        })
        .collect::<anyhow::Result<Vec<_>>>()
        .map(|items| items.into_iter().flatten().collect())
}

#[allow(clippy::unnecessary_wraps)]
fn channel_addresses_from_channel(
    _channel_ref: &Reference,
    _channel_name: &str,
    action: OperationAction,
    channel: &Channel,
    _doc: &Document,
    _path: &Path,
) -> anyhow::Result<Option<String>> {
    if let OperationAction::Receive = action {
        return Ok(None);
    }

    let Some(Some(address)) = &channel.address else {
        return Ok(None);
    };

    Ok(Some(wildcard_from_address(address)))
}

/// Convert one concrete (non-parametrized) channel into a [`TopicDef`];
/// returns `None` for parametrized channels or channels without a topic.
#[allow(clippy::unnecessary_wraps)]
fn topic_from_channel(
    channel_ref: &Reference,
    channel_name: &str,
    action: OperationAction,
    channel: &Channel,
    doc: &Document,
    path: &Path,
) -> anyhow::Result<Option<TopicDef>> {
    // Parametrized channels are handled by groups_from_document.
    if is_parametrized_channel(channel.address()) {
        return Ok(None);
    }

    let mqtt_topic = channel.address().map(ToString::to_string);
    let Some(mqtt_topic) = mqtt_topic else {
        warn!(
            "Channel '{}' in {} has no mqtt binding topic and no address, skipping",
            channel_name,
            path.display()
        );
        return Ok(None);
    };

    if channel.messages.is_empty() {
        info!("Channel '{channel_name}' (topic: '{mqtt_topic}') has no messages");
    }

    let (fields, payload_schema_ref, _) = message_fields(channel_ref, channel, doc);
    debug!(
        "Parsed channel {} with {} fields",
        channel_name,
        fields.len()
    );

    Ok(Some(TopicDef {
        topic: mqtt_topic,
        action,
        fields,
        payload_schema_ref,
        ttl_secs: ttl_for_channel(channel_ref, channel, doc),
    }))
}

/// Convert one parametrized channel into a [`TopicGroupDef`]; returns
/// `None` for concrete channels. A parametrized channel without an address
/// is an error: neither the group name nor the wildcard pattern can be
/// derived without it.
fn group_from_channel(
    channel_ref: &Reference,
    channel_name: &str,
    action: OperationAction,
    channel: &Channel,
    doc: &Document,
    path: &Path,
) -> anyhow::Result<Option<TopicGroupDef>> {
    if !is_parametrized_channel(channel.address()) {
        return Ok(None);
    }
    let Some(address) = channel.address().map(str::to_string) else {
        anyhow::bail!(
            "parametrized channel '{}' in {} has no address",
            channel_name,
            path.display()
        );
    };
    let group = static_prefix(&address).unwrap_or_else(|| address.clone());
    let pattern = wildcard_from_address(&address);

    let (fields, payload_schema_ref, payload_schema) = message_fields(channel_ref, channel, doc);
    let value_extensions = payload_schema
        .as_ref()
        .map(extensions_from_payload_schema)
        .unwrap_or_default();

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

    info!(
        "Loaded topic group '{}' ({}) from {}",
        group,
        pattern,
        path.display()
    );
    Ok(Some(TopicGroupDef {
        group,
        pattern,
        fields,
        payload_schema_ref,
        value_extensions,
        ttl_secs: ttl_for_channel(channel_ref, channel, doc),
        action,
        topic_metadata,
        group_by,
    }))
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

/// Static leading segments of the address: `power-tags/{panel}/{slug}` →
/// `power-tags`.
fn static_prefix(address: &str) -> Option<String> {
    let prefix = address
        .split('/')
        .take_while(|segment| param_name(segment).is_none())
        .collect::<Vec<_>>()
        .join("/");
    (!prefix.is_empty()).then_some(prefix)
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

/// Extract scalar fields + payload schema from the channel's first message.
///
/// Channels with multiple messages are not yet union-typed; only the first
/// message contributes fields and schema.
fn message_fields(
    channel_ref: &Reference,
    channel: &Channel,
    doc: &Document,
) -> (Vec<FieldDef>, Option<String>, Option<Value>) {
    let Some((message_ref, message)) = channel_messages(channel_ref, channel, doc)
        .into_iter()
        .next()
    else {
        info!("Channel {} has no message", channel_ref.reference);
        return (Vec::new(), None, None);
    };
    // The message payload may be inline or a `$ref` into components
    let Some(payload_ref) = &message.payload else {
        info!("Channel {} message has no payload", channel_ref.reference);
        return (Vec::new(), None, None);
    };

    let (schema_or_multi, payload_schema_ref, payload_schema) = match payload_ref {
        RefOr::Reference(payload_reference) => {
            if let Some(schema_or_multi) = resolve_payload_schema(payload_ref, doc) {
                (
                    schema_or_multi,
                    Some(payload_reference.reference.clone()),
                    serde_json::to_value(schema_or_multi).ok(),
                )
            } else {
                info!(
                    "Channel {} message payload reference {} does not resolve",
                    channel_ref.reference, payload_reference.reference
                );
                return (Vec::new(), None, None);
            }
        }
        RefOr::Item(schema_or_multi) => {
            let schema_ref = format!("{message_ref}/payload");
            let schema_value = serde_json::to_value(schema_or_multi).ok();
            (schema_or_multi, Some(schema_ref), schema_value)
        }
    };

    let fields = extract_fields_from_schema_or_multi(schema_or_multi, doc);

    (fields, payload_schema_ref, payload_schema)
}

/// All messages referenced by the channel, resolved against components.
fn channel_messages<'a>(
    channel_ref: &Reference,
    channel: &'a Channel,
    doc: &'a Document,
) -> BTreeMap<String, &'a Message> {
    channel
        .messages
        .iter()
        .filter_map(|(message_key, message_ref)| {
            let message_reference = match message_ref {
                RefOr::Reference(reference) => reference.reference.clone(),
                RefOr::Item(_) => format!(
                    "{}/messages/{}",
                    channel_ref.reference,
                    message_key.replace('~', "~0").replace('/', "~1")
                ),
            };
            resolve_message(message_ref, doc).map(|message| (message_reference, message))
        })
        .collect()
}

/// Extension attributes per payload field, read from `x-*` schema
/// extensions: `properties.<name>.x-<key>` → `<key>`. Non-scalar extension
/// values are ignored.
fn extensions_from_payload_schema(
    payload_schema: &Value,
) -> BTreeMap<String, BTreeMap<String, String>> {
    let Some(properties) = payload_schema.get("properties").and_then(Value::as_object) else {
        return BTreeMap::new();
    };
    properties
        .iter()
        .filter_map(|(name, property)| {
            let extensions: BTreeMap<String, String> = property
                .as_object()?
                .iter()
                .filter_map(|(key, value)| {
                    let attribute = key.strip_prefix("x-")?;
                    let rendered = match value {
                        Value::String(string) => string.clone(),
                        Value::Number(number) => number.to_string(),
                        Value::Bool(boolean) => boolean.to_string(),
                        _ => return None,
                    };
                    Some((attribute.to_string(), rendered))
                })
                .collect();
            (!extensions.is_empty()).then_some((name.clone(), extensions))
        })
        .collect()
}

/// Follow a component `$ref` to a real entry
fn resolve_ref_to_entry<'a, T: Debug>(
    reference: &'a Reference,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
    mut traversed_keys: Vec<&'a str>,
) -> Option<&'a T> {
    let pointer = reference.local_pointer()?;
    let key = reference.local_key()?;

    let entries = if reference.reference.starts_with("#/components/") {
        entries_components
    } else {
        entries_main
    };

    let entries = entries?;

    if (traversed_keys).contains(&pointer) {
        info!("Found circular refs, aborting on: {key}");
        return None;
    }

    match entries.get(&key)? {
        RefOr::Reference(nested) => {
            traversed_keys.push(pointer);
            resolve_ref_to_entry(nested, entries_main, entries_components, traversed_keys)
        }
        RefOr::Item(entry) => Some(entry),
    }
}

fn resolve_refor<'a, T: Debug>(
    reference: &'a RefOr<T>,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
) -> Option<&'a T> {
    match reference {
        RefOr::Item(m) => Some(m),
        RefOr::Reference(reference) => {
            resolve_ref_to_entry(reference, entries_main, entries_components, vec![])
        }
    }
}

fn resolve_channel<'a>(r: &'a RefOr<Channel>, doc: &'a Document) -> Option<&'a Channel> {
    resolve_refor(
        r,
        Some(&doc.channels),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.channels),
    )
}

fn resolve_operation<'a>(r: &'a RefOr<Operation>, doc: &'a Document) -> Option<&'a Operation> {
    resolve_refor(
        r,
        Some(&doc.operations),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.operations),
    )
}

fn resolve_message<'a>(r: &'a RefOr<Message>, doc: &'a Document) -> Option<&'a Message> {
    resolve_refor(
        r,
        None,
        doc.components
            .as_ref()
            .map(|componentens| &componentens.messages),
    )
}

fn resolve_payload_schema<'a>(
    r: &'a RefOr<SchemaOrMultiFormat>,
    doc: &'a Document,
) -> Option<&'a SchemaOrMultiFormat> {
    resolve_refor(
        r,
        None,
        doc.components
            .as_ref()
            .map(|componentens| &componentens.schemas),
    )
}

fn extract_fields_from_schema_or_multi(
    schema_or_multi: &SchemaOrMultiFormat,
    doc: &Document,
) -> Vec<FieldDef> {
    match schema_or_multi {
        SchemaOrMultiFormat::Schema(schema) => extract_fields_from_schema(schema, doc),
        SchemaOrMultiFormat::MultiFormat(mf) => {
            // Try to deserialize the raw schema value as a Schema
            if let Ok(schema) = serde_json::from_value::<Schema>(mf.schema.clone()) {
                extract_fields_from_schema(&schema, doc)
            } else {
                info!("Payload schema has no fields");
                Vec::new()
            }
        }
        SchemaOrMultiFormat::Bool(_) => {
            info!("Payload schema has no fields");
            Vec::new()
        }
    }
}

fn extract_fields_from_schema(schema: &Schema, doc: &Document) -> Vec<FieldDef> {
    // Fields colliding after lowerCamel sanitization are not tolerated here:
    // they surface as errors from `validate_topics` instead.
    schema
        .properties
        .iter()
        .filter_map(|(name, subschema)| {
            let graphql_type = graphql_type_for_subschema(subschema, doc)?;
            let sanitized = sanitize_to_graphql_name(name);
            if sanitized.is_empty() {
                warn!("Skipping field '{name}' sanitizes to empty GraphQL name");
                return None;
            }
            Some(FieldDef {
                name: name.clone(),
                graphql_type,
            })
        })
        .collect()
}

/// Effective TTL for cached values of a channel: the maximum `x-ttl`
/// across its messages (a channel may declare several), falling back to the
/// channel's own extension, then the global default.
fn ttl_for_channel(channel_ref: &Reference, channel: &Channel, doc: &Document) -> u64 {
    channel_messages(channel_ref, channel, doc)
        .into_values()
        .filter_map(|message| ttl_from_extensions(message.extensions.as_ref()))
        .max()
        .or_else(|| ttl_from_extensions(channel.extensions.as_ref()))
        .unwrap_or(crate::config::DEFAULT_TTL_SECS)
}

fn ttl_from_extensions(ext: Option<&std::collections::BTreeMap<String, Value>>) -> Option<u64> {
    let map = ext?;
    ttl_from_value(map.get("x-ttl"))
}

fn ttl_from_value(v: Option<&Value>) -> Option<u64> {
    match v? {
        Value::Number(n) => n.as_u64(),
        Value::String(s) => parse_ttl_str(s),
        _ => None,
    }
}

/// Parse an `x-ttl` string: plain seconds (`"300"`) or a suffixed form
/// (`"30s"`, `"5m"`, `"1h"`). Logs and returns `None` on unsupported values.
fn parse_ttl_str(s: &str) -> Option<u64> {
    if let Ok(n) = s.parse::<u64>() {
        return Some(n);
    }
    let (num, mult) = if let Some(num) = s.strip_suffix('h') {
        (num, 3600)
    } else if let Some(num) = s.strip_suffix('m') {
        (num, 60)
    } else if let Some(num) = s.strip_suffix('s') {
        (num, 1)
    } else {
        warn!(
            "Unsupported x-ttl value '{s}' (expected seconds, '30s', '5m' or '1h') — using default"
        );
        return None;
    };
    if let Ok(n) = num.parse::<u64>() {
        Some(n * mult)
    } else {
        warn!(
            "Unparseable x-ttl value '{s}' (expected seconds, '30s', '5m' or '1h') — using default"
        );
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::roas_asyncapi::SubSchema;
    use serde_json::json;
    use std::collections::BTreeMap;

    /// Test convenience wrapper.
    fn loaded_topics(dir: &Path) -> anyhow::Result<Vec<TopicDef>> {
        let api = load_specs(dir.to_str().unwrap(), false)?;
        Ok(api.topics())
    }

    fn schema_with_properties(props: BTreeMap<String, Value>) -> Schema {
        let mut properties = BTreeMap::new();
        for (k, v) in props {
            let sub: SubSchema = serde_json::from_value(v).unwrap();
            properties.insert(k, sub);
        }
        Schema {
            properties,
            ..Default::default()
        }
    }

    #[test_log::test]
    fn test_extract_scalar_fields() {
        let props = BTreeMap::from([
            ("celsius".to_string(), json!({"type": "number"})),
            ("sensor_id".to_string(), json!({"type": "integer"})),
            ("ok".to_string(), json!({"type": "boolean"})),
            ("label".to_string(), json!({"type": "string"})),
            (
                "nested".to_string(),
                json!({"type": "object", "properties": {"x": {"type": "number"}}}),
            ),
            ("items".to_string(), json!({"type": "array"})),
        ]);
        let schema = schema_with_properties(props);
        let doc = Document::default();
        let fields = extract_fields_from_schema(&schema, &doc);
        assert_eq!(fields.len(), 4);
        // BTreeMap ordering, so sorted by key
        let get = |name: &str| fields.iter().find(|f| f.name == name).unwrap();
        assert_eq!(get("celsius").graphql_type, "Float");
        assert_eq!(get("sensor_id").graphql_type, "Int");
        assert_eq!(get("ok").graphql_type, "Boolean");
        assert_eq!(get("label").graphql_type, "String");
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
                    },
                    "bindings": {
                        "mqtt": {
                            "qos": 0,
                            "retain": false,
                            "bindingVersion": "0.2.0"
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

        let dir = std::env::temp_dir().join("mqtt-graphql-test-specs");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("test.json");
        std::fs::write(&path, serde_json::to_string_pretty(&spec).unwrap()).unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(topics.len(), 1);
        assert_eq!(
            topics[0].topic,
            "termodinamica/compressor/temperature:Publisher"
        );
        assert_eq!(topics[0].fields.len(), 3);
        assert_eq!(topics[0].fields[0].name, "celsius");
        assert_eq!(topics[0].fields[0].graphql_type, "Float");
    }

    #[test_log::test]
    fn test_no_mqtt_binding_skipped() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "some.channel:Publisher": {
                    "address": "some/channel:Publisher",
                    "messages": {
                        "Message": {
                            "$ref": "#/components/messages/some.channel:Publisher:Message"
                        }
                    },
                    "bindings": {
                        "http": {}
                    }
                }
            },
            "operations": {
                "some.channel:Publisher": {
                    "action": "send",
                    "channel": {
                        "$ref": "#/channels/some.channel:Publisher"
                    }
                },
            },
            "components": {
                "messages": {
                    "some.channel:Publisher:Message": {
                        "payload": { "$ref": "#/components/schemas/SomeType" }
                    }
                },
                "schemas": {
                    "SomeType": {
                        "type": "object",
                        "properties": {
                            "x": { "type": "integer" }
                        }
                    }
                }
            }
        });

        let dir = std::env::temp_dir().join("mqtt-graphql-test-no-mqtt");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("test.json");
        std::fs::write(&path, serde_json::to_string_pretty(&spec).unwrap()).unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        // Channel has no mqtt binding but has address, so it falls back to address
        // For this spec address is "some/channel:Publisher", so it is not skipped.
        // To test skipping, we need a channel with no bindings and no address.
        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "some/channel:Publisher");
    }

    #[test_log::test]
    fn test_empty_properties_returns_empty_fields() {
        let schema = Schema::default();
        let doc = Document::default();
        let fields = extract_fields_from_schema(&schema, &doc);
        assert_eq!(fields.len(), 0);
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
                    "bindings": {
                        "mqtt": {
                            "topic": "test/channel",
                            "qos": 0,
                            "retain": false
                        }
                    }
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

        let dir = std::env::temp_dir().join("mqtt-graphql-test-inline");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("test.json");
        std::fs::write(&path, serde_json::to_string_pretty(&spec).unwrap()).unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "test/channel:Publisher");
        assert_eq!(topics[0].fields.len(), 1);
        assert_eq!(topics[0].fields[0].name, "value");
        assert_eq!(topics[0].fields[0].graphql_type, "Float");
    }

    #[test_log::test]
    fn test_load_specs_skips_non_json_files() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-nonjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("readme.txt"), "not a spec").unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(topics.is_empty());
    }

    #[test_log::test]
    fn test_load_specs_rejects_invalid_json() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-invalidjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("broken.json"), "{ not json }").unwrap();

        let err = loaded_topics(&dir).unwrap_err();
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

        let err = loaded_topics(&dir).unwrap_err();
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
                    "address": "test/channel",
                    "bindings": { "mqtt": { "topic": "test/channel" } }
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

        let err = loaded_topics(&dir).unwrap_err();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(err.to_string().contains("only 3.x is supported"), "{err}");
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
                    "bindings": { "mqtt": { "topic": "one/channel" } }
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
                    "bindings": { "mqtt": { "topic": "two/channel" } }
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

        let dir = std::env::temp_dir().join("mqtt-graphql-test-multi");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(topics.len(), 2);
        // BTreeMap ordering
        assert!(topics.iter().any(|t| t.topic == "one/channel"));
        assert!(topics.iter().any(|t| t.topic == "two/channel"));
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

        let dir = std::env::temp_dir().join("mqtt-graphql-test-subscribe");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let api = load_specs(dir.to_str().unwrap(), false).unwrap();
        let subscribed_topics = api.subscribe_topics();
        let _ = std::fs::remove_dir_all(&dir);

        // We expect one topic that is not receive and the broadest
        assert_eq!(subscribed_topics.len(), 1);
        assert!(subscribed_topics.contains(&"two/#".to_string()));
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
                        "bindings": { "mqtt": { "topic": "ref/channel" } }
                    }
                }
            }
        });

        let dir = std::env::temp_dir().join("mqtt-graphql-test-channel-ref");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "ref/channel");
        assert_eq!(topics[0].fields[0].name, "x");
        assert_eq!(topics[0].fields[0].graphql_type, "Int");
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
                    "bindings": { "mqtt": { "topic": "bare/channel" } }
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

        let dir = std::env::temp_dir().join("mqtt-graphql-test-no-payload");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(
            dir.join("test.json"),
            serde_json::to_string_pretty(&spec).unwrap(),
        )
        .unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(topics.len(), 1);
        assert_eq!(topics[0].topic, "bare/channel");
        assert!(topics[0].fields.is_empty());
    }

    #[test_log::test]
    fn test_extensions_from_payload_schema() {
        let schema = json!({
            "type": "object",
            "properties": {
                "current_a": {"type": "number", "x-unit": "A", "x-display-name": "Current A"},
                "active_power_total": {"type": "number", "x-unit": "W"},
                "power_factor_a": {"type": "number"},
                "ignored": {"type": "number", "x-nested": {"deep": true}}
            }
        });
        let extensions = extensions_from_payload_schema(&schema);
        assert_eq!(
            extensions
                .get("current_a")
                .map(|e| e.get("unit").map(String::as_str)),
            Some(Some("A"))
        );
        assert_eq!(
            extensions
                .get("current_a")
                .map(|e| e.get("display-name").map(String::as_str)),
            Some(Some("Current A"))
        );
        assert_eq!(
            extensions
                .get("active_power_total")
                .map(|e| e.get("unit").map(String::as_str)),
            Some(Some("W"))
        );
        assert!(!extensions.contains_key("power_factor_a"));
        // Non-scalar extension values are ignored, leaving no entry at all.
        assert!(!extensions.contains_key("ignored"));
    }

    #[test_log::test]
    fn test_nullable_anyof_field() {
        let props = BTreeMap::from([(
            "current_a".to_string(),
            json!({"anyOf": [{"type": "number"}, {"type": "null"}]}),
        )]);
        let schema = schema_with_properties(props);
        let doc = Document::default();
        let fields = extract_fields_from_schema(&schema, &doc);
        assert_eq!(fields.len(), 1);
        assert_eq!(fields[0].name, "current_a");
        assert_eq!(fields[0].graphql_type, "Float");
    }

    #[test_log::test]
    fn test_parse_ttl_str() {
        assert_eq!(parse_ttl_str("300"), Some(300));
        assert_eq!(parse_ttl_str("30s"), Some(30));
        assert_eq!(parse_ttl_str("5m"), Some(300));
        assert_eq!(parse_ttl_str("1h"), Some(3600));
        assert_eq!(parse_ttl_str("0"), Some(0));
        assert_eq!(parse_ttl_str(""), None);
        assert_eq!(parse_ttl_str("abc"), None);
        assert_eq!(parse_ttl_str("5x"), None);
    }

    #[test_log::test]
    fn test_ttl_from_value() {
        assert_eq!(ttl_from_value(Some(&json!(45))), Some(45));
        assert_eq!(ttl_from_value(Some(&json!("2m"))), Some(120));
        assert_eq!(ttl_from_value(Some(&json!(-1.5))), None);
        assert_eq!(ttl_from_value(Some(&json!(true))), None);
        assert_eq!(ttl_from_value(None), None);
    }
}
