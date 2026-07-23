use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::Context;
use log::{info, warn};
use roas_asyncapi::common::reference::{RefOr, Reference};
use roas_asyncapi::v3_0::channel::Channel;
use roas_asyncapi::v3_0::message::Message;
use roas_asyncapi::v3_0::schema::{Schema, SchemaOrMultiFormat};
use roas_asyncapi::v3_0::Document;
use serde_json::Value;

use crate::graphql::graphql_type_for_subschema;
use crate::naming::*;

#[derive(Debug, Clone)]
pub struct TopicDef {
    pub topic: String,
    pub fields: Vec<FieldDef>,
    /// Raw JSON Schema value for the payload, used for live validation in listen mode.
    pub payload_schema: Option<Value>,
    /// TTL in seconds for cached values of this topic. Determined from
    /// `x-ttl` extensions on the AsyncAPI message or channel
    /// (per-schema override) or a global default.
    pub ttl_secs: u64,
}

/// A parametrized topic family declared by a single channel, e.g.
/// address `power-tags/{panel}/{slug}` with mqtt binding `power-tags/+/+`.
#[derive(Debug, Clone)]
pub struct TopicGroupDef {
    /// Static prefix of the address (`power-tags`); seeds the GraphQL names.
    pub group: String,
    /// Wildcard MQTT topic to subscribe to (`power-tags/+/+`).
    pub pattern: String,
    /// Parameter names, in address order (`panel`, `slug`). Reserved for
    /// future use (e.g. per-parameter filtering); nothing reads it today.
    pub params: Vec<String>,
    pub fields: Vec<FieldDef>,
    /// Raw JSON Schema value for the payload.
    pub payload_schema: Option<Value>,
    /// Extension attributes per payload field (`x-*` schema extensions
    /// minus the prefix), keyed by raw field name.
    pub value_extensions: BTreeMap<String, BTreeMap<String, String>>,
    pub ttl_secs: u64,
}

#[derive(Debug, Clone)]
pub struct FieldDef {
    pub name: String,
    pub graphql_type: String,
}

/// Read and parse every AsyncAPI document in `spec_dir` once, returning
/// `(file name, path, document)` for each. Non-JSON files and topic-metadata
/// files are skipped; unreadable or invalid `.json` files are an error —
/// see [`read_asyncapi_document`].
fn spec_documents(spec_dir: &str) -> anyhow::Result<Vec<(String, PathBuf, Document)>> {
    let dir = Path::new(spec_dir);
    if !dir.is_dir() {
        anyhow::bail!("spec_dir does not exist or is not a directory: {spec_dir}");
    }

    std::fs::read_dir(dir)?
        .map(|entry| {
            let path = entry?.path();
            let file_name = path
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("")
                .to_string();
            Ok((file_name, path))
        })
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .filter(|(_, path)| path.extension().and_then(|e| e.to_str()) == Some("json"))
        .filter(|(_, path)| !crate::metadata::is_metadata_file(path))
        .map(|(file_name, path)| read_asyncapi_document(&path).map(|doc| (file_name, path, doc)))
        .collect()
}

/// Load AsyncAPI 3.0.0 spec files from a directory in a single pass over the
/// spec directory, extracting both concrete topics and parametrized groups.
///
/// Consumers that only need one of the two should still use this loader and
/// ignore the other half, so each spec file is read exactly once.
pub fn load_specs_and_groups(
    spec_dir: &str,
) -> anyhow::Result<(Vec<TopicDef>, Vec<TopicGroupDef>)> {
    let docs = spec_documents(spec_dir)?;

    let topics: Vec<TopicDef> = docs
        .iter()
        .map(|(_, path, doc)| topics_from_document(doc, path))
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .collect();

    let groups: Vec<TopicGroupDef> = docs
        .iter()
        .map(|(_, path, doc)| groups_from_document(doc, path))
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .collect();

    info!(
        "Loaded {} topic(s) and {} topic group(s) from {}",
        topics.len(),
        groups.len(),
        spec_dir
    );
    Ok((topics, groups))
}

