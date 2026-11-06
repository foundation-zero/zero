use std::collections::BTreeMap;
use std::fmt::Debug;
use std::path::{Path, PathBuf};

use crate::metadata::MetadataByTopic;
use crate::roas_asyncapi::{
    Channel, Document, Message, Operation, OperationAction, Schema, SchemaOrMultiFormat,
    SchemaType, SubSchema,
};
use anyhow::Context;
use jsonschema::Validator;
use log::{debug, info, warn};
use roas_asyncapi::common::reference::{RefOr, Reference};
use serde_json::Value;

use crate::api_model::{Api, Direction, FieldType, GroupDef, Payload, Spec, TopicDef, TopicKind};
use crate::message_validation::ValidatorBuilder;
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

fn load_spec(path: &Path, document_json: &Value) -> anyhow::Result<Spec> {
    let validator_builder = ValidatorBuilder::new(document_json.clone())?;

    let document = serde_json::from_value::<Document>(document_json.clone())
        .with_context(|| format!("parsing AsyncAPI document {}", path.display()))?;

    let topics = channels_from_document(&document, path, topic_from_channel)?;
    let subscribe_topics = channels_from_document(&document, path, channel_addresses_from_channel)?
        .into_iter()
        .fold(TopicMap::new(), |mut acc, topic| {
            if !acc.covers_topic(&topic) {
                acc.insert_with_replace(topic, ());
            }
            acc
        });

    let validators: Vec<(String, Validator)> =
        channels_from_document(&document, path, |channel_ref, _, _, channel, doc, _| {
            Ok(validator_from_channel(
                &validator_builder,
                channel_ref,
                channel,
                doc,
            ))
        })?;

    info!(
        "Parsed: {} topic(s) and {} validator(s) from '{}'.",
        topics.len(),
        validators.len(),
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

            let (_, operation) = resolve_operation(operation_ref, doc).with_context(|| {
                format!(
                    "unresolvable operation $ref '{}' ({}) in {}",
                    operation_name,
                    operation_ref
                        .reference()
                        .map_or("<inline channel>", |r| r.reference.as_str()),
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
            let (_, channel) = resolve_channel(&channel_ref, doc).with_context(|| {
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

/// The JSON Schema validator of a channel's payload, keyed by its topic: an
/// exact topic, or a wildcard filter for a Group (e.g. `power-tags/+/+`).
/// `None` for a channel without an address or payload, or whose schema does
/// not compile.
fn validator_from_channel(
    validator_builder: &ValidatorBuilder,
    channel_ref: &Reference,
    channel: &Channel,
    doc: &Document,
) -> Option<(String, Validator)> {
    let topic = wildcard_from_address(channel.address()?);
    let schema_ref = message_payload(channel_ref, channel, doc)?.schema_ref;
    match validator_builder.build_validator(&schema_ref) {
        Ok(validator) => Some((topic, validator)),
        Err(e) => {
            warn!(
                "Failed to compile JSON Schema for topic '{topic}': {e} — skipping validation for this topic"
            );
            None
        }
    }
}

/// Convert one channel into a [`TopicDef`]: a Group when its address is
/// parametrized, a single topic otherwise. Returns `None` for channels
/// without an address.
fn topic_from_channel(
    channel_ref: &Reference,
    channel_name: &str,
    action: OperationAction,
    channel: &Channel,
    doc: &Document,
    path: &Path,
) -> anyhow::Result<Option<TopicDef>> {
    let Some(address) = channel.address() else {
        warn!(
            "Channel '{}' in {} has no address, skipping",
            channel_name,
            path.display()
        );
        return Ok(None);
    };

    if channel.messages.is_empty() {
        info!("Channel '{channel_name}' (address: '{address}') has no messages");
    }

    let message_payload = message_payload(channel_ref, channel, doc);
    debug!("Parsed channel {channel_name} with payload {message_payload:?}");

    let kind = if is_parametrized_channel(Some(address)) {
        let field_attributes = message_payload
            .as_ref()
            .map(|m| m.field_attributes.clone())
            .unwrap_or_default();
        let group = group_from_channel(channel_name, channel, field_attributes, path)?;
        info!("Loaded topic group '{address}' from {}", path.display());
        TopicKind::Group(group)
    } else {
        TopicKind::Single
    };

    Ok(Some(TopicDef {
        topic: wildcard_from_address(address),
        operation: match action {
            OperationAction::Send => Direction::Send,
            OperationAction::Receive => Direction::Receive,
        },
        payload: message_payload.map(|m| m.payload),
        ttl_secs: ttl_for_channel(channel_ref, channel, doc),
        kind,
    }))
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

/// The payload of a channel's message, with what else is read from its
/// schema.
#[derive(Debug)]
struct MessagePayload {
    payload: Payload,
    /// JSON pointer to the payload schema in the document, which its
    /// validator is built from.
    schema_ref: String,
    /// Attributes per payload field, from the schema's `x-*` extensions.
    field_attributes: BTreeMap<String, BTreeMap<String, String>>,
}

/// The payload of the channel's first message; `None` when there is no
/// message, no payload, or the payload reference does not resolve.
///
/// Channels with multiple messages are not yet union-typed; only the first
/// message contributes a payload.
fn message_payload(
    channel_ref: &Reference,
    channel: &Channel,
    doc: &Document,
) -> Option<MessagePayload> {
    let Some((message_ref, message)) = channel_messages(channel_ref, channel, doc)
        .into_iter()
        .next()
    else {
        info!("Channel {} has no message", channel_ref.reference);
        return None;
    };
    // The message payload may be inline or a `$ref` into components
    let Some(payload_ref) = &message.payload else {
        info!("Channel {} message has no payload", channel_ref.reference);
        return None;
    };

    let Some((pointer, schema_or_multi)) = resolve_payload_schema(payload_ref, doc) else {
        info!(
            "Channel {} message payload reference does not resolve",
            channel_ref.reference,
        );
        return None;
    };

    let schema_ref = pointer.unwrap_or(format!("{message_ref}/payload"));
    Some(MessagePayload {
        payload: Payload {
            // Named after its schema component; an inline payload after its
            // full pointer.
            name: schema_ref
                .strip_prefix("#/components/schemas/")
                .unwrap_or(&schema_ref)
                .to_string(),
            fields: extract_fields_from_schema_or_multi(schema_or_multi, doc),
        },
        field_attributes: serde_json::to_value(schema_or_multi)
            .map(|schema| extensions_from_payload_schema(&schema))
            .unwrap_or_default(),
        schema_ref,
    })
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
            resolve_message(message_ref, doc).map(|(_, message)| (message_reference, message))
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
pub(crate) fn resolve_ref_to_entry<'a, T: Debug>(
    reference: &'a Reference,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
    mut traversed_keys: Vec<&'a str>,
) -> Option<(Option<String>, &'a T)> {
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
        RefOr::Item(entry) => Some((Some(reference.reference.clone()), entry)),
    }
}

fn resolve_refor<'a, T: Debug>(
    reference: &'a RefOr<T>,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
) -> Option<(Option<String>, &'a T)> {
    match reference {
        RefOr::Item(m) => Some((None, m)),
        RefOr::Reference(reference) => {
            resolve_ref_to_entry(reference, entries_main, entries_components, vec![])
        }
    }
}

fn resolve_channel<'a>(
    r: &'a RefOr<Channel>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Channel)> {
    resolve_refor(
        r,
        Some(&doc.channels),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.channels),
    )
}

fn resolve_operation<'a>(
    r: &'a RefOr<Operation>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Operation)> {
    resolve_refor(
        r,
        Some(&doc.operations),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.operations),
    )
}

fn resolve_message<'a>(
    r: &'a RefOr<Message>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Message)> {
    resolve_refor(
        r,
        None,
        doc.components
            .as_ref()
            .map(|componentens| &componentens.messages),
    )
}

#[must_use]
pub fn resolve_payload_schema<'a>(
    r: &'a RefOr<SchemaOrMultiFormat>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a SchemaOrMultiFormat)> {
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
) -> BTreeMap<String, FieldType> {
    let schema_entries = doc
        .components
        .as_ref()
        .map(|componentens| &componentens.schemas);

    match schema_or_multi {
        SchemaOrMultiFormat::Schema(schema) => extract_fields_from_schema(schema, schema_entries),
        SchemaOrMultiFormat::MultiFormat(mf) => {
            // Try to deserialize the raw schema value as a Schema
            if let Ok(schema) = serde_json::from_value::<Schema>(mf.schema.clone()) {
                extract_fields_from_schema(&schema, schema_entries)
            } else {
                info!("Payload schema has no fields");
                BTreeMap::new()
            }
        }
        SchemaOrMultiFormat::Bool(_) => {
            info!("Payload schema has no fields");
            BTreeMap::new()
        }
    }
}