/// Extract concrete topics from one document, erroring on unresolvable
/// channel references.
fn topics_from_document(doc: &Document, path: &Path) -> anyhow::Result<Vec<TopicDef>> {
    if doc.channels.is_empty() {
        info!("File {} has no channels, skipping", path.display());
        return Ok(Vec::new());
    }

    doc.channels
        .iter()
        .map(|(channel_name, channel_ref)| {
            let channel = resolve_channel(channel_ref, doc).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' in {}",
                    channel_name,
                    path.display()
                )
            })?;
            Ok(topic_from_channel(channel_name, channel, doc, path))
        })
        .collect::<anyhow::Result<Vec<_>>>()
        .map(|topics| topics.into_iter().flatten().collect())
}

/// Extract parametrized groups from one document, erroring on unresolvable
/// channel references or malformed parametrized channels.
fn groups_from_document(doc: &Document, path: &Path) -> anyhow::Result<Vec<TopicGroupDef>> {
    doc.channels
        .iter()
        .map(|(channel_name, channel_ref)| {
            let channel = resolve_channel(channel_ref, doc).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' in {}",
                    channel_name,
                    path.display()
                )
            })?;
            group_from_channel(channel_name, channel, doc, path)
        })
        .collect::<anyhow::Result<Vec<_>>>()
        .map(|groups| groups.into_iter().flatten().collect())
}

/// Convert one concrete (non-parametrized) channel into a [`TopicDef`];
/// returns `None` for parametrized channels or channels without a topic.
fn topic_from_channel(
    channel_name: &str,
    channel: &Channel,
    doc: &Document,
    path: &Path,
) -> Option<TopicDef> {
    // Parametrized channels are handled by groups_from_document.
    let binding_topic = mqtt_topic_from_channel(channel);
    if is_parametrized_channel(channel.address(), binding_topic.as_deref()) {
        return None;
    }

    let mqtt_topic = binding_topic.or_else(|| channel.address().map(|s| s.to_string()));
    let mqtt_topic = match mqtt_topic {
        Some(t) => t,
        None => {
            warn!(
                "Channel '{}' in {} has no mqtt binding topic and no address, skipping",
                channel_name,
                path.display()
            );
            return None;
        }
    };

    if channel.messages.is_empty() {
        info!(
            "Channel '{}' (topic: '{}') has no messages",
            channel_name, mqtt_topic
        );
    }

    let (fields, payload_schema) = message_fields(channel, doc);

    Some(TopicDef {
        topic: mqtt_topic,
        fields,
        payload_schema,
        ttl_secs: ttl_for_channel(channel, doc),
    })
}

/// Convert one parametrized channel into a [`TopicGroupDef`]; returns
/// `None` for concrete channels. A parametrized channel without an address
/// is an error: neither the group name nor the wildcard pattern can be
/// derived without it.
fn group_from_channel(
    channel_name: &str,
    channel: &Channel,
    doc: &Document,
    path: &Path,
) -> anyhow::Result<Option<TopicGroupDef>> {
    let binding_topic = mqtt_topic_from_channel(channel);
    if !is_parametrized_channel(channel.address(), binding_topic.as_deref()) {
        return Ok(None);
    }
    let Some(address) = channel.address().map(str::to_string) else {
        anyhow::bail!(
            "parametrized channel '{}' in {} has no address",
            channel_name,
            path.display()
        );
    };
    let params = extract_params(&address);
    let group = static_prefix(&address).unwrap_or_else(|| address.clone());
    let pattern = binding_topic
        .filter(|topic| topic.contains('+') || topic.contains('#'))
        .unwrap_or_else(|| wildcard_from_address(&address));

    let (fields, payload_schema) = message_fields(channel, doc);
    let value_extensions = payload_schema
        .as_ref()
        .map(extensions_from_payload_schema)
        .unwrap_or_default();

    info!(
        "Loaded topic group '{}' ({}) from {}",
        group,
        pattern,
        path.display()
    );
    Ok(Some(TopicGroupDef {
        group,
        pattern,
        params,
        fields,
        payload_schema,
        value_extensions,
        ttl_secs: ttl_for_channel(channel, doc),
    }))
}

/// Read and parse one file into an AsyncAPI 3.x `Document`.
///
/// Errors when the file is unreadable, not valid JSON, lacks an `asyncapi`
/// version, or is not an AsyncAPI 3.x document — a spec directory is
/// expected to contain only loadable specs.
fn read_asyncapi_document(path: &Path) -> anyhow::Result<Document> {
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

    serde_json::from_value::<Document>(spec_value)
        .with_context(|| format!("parsing AsyncAPI document {}", path.display()))
}

/// Whether a channel describes a parametrized topic family rather than one
/// concrete topic: a `{placeholder}` segment in the address or `+`/`#` in
/// the binding.
fn is_parametrized_channel(address: Option<&str>, binding_topic: Option<&str>) -> bool {
    address.is_some_and(|address| {
        address
            .split('/')
            .any(|segment| param_name(segment).is_some())
    }) || binding_topic.is_some_and(|topic| topic.contains('+') || topic.contains('#'))
}

/// Parameter name when an address segment is a `{placeholder}`, else
/// `None`: `{panel}` → `panel`.
fn param_name(segment: &str) -> Option<&str> {
    segment.strip_prefix('{')?.strip_suffix('}')
}

/// Parameter names in order: `power-tags/{panel}/{slug}` → `[panel, slug]`.
fn extract_params(address: &str) -> Vec<String> {
    address
        .split('/')
        .filter_map(param_name)
        .map(str::to_string)
        .collect()
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
fn message_fields(channel: &Channel, doc: &Document) -> (Vec<FieldDef>, Option<Value>) {
    let Some(message) = channel_messages(channel, doc).into_iter().next() else {
        return (Vec::new(), None);
    };
    // The message payload may be inline or a `$ref` into components; both are
    // resolved by `resolve_payload_schema`.
    let Some(payload_ref) = &message.payload else {
        return (Vec::new(), None);
    };
    match resolve_payload_schema(payload_ref, doc) {
        Some(schema_or_multi) => {
            let schema_value = serde_json::to_value(&schema_or_multi).ok();
            let fields = extract_fields_from_schema_or_multi(&schema_or_multi, doc);
            (fields, schema_value)
        }
        None => (Vec::new(), None),
    }
}

/// All messages referenced by the channel, resolved against components.
fn channel_messages<'a>(channel: &'a Channel, doc: &'a Document) -> Vec<&'a Message> {
    channel
        .messages
        .values()
        .filter_map(|message_ref| resolve_message(message_ref, doc))
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

/// Resolve a channel that may be a `$ref` into components.
///
/// Near-duplicate of [`resolve_ref_to_entry`] (as are the message/schema
/// resolvers) but kept separate: channel refs additionally fall back to
/// root-level `channels` entries and guard self-referential component refs.
fn resolve_channel<'a>(r: &'a RefOr<Channel>, doc: &'a Document) -> Option<&'a Channel> {
    match r {
        RefOr::Item(c) => Some(c),
        RefOr::Reference(reference) => {
            let key = reference
                .component_key("channels")
                .or_else(|| reference.local_key())?;
            // If the key is the current iteration key itself, avoid infinite recursion
            // by looking directly in components without recursing into the same ref.
            if let Some(components) = &doc.components {
                if let Some(entry) = components.channels.get(&key) {
                    return match entry {
                        RefOr::Item(c) => Some(c),
                        RefOr::Reference(r2) => {
                            let key2 = r2.component_key("channels").or_else(|| r2.local_key())?;
                            if key2 == key {
                                return None;
                            }
                            components.channels.get(&key2)?.item()
                        }
                    };
                }
            }
            if let Some(entry) = doc.channels.get(&key) {
                if let RefOr::Item(c) = entry {
                    return Some(c);
                }
                // Root entry is itself a $ref — if it points to the same key we'd loop
                return None;
            }
            None
        }
    }
}

fn mqtt_topic_from_channel(channel: &Channel) -> Option<String> {
    let bindings = channel.bindings.as_ref()?.item()?;
    let mqtt_val = bindings.get("mqtt")?;
    mqtt_val.get("topic")?.as_str().map(|s| s.to_string())
}

/// Follow a component `$ref` to its entry in one components map, resolving
/// at most one extra level of indirection (`ref` → `ref` → item).
///
/// Shared by [`resolve_message`] and [`resolve_payload_schema`].
/// [`resolve_channel`] duplicates this pattern but cannot reuse it: it also
/// falls back to root-level `channels` entries and guards against
/// self-referential channel refs.
fn resolve_ref_to_entry<'a, T>(
    reference: &Reference,
    section: &str,
    entries: &'a BTreeMap<String, RefOr<T>>,
) -> Option<&'a RefOr<T>> {
    let key = reference
        .component_key(section)
        .or_else(|| reference.local_key())?;
    match entries.get(&key)? {
        RefOr::Reference(nested) => {
            let key2 = nested
                .component_key(section)
                .or_else(|| nested.local_key())?;
            // A ref pointing back at itself would loop forever.
            if key2 == key {
                return None;
            }
            entries.get(&key2)
        }
        entry => Some(entry),
    }
}