fn extract_fields_from_schema(
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> BTreeMap<String, FieldType> {
    // Fields colliding after lowerCamel sanitization are not tolerated here:
    // they surface as errors from `validate_topics` instead.
    schema
        .properties
        .iter()
        .filter_map(|(name, subschema)| {
            let field_type = field_type_for_subschema(name.clone(), subschema, schema_entries)?;

            Some((name.clone(), field_type))
        })
        .collect()
}

/// Derive a field type from a (possibly `$ref`'d) subschema.
fn field_type_for_subschema(
    name: String,
    sub: &SubSchema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    match sub {
        SubSchema::Bool(_) => None,
        SubSchema::Schema(boxed) => match boxed.as_ref() {
            RefOr::Item(schema) => type_from_schema(name, schema, schema_entries),
            RefOr::Reference(r) => {
                let Some((reference, resolved)) =
                    resolve_ref_to_entry(r, None, schema_entries, vec![])
                else {
                    warn!("Cannot resolve reference {r:?} while determining payload type");
                    return None;
                };
                let name = reference
                    .and_then(|r| r.rsplit('/').next().map(ToOwned::to_owned))
                    .unwrap_or(name);

                match resolved {
                    SchemaOrMultiFormat::Schema(s) => type_from_schema(name, s, schema_entries),
                    SchemaOrMultiFormat::MultiFormat(mf) => {
                        let schema: Schema = serde_json::from_value(mf.schema.clone()).ok()?;
                        type_from_schema(name, &schema, schema_entries)
                    }
                    SchemaOrMultiFormat::Bool(_) => None,
                }
            }
        },
    }
}

fn type_from_schema(
    name: String,
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    if let Some(schema_type) = &schema.schema_type {
        return match schema_type {
            SchemaType::Single(t) => field_type_for_json_type(name, t, schema, schema_entries),
            SchemaType::Multiple(types) => {
                for (index, t) in types.iter().enumerate() {
                    if t == "null" {
                        continue;
                    }
                    if let Some(field_type) = field_type_for_json_type(
                        format!("{name}{index}"),
                        t,
                        schema,
                        schema_entries,
                    ) {
                        // TODO: properly handle unions here
                        return Some(field_type);
                    }
                }
                None
            }
        };
    }

    // Handle nullable via anyOf / oneOf / allOf
    if let Some(any_of) = &schema.any_of {
        for (index, sub) in any_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }
    if let Some(one_of) = &schema.one_of {
        for (index, sub) in one_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }
    if let Some(all_of) = &schema.all_of {
        for (index, sub) in all_of.iter().enumerate() {
            if let Some(t) = field_type_for_subschema(format!("{name}{index}"), sub, schema_entries)
            {
                return Some(t);
            }
        }
    }

    None
}

fn field_type_for_json_type(
    name: String,
    t: &str,
    schema: &Schema,
    schema_entries: Option<&BTreeMap<String, RefOr<SchemaOrMultiFormat>>>,
) -> Option<FieldType> {
    match t {
        "object" => {
            let fields = extract_fields_from_schema(schema, schema_entries);
            (!fields.is_empty()).then(|| FieldType::Object(name, Box::new(fields)))
        }
        "number" => Some(FieldType::Float),
        "integer" => Some(FieldType::Int),
        "boolean" => Some(FieldType::Boolean),
        "string" => Some(FieldType::String),
        _ => None,
    }
}

/// Effective TTL for cached values of a channel: the maximum `x-ttl`
/// across its messages (a channel may declare several), falling back to the
/// channel's own extension, then the global default.
fn ttl_for_channel(channel_ref: &Reference, channel: &Channel, doc: &Document) -> Option<u64> {
    channel_messages(channel_ref, channel, doc)
        .into_values()
        .filter_map(|message| ttl_from_extensions(message.extensions.as_ref()))
        .max()
        .or_else(|| ttl_from_extensions(channel.extensions.as_ref()))
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
    use crate::{api_model::FieldType, roas_asyncapi::SubSchema};
    use serde_json::json;
    use std::collections::BTreeMap;

    /// The topics `load_spec` reads from a document, before they go into a
    /// Spec's Query tree.
    fn loaded_topics(spec: &Value) -> anyhow::Result<Vec<TopicDef>> {
        let document = serde_json::from_value::<Document>(spec.clone())?;
        channels_from_document(&document, Path::new("test"), topic_from_channel)
    }

    /// The payload fields of a topic that must have a payload.
    fn fields(topic: &TopicDef) -> &BTreeMap<String, FieldType> {
        &topic.payload.as_ref().unwrap().fields
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
            ("reffed".to_string(), json!({"$ref": "#/components/nested"})),
            ("items".to_string(), json!({"type": "array"})),
        ]);
        let schema = schema_with_properties(props);
        let schema_entries = BTreeMap::from([(
            "nested".to_string(),
            RefOr::Item(
                serde_json::from_value::<SchemaOrMultiFormat>(
                    json!({"type": "object", "properties": {"x": {"type": "number"}}}),
                )
                .unwrap(),
            ),
        )]);

        let fields = extract_fields_from_schema(&schema, Some(&schema_entries));
        assert_eq!(fields.len(), 6);
        // BTreeMap ordering, so sorted by key
        let get = |name: &str| fields.get(name).unwrap();
        assert_eq!(get("celsius"), &FieldType::Float);
        assert_eq!(get("sensor_id"), &FieldType::Int);
        assert_eq!(get("ok"), &FieldType::Boolean);
        assert_eq!(get("label"), &FieldType::String);
        assert_eq!(
            get("nested"),
            &FieldType::Object(
                "nested".to_string(),
                Box::new(BTreeMap::from([("x".to_string(), FieldType::Float); 1]))
            )
        );
        assert_eq!(
            get("reffed"),
            &FieldType::Object(
                "nested".to_string(),
                Box::new(BTreeMap::from([("x".to_string(), FieldType::Float); 1]))
            )
        );
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
    fn test_empty_properties_returns_empty_fields() {
        let schema = Schema::default();
        let fields = extract_fields_from_schema(&schema, None);
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
    fn test_validators_are_keyed_by_topic_and_skip_channels_without_payload() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "power": {
                    "address": "power/{panel}",
                    "messages": {"Message": {"payload": {"type": "object"}}}
                },
                "bare": {"address": "bare/channel"}
            },
            "operations": {
                "power": {"action": "send", "channel": {"$ref": "#/channels/power"}},
                "bare": {"action": "send", "channel": {"$ref": "#/channels/bare"}}
            }
        });
        let document = serde_json::from_value::<Document>(spec.clone()).unwrap();
        let validator_builder = ValidatorBuilder::new(spec).unwrap();

        let validators = channels_from_document(
            &document,
            Path::new("test"),
            |channel_ref, _, _, channel, doc, _| {
                Ok(validator_from_channel(
                    &validator_builder,
                    channel_ref,
                    channel,
                    doc,
                ))
            },
        )
        .unwrap();

        let topics: Vec<&str> = validators.iter().map(|(topic, _)| topic.as_str()).collect();
        assert_eq!(topics, ["power/+"]);
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
            "unresolvable channel $ref 'does-not-exist' (#/channels/does-not-exist) in test",
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
        let fields = extract_fields_from_schema(&schema, None);
        assert_eq!(fields.len(), 1);
        assert_eq!(fields.get("current_a"), Some(&FieldType::Float));
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