fn resolve_message<'a>(r: &'a RefOr<Message>, doc: &'a Document) -> Option<&'a Message> {
    match r {
        RefOr::Item(m) => Some(m),
        RefOr::Reference(reference) => {
            resolve_ref_to_entry(reference, "messages", &doc.components.as_ref()?.messages)?.item()
        }
    }
}

fn resolve_payload_schema<'a>(
    r: &'a RefOr<SchemaOrMultiFormat>,
    doc: &'a Document,
) -> Option<SchemaOrMultiFormat> {
    match r {
        RefOr::Item(s) => Some(s.clone()),
        RefOr::Reference(reference) => {
            resolve_ref_to_entry(reference, "schemas", &doc.components.as_ref()?.schemas)?
                .item()
                .cloned()
        }
    }
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
                Vec::new()
            }
        }
        SchemaOrMultiFormat::Bool(_) => Vec::new(),
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
fn ttl_for_channel(channel: &Channel, doc: &Document) -> u64 {
    channel_messages(channel, doc)
        .into_iter()
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
    match num.parse::<u64>() {
        Ok(n) => Some(n * mult),
        Err(_) => {
            warn!(
                "Unparseable x-ttl value '{s}' (expected seconds, '30s', '5m' or '1h') — using default"
            );
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use roas_asyncapi::v3_0::schema::{Schema, SubSchema};
    use serde_json::json;
    use std::collections::BTreeMap;

    /// Test convenience wrapper extracting just the topics.
    fn loaded_topics(dir: &Path) -> anyhow::Result<Vec<TopicDef>> {
        let (topics, _) = load_specs_and_groups(dir.to_str().unwrap())?;
        Ok(topics)
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

    #[test]
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

    #[test]
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
                            "topic": "termodinamica/compressor/temperature",
                            "qos": 0,
                            "retain": false,
                            "bindingVersion": "0.2.0"
                        }
                    }
                }
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
        assert_eq!(topics[0].topic, "termodinamica/compressor/temperature");
        assert_eq!(topics[0].fields.len(), 3);
        assert_eq!(topics[0].fields[0].name, "celsius");
        assert_eq!(topics[0].fields[0].graphql_type, "Float");
    }

    #[test]
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

    #[test]
    fn test_empty_properties_returns_empty_fields() {
        let schema = Schema::default();
        let doc = Document::default();
        let fields = extract_fields_from_schema(&schema, &doc);
        assert_eq!(fields.len(), 0);
    }

    #[test]
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
        assert_eq!(topics[0].topic, "test/channel");
        assert_eq!(topics[0].fields.len(), 1);
        assert_eq!(topics[0].fields[0].name, "value");
        assert_eq!(topics[0].fields[0].graphql_type, "Float");
    }

    #[test]
    fn test_load_specs_skips_non_json_files() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-nonjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("readme.txt"), "not a spec").unwrap();

        let topics = loaded_topics(&dir).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(topics.is_empty());
    }

    #[test]
    fn test_load_specs_rejects_invalid_json() {
        let dir = std::env::temp_dir().join("mqtt-graphql-test-invalidjson");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("broken.json"), "{ not json }").unwrap();

        let err = loaded_topics(&dir).unwrap_err();
        let _ = std::fs::remove_dir_all(&dir);

        assert!(err.to_string().contains("parsing JSON"), "{err}");
    }

    #[test]
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

    #[test]
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

    #[test]
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

    #[test]
    fn test_channel_ref_is_resolved() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "referenced.channel:Publisher": {
                    "$ref": "#/components/channels/referenced.channel:Publisher"
                }
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

    #[test]
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
            }
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

    #[test]
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

    #[test]
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

    #[test]
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

    #[test]
    fn test_ttl_from_value() {
        assert_eq!(ttl_from_value(Some(&json!(45))), Some(45));
        assert_eq!(ttl_from_value(Some(&json!("2m"))), Some(120));
        assert_eq!(ttl_from_value(Some(&json!(-1.5))), None);
        assert_eq!(ttl_from_value(Some(&json!(true))), None);
        assert_eq!(ttl_from_value(None), None);
    }
}
