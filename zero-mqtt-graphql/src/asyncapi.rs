use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::Context;
use log::{info, warn};
use roas_asyncapi::common::reference::{RefOr, Reference};
use roas_asyncapi::v3_0::channel::Channel;
use roas_asyncapi::v3_0::message::Message;
use roas_asyncapi::v3_0::operation::OperationAction;
use roas_asyncapi::v3_0::schema::{Schema, SchemaOrMultiFormat, SubSchema};
use roas_asyncapi::v3_0::Document;
use serde_json::{json, Value};

use crate::extension::{parse_extension, GraphqlExtension};
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
    /// Raw JSON Schema for the payload. For a multi-type `{field}` group it's
    /// the permissive `anyOf` of every branch, so it can't catch an out-of-bounds
    /// value on a single field; `field_schemas` handles that.
    pub payload_schema: Option<Value>,
    /// The exact schema per concrete topic (group pattern with its `+` filled
    /// in), from the channel's `x-{param}-schema` extension. Lets each topic be
    /// validated against its own schema instead of the group-wide union, like
    /// thrs-api's per-field validation. Empty without that extension (single-type
    /// groups, or multi-`+` patterns).
    pub field_schemas: BTreeMap<String, Value>,
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

/// A pydantic model referenced by a field that isn't a scalar or a
/// `Stamped` envelope (e.g. `PidControllerValues`). Gets its own GraphQL
/// type instead of getting dropped. Same idea as THRS's own
/// `pydantic_to_strawberry_type`: every model becomes its own named type.
#[derive(Debug, Clone)]
pub struct ObjectTypeDef {
    /// Schema `title`, used as-is for the GraphQL type name.
    pub name: String,
    pub fields: Vec<FieldDef>,
}

/// Object types found so far, keyed by name. Dedupes a schema referenced
/// from multiple fields. Threaded as `&mut` through the schema walk.
pub type ObjectTypeRegistry = BTreeMap<String, ObjectTypeDef>;

/// A topic (or wildcard pattern) some described application *receives* on,
/// i.e. one this bridge may publish to. Declared by a channel with a
/// `receive` operation. Not a query field: the bridge only subscribes to
/// what an application sends.
#[derive(Debug, Clone)]
pub struct PublishTargetDef {
    pub pattern: String,
    /// Raw JSON Schema of the payload the receiver expects.
    pub payload_schema: Option<Value>,
}

/// One operation of a document, resolved to its channel's topic template so
/// an extension can name the operation it binds to instead of a raw topic,
/// and to the payload schema its messages carry so the extension can derive
/// the GraphQL shape of what it reads or writes there.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OperationDef {
    pub action: OperationAction,
    /// The channel's address template without the `:<Role>` suffix, e.g.
    /// `thrs/controller/{module}/parameters`.
    pub address: String,
    /// The MQTT pattern (`{param}` -> `+`).
    pub pattern: String,
    /// The document that declares the operation; `$ref`s in `payload` and
    /// `parameter_schemas` are relative to it.
    pub document: String,
    /// The payload schema of the operation's message, as the document
    /// declares it (a `$ref` into `components.schemas`, or inline).
    pub payload: Option<Value>,
    /// For a single-parameter address: the payload schema per parameter
    /// value (the message's `x-{param}-schema`), which pins each concrete
    /// topic to the one schema it carries instead of the channel's union.
    pub parameter_schemas: BTreeMap<String, Value>,
}

impl OperationDef {
    /// The payload schema of the concrete topic `parameters` select: the
    /// per-value schema when the message declares one, else the message's.
    pub fn schema(&self, parameters: &BTreeMap<String, String>) -> Option<&Value> {
        parameters
            .values()
            .find_map(|value| self.parameter_schemas.get(value))
            .or(self.payload.as_ref())
    }

    /// The concrete topic for the given parameter values: every `{param}`
    /// segment of the address must be supplied, and only those.
    pub fn topic(&self, parameters: &BTreeMap<String, String>) -> anyhow::Result<String> {
        let mut used: BTreeSet<&str> = BTreeSet::new();
        let segments = self
            .address
            .split('/')
            .map(|segment| match param_name(segment) {
                Some(name) => {
                    used.insert(name);
                    parameters.get(name).map(String::as_str).ok_or_else(|| {
                        anyhow::anyhow!("operation on '{}' needs parameter '{name}'", self.address)
                    })
                }
                None => Ok(segment),
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        if let Some(extra) = parameters.keys().find(|k| !used.contains(k.as_str())) {
            anyhow::bail!("operation on '{}' has no parameter '{extra}'", self.address);
        }
        Ok(segments.join("/"))
    }
}

/// Every operation of every loaded document, by operation key.
pub type OperationIndex = BTreeMap<String, OperationDef>;

/// Whether an MQTT topic matches a subscription pattern (`+` one level, `#`
/// the rest); a pattern without wildcards matches only itself.
pub fn topic_matches(pattern: &str, topic: &str) -> bool {
    let mut topic_segments = topic.split('/');
    for pattern_segment in pattern.split('/') {
        if pattern_segment == "#" {
            return true;
        }
        match topic_segments.next() {
            Some(segment) if pattern_segment == "+" || pattern_segment == segment => {}
            _ => return false,
        }
    }
    topic_segments.next().is_none()
}

/// How a document's operations use one channel: whether some described
/// application sends on it (so the bridge subscribes) and/or receives on it
/// (so the bridge may publish). A channel no operation names counts as sent:
/// older specs declare channels only.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
struct ChannelUse {
    send: bool,
    receive: bool,
    /// Keys of the channel messages the send operations name, in
    /// operation order: the payloads sent on the channel.
    send_messages: Vec<String>,
    /// Keys of the channel messages the receive operations name.
    receive_messages: Vec<String>,
}

impl ChannelUse {
    fn subscribed(&self) -> bool {
        self.send || !self.receive
    }
}

/// The message an operation of one direction carries: the first of the
/// channel's messages its operations name, else the channel's first message
/// (a channel with one message needs no operation to say so).
fn select_message<'a>(
    channel: &'a Channel,
    doc: &'a Document,
    preferred: &[String],
) -> Option<&'a Message> {
    preferred
        .iter()
        .find_map(|key| channel.messages.get(key))
        .and_then(|message| resolve_message(message, doc))
        .or_else(|| channel_messages(channel, doc).into_iter().next())
}

/// The [`ChannelUse`] of every channel a document's operations name.
fn channel_uses(doc: &Document) -> BTreeMap<String, ChannelUse> {
    let mut uses: BTreeMap<String, ChannelUse> = BTreeMap::new();
    for operation in doc.operations.values() {
        let RefOr::Item(operation) = operation else {
            continue;
        };
        let Some(key) = operation.channel.local_key() else {
            continue;
        };
        let entry = uses.entry(key).or_default();
        let messages = operation.messages.iter().filter_map(|r| r.local_key());
        match operation.action {
            OperationAction::Send => {
                entry.send = true;
                entry.send_messages.extend(messages);
            }
            OperationAction::Receive => {
                entry.receive = true;
                entry.receive_messages.extend(messages);
            }
        }
    }
    uses
}

/// The operations of one document, resolved to their channels' templates.
/// An operation whose channel is missing or has no address is an error: an
/// extension may bind to it, and nothing could be resolved for it.
fn operations_from_document(doc: &Document, path: &Path) -> anyhow::Result<OperationIndex> {
    let mut index = OperationIndex::new();
    for (key, operation) in &doc.operations {
        let RefOr::Item(operation) = operation else {
            continue;
        };
        let channel_key = operation
            .channel
            .local_key()
            .with_context(|| format!("operation '{key}' in {} has no channel", path.display()))?;
        let channel = doc
            .channels
            .get(&channel_key)
            .and_then(|c| resolve_channel(c, doc))
            .with_context(|| {
                format!(
                    "operation '{key}' in {} names unknown channel '{channel_key}'",
                    path.display()
                )
            })?;
        let address = channel.address().map(strip_role_suffix).with_context(|| {
            format!(
                "channel '{channel_key}' in {} has no address",
                path.display()
            )
        })?;
        let pattern =
            mqtt_topic_from_channel(channel).unwrap_or_else(|| wildcard_from_address(&address));
        let preferred: Vec<String> = operation
            .messages
            .iter()
            .filter_map(|r| r.local_key())
            .collect();
        let message = select_message(channel, doc, &preferred);
        let payload = message.and_then(payload_value);
        let parameter_schemas = match extract_params(&address).as_slice() {
            [param] => message
                .and_then(|m| m.extensions.as_ref())
                .and_then(|e| e.get(&format!("x-{param}-schema")))
                .and_then(Value::as_object)
                .map(|schemas| {
                    schemas
                        .iter()
                        .map(|(k, v)| (k.clone(), v.clone()))
                        .collect()
                })
                .unwrap_or_default(),
            _ => BTreeMap::new(),
        };
        index.insert(
            key.clone(),
            OperationDef {
                action: operation.action,
                address,
                pattern,
                document: path.display().to_string(),
                payload,
                parameter_schemas,
            },
        );
    }
    Ok(index)
}

/// A message's payload schema as the document declares it: the `$ref` kept
/// as a reference (so it can be matched against the extension's types), an
/// inline schema as its JSON.
fn payload_value(message: &Message) -> Option<Value> {
    match message.payload.as_ref()? {
        RefOr::Reference(reference) => Some(json!({"$ref": reference.reference})),
        RefOr::Item(schema) => serde_json::to_value(schema).ok(),
    }
}

/// The channel address without the trailing `:<Role>` (`:Publisher`,
/// `:Handler`) FastStream appends to name the operation kind; it is not part
/// of the topic path.
fn strip_role_suffix(address: &str) -> String {
    address
        .rsplit_once(':')
        .map_or(address, |(path, _role)| path)
        .to_string()
}

/// The publish targets of one document: the topic/pattern and payload schema
/// of every channel some application receives on.
fn publish_targets_from_document(
    doc: &Document,
    path: &Path,
    uses: &BTreeMap<String, ChannelUse>,
) -> anyhow::Result<Vec<PublishTargetDef>> {
    let mut targets: Vec<PublishTargetDef> = Vec::new();
    for (channel_name, channel_ref) in &doc.channels {
        let Some(channel_use) = uses.get(channel_name).filter(|u| u.receive) else {
            continue;
        };
        let channel = resolve_channel(channel_ref, doc).with_context(|| {
            format!(
                "unresolvable channel $ref '{}' in {}",
                channel_name,
                path.display()
            )
        })?;
        let Some(pattern) = mqtt_topic_from_channel(channel).or_else(|| {
            channel
                .address()
                .map(|a| wildcard_from_address(&strip_role_suffix(a)))
        }) else {
            continue;
        };
        let payload_schema = select_message(channel, doc, &channel_use.receive_messages)
            .and_then(|message| message.payload.as_ref())
            .and_then(|payload| resolve_payload_schema(payload, doc))
            .and_then(|schema| serde_json::to_value(schema).ok());
        if targets.iter().any(|t| t.pattern == pattern) {
            continue;
        }
        targets.push(PublishTargetDef {
            pattern,
            payload_schema,
        });
    }
    Ok(targets)
}

/// Read and parse every AsyncAPI document in `spec_dir` once, returning
/// `(file name, path, document)` for each. Non-JSON files and topic-metadata
/// files are skipped; unreadable or invalid `.json` files are an error —
/// see [`read_asyncapi_document`].
type SpecDocument = (String, PathBuf, Document, Option<Arc<Value>>);

fn spec_documents(spec_dir: &str) -> anyhow::Result<Vec<SpecDocument>> {
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
        .map(|(file_name, path)| {
            read_asyncapi_document(&path)
                .map(|(doc, components)| (file_name, path, doc, components))
        })
        .collect()
}

/// Load AsyncAPI 3.0.0 spec files from a directory in a single pass over the
/// spec directory, extracting both concrete topics and parametrized groups.
///
/// Consumers that only need one of the two should still use this loader and
/// ignore the other half, so each spec file is read exactly once.
/// A validator input: an MQTT topic (or wildcard pattern) and a self-contained
/// JSON Schema for its payloads. Self-contained means the schema carries its
/// document's `components` at the root, so `#/components/schemas/...` `$ref`s
/// still resolve when it's compiled on its own.
pub type ValidatorSpec = (String, Value);

pub struct LoadedSpecs {
    pub topics: Vec<TopicDef>,
    pub groups: Vec<TopicGroupDef>,
    pub object_types: Vec<ObjectTypeDef>,
    /// Validator inputs: concrete topics, then group patterns, then per-field
    /// topics, in that order, so a later exact-topic entry beats an earlier
    /// wildcard one at validation time.
    pub validators: Vec<ValidatorSpec>,
    /// Topics/patterns some described application receives on (channels with
    /// a `receive` operation): where the bridge may publish.
    pub publish_targets: Vec<PublishTargetDef>,
    /// Every operation of every document, for extensions that bind to one.
    pub operations: OperationIndex,
    /// The `x-mqtt-graphql` specification extension (views, mutations,
    /// metadata and lifecycles) merged across the documents that carry one,
    /// resolved against every document's operations; `None` when none does.
    /// See [`crate::extension`].
    pub extension: Option<GraphqlExtension>,
}

pub fn load_specs_and_groups(spec_dir: &str) -> anyhow::Result<LoadedSpecs> {
    let docs = spec_documents(spec_dir)?;
    let mut object_types: ObjectTypeRegistry = ObjectTypeRegistry::new();

    let mut topics: Vec<TopicDef> = Vec::new();
    let mut groups: Vec<TopicGroupDef> = Vec::new();
    let mut validators: Vec<ValidatorSpec> = Vec::new();
    let mut publish_targets: Vec<PublishTargetDef> = Vec::new();
    let mut operations = OperationIndex::new();
    let mut extension: Option<GraphqlExtension> = None;

    for (_, path, doc, components) in &docs {
        // Direction comes from the operations: the bridge subscribes to what
        // the described applications send and may publish where they receive.
        // One topic can be both (THRS's control and API sides are one document).
        let uses = channel_uses(doc);
        for (key, operation) in operations_from_document(doc, path)? {
            if operations.insert(key.clone(), operation).is_some() {
                anyhow::bail!("operation '{key}' is declared by more than one document");
            }
        }
        publish_targets.extend(publish_targets_from_document(doc, path, &uses)?);
        if let Some(doc_extension) = parse_extension(
            doc.extensions.as_ref(),
            components.as_deref(),
            &path.display().to_string(),
        )
        .with_context(|| format!("in {}", path.display()))?
        {
            extension
                .get_or_insert_with(GraphqlExtension::default)
                .merge(doc_extension)
                .with_context(|| format!("in {}", path.display()))?;
        }
        let doc_topics = topics_from_document(doc, path, &mut object_types, &uses)?;
        let doc_groups = groups_from_document(doc, path, &mut object_types, &uses)?;

        // Wrap each spec with this doc's raw components so `$ref`s resolve.
        // Topics and group patterns first, then per-field topics (which override
        // the group pattern via the exact-topic-first lookup in
        // `MqttSubscriber::validate_payload`).
        for t in &doc_topics {
            if let Some(schema) = &t.payload_schema {
                validators.push((t.topic.clone(), self_contained(schema, components)));
            }
        }
        for g in &doc_groups {
            if let Some(schema) = &g.payload_schema {
                validators.push((g.pattern.clone(), self_contained(schema, components)));
            }
        }
        for g in &doc_groups {
            for (topic, schema) in &g.field_schemas {
                validators.push((topic.clone(), self_contained(schema, components)));
            }
        }

        topics.extend(doc_topics);
        groups.extend(doc_groups);
    }

    info!(
        "Loaded {} topic(s), {} topic group(s), {} publish target(s) and {} composite object type(s) from {}",
        topics.len(),
        groups.len(),
        publish_targets.len(),
        object_types.len(),
        spec_dir
    );
    // The extension binds to operations of any loaded document, so it is
    // resolved once every document is in.
    if let Some(extension) = &mut extension {
        extension.resolve(&operations, &groups).with_context(|| {
            format!(
                "invalid {} extension in {spec_dir}",
                crate::extension::EXTENSION_KEY
            )
        })?;
        info!(
            "Loaded {} extension: {} view(s), {} mutation(s), {} lifecycle(s), {} metadata group(s)",
            crate::extension::EXTENSION_KEY,
            extension.views.len(),
            extension.mutation_count(),
            extension.lifecycles.len(),
            extension.metadata.len()
        );
    }
    Ok(LoadedSpecs {
        topics,
        groups,
        object_types: object_types.into_values().collect(),
        validators,
        publish_targets,
        operations,
        extension,
    })
}

/// Make a payload schema compilable on its own: put it under `allOf` and attach
/// the document's raw `components` at the root, so its `#/components/schemas/...`
/// `$ref`s resolve. Returned unchanged when there are no components (already
/// self-contained, e.g. in tests).
fn self_contained(schema: &Value, components: &Option<Arc<Value>>) -> Value {
    match components {
        Some(components) => json!({
            "allOf": [schema],
            "components": components.as_ref(),
        }),
        None => schema.clone(),
    }
}

/// Extract concrete topics from one document, erroring on unresolvable
/// channel references. Only channels some application sends on become
/// topics; a topic declared by several such channels is taken once.
fn topics_from_document(
    doc: &Document,
    path: &Path,
    object_types: &mut ObjectTypeRegistry,
    uses: &BTreeMap<String, ChannelUse>,
) -> anyhow::Result<Vec<TopicDef>> {
    if doc.channels.is_empty() {
        info!("File {} has no channels, skipping", path.display());
        return Ok(Vec::new());
    }

    let mut seen: BTreeSet<String> = BTreeSet::new();
    doc.channels
        .iter()
        .filter(|(channel_name, _)| uses.get(*channel_name).is_none_or(ChannelUse::subscribed))
        .map(|(channel_name, channel_ref)| {
            let channel = resolve_channel(channel_ref, doc).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' in {}",
                    channel_name,
                    path.display()
                )
            })?;
            let preferred = uses.get(channel_name).map(|u| u.send_messages.as_slice());
            Ok(
                topic_from_channel(channel_name, channel, doc, path, object_types, preferred)
                    .filter(|topic| seen.insert(topic.topic.clone())),
            )
        })
        .collect::<anyhow::Result<Vec<_>>>()
        .map(|topics| topics.into_iter().flatten().collect())
}

/// Extract parametrized groups from one document, erroring on unresolvable
/// channel references or malformed parametrized channels. Only channels some
/// application sends on become groups; a pattern declared by several such
/// channels is taken once.
fn groups_from_document(
    doc: &Document,
    path: &Path,
    object_types: &mut ObjectTypeRegistry,
    uses: &BTreeMap<String, ChannelUse>,
) -> anyhow::Result<Vec<TopicGroupDef>> {
    let mut seen: BTreeSet<String> = BTreeSet::new();
    doc.channels
        .iter()
        .filter(|(channel_name, _)| uses.get(*channel_name).is_none_or(ChannelUse::subscribed))
        .map(|(channel_name, channel_ref)| {
            let channel = resolve_channel(channel_ref, doc).with_context(|| {
                format!(
                    "unresolvable channel $ref '{}' in {}",
                    channel_name,
                    path.display()
                )
            })?;
            let preferred = uses.get(channel_name).map(|u| u.send_messages.as_slice());
            Ok(
                group_from_channel(channel_name, channel, doc, path, object_types, preferred)?
                    .filter(|group| seen.insert(group.pattern.clone())),
            )
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
    object_types: &mut ObjectTypeRegistry,
    preferred_messages: Option<&[String]>,
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

    let message = select_message(channel, doc, preferred_messages.unwrap_or_default());
    let (fields, payload_schema) = message_fields(message, doc, object_types);

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
    object_types: &mut ObjectTypeRegistry,
    preferred_messages: Option<&[String]>,
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
    let group = group_identity(&address).unwrap_or_else(|| address.clone());
    let pattern = binding_topic
        .filter(|topic| topic.contains('+') || topic.contains('#'))
        .unwrap_or_else(|| wildcard_from_address(&address));

    let message = select_message(channel, doc, preferred_messages.unwrap_or_default());
    let (fields, payload_schema) = message_fields(message, doc, object_types);
    let value_extensions = payload_schema
        .as_ref()
        .map(extensions_from_payload_schema)
        .unwrap_or_default();
    let field_schemas = field_schemas_for(message, channel, &params, &pattern);

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
        field_schemas,
        value_extensions,
        ttl_secs: ttl_for_channel(channel, doc),
    }))
}

/// Expand the `x-{param}-schema` extension of the message (or, for older
/// documents, of the channel) into a map of concrete topic to the schema that
/// topic carries. Only single-parameter groups (one `+` in the pattern) are
/// expanded: each value's schema is pinned to `pattern` with the `+` replaced
/// by that value. Empty when there's no such extension or the pattern has
/// more than one `+` (e.g. `power-tags/+/+`).
fn field_schemas_for(
    message: Option<&Message>,
    channel: &Channel,
    params: &[String],
    pattern: &str,
) -> BTreeMap<String, Value> {
    let mut out = BTreeMap::new();
    let [param] = params else { return out };
    if pattern.matches('+').count() != 1 {
        return out;
    }
    let name = format!("x-{param}-schema");
    let Some(schema_map) = message
        .and_then(|m| m.extensions.as_ref())
        .and_then(|e| e.get(&name))
        .or_else(|| channel.extensions.as_ref().and_then(|e| e.get(&name)))
        .and_then(Value::as_object)
    else {
        return out;
    };
    for (field_value, schema) in schema_map {
        let concrete_topic = pattern.replacen('+', field_value, 1);
        out.insert(concrete_topic, schema.clone());
    }
    out
}

/// Read and parse one file into an AsyncAPI 3.x `Document`, plus the file's raw
/// `components` value. We keep components verbatim so JSON Schema constraints
/// like `minimum`/`maximum` survive for the validators (the typed model drops
/// them), and so payload schemas' `#/components/schemas/...` `$ref`s resolve.
///
/// Errors when the file is unreadable, not valid JSON, lacks an `asyncapi`
/// version, or is not an AsyncAPI 3.x document — a spec directory is
/// expected to contain only loadable specs.
fn read_asyncapi_document(path: &Path) -> anyhow::Result<(Document, Option<Arc<Value>>)> {
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

    let components = spec_value.get("components").cloned().map(Arc::new);
    let doc = serde_json::from_value::<Document>(spec_value)
        .with_context(|| format!("parsing AsyncAPI document {}", path.display()))?;
    Ok((doc, components))
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
///
/// Strips the trailing `:<Role>` operation suffix first (like
/// [`group_identity`]). Otherwise the last segment of `.../{field}:Publisher` is
/// `{field}:Publisher`, which `param_name` doesn't see as a placeholder, so the
/// param gets dropped and per-field schema pinning
/// (`field_schemas_from_channel`) never fires.
fn extract_params(address: &str) -> Vec<String> {
    let address = address
        .rsplit_once(':')
        .map_or(address, |(path, _role)| path);
    address
        .split('/')
        .filter_map(param_name)
        .map(str::to_string)
        .collect()
}

/// Group identity of an address: all of its static segments, so that
/// `thrs/controller/{module}/parameters` and
/// `thrs/controller/{module}/manual-values` are distinct groups
/// (`thrs/controller/parameters`, `thrs/controller/manual-values`).
fn group_identity(address: &str) -> Option<String> {
    // Addresses end in `:<Role>` (`controller-state:Publisher`,
    // `{field}:Handler`) that names the AsyncAPI operation kind, not part
    // of the topic path, so strip it first or it leaks into the group name.
    let address = address
        .rsplit_once(':')
        .map_or(address, |(path, _role)| path);
    let segments: Vec<&str> = address
        .split('/')
        .filter(|segment| param_name(segment).is_none())
        .collect();
    (!segments.is_empty()).then(|| segments.join("/"))
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

/// Extract scalar fields + payload schema from one message of a channel.
fn message_fields(
    message: Option<&Message>,
    doc: &Document,
    object_types: &mut ObjectTypeRegistry,
) -> (Vec<FieldDef>, Option<Value>) {
    let Some(message) = message else {
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
            let fields = extract_fields_from_schema_or_multi(&schema_or_multi, doc, object_types);
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
    object_types: &mut ObjectTypeRegistry,
) -> Vec<FieldDef> {
    match schema_or_multi {
        SchemaOrMultiFormat::Schema(schema) => {
            extract_fields_from_schema(schema, doc, object_types)
        }
        SchemaOrMultiFormat::MultiFormat(mf) => {
            // Try to deserialize the raw schema value as a Schema
            if let Ok(schema) = serde_json::from_value::<Schema>(mf.schema.clone()) {
                extract_fields_from_schema(&schema, doc, object_types)
            } else {
                Vec::new()
            }
        }
        SchemaOrMultiFormat::Bool(_) => Vec::new(),
    }
}

fn extract_fields_from_schema(
    schema: &Schema,
    doc: &Document,
    object_types: &mut ObjectTypeRegistry,
) -> Vec<FieldDef> {
    // Groups with a per-{field} payload (adsorption etc, where one field
    // is a TemperatureSensor and another a Valve) come through as a
    // top-level `anyOf` of branch schemas instead of one `properties` map.
    // Union all the branches into one wide column set. Each topic only
    // fills in its own branch's columns, the rest stay null (group_row in
    // graphql.rs).
    if schema.properties.is_empty() {
        if let Some(any_of) = &schema.any_of {
            return extract_fields_from_any_of(any_of, doc, object_types);
        }
    }

    // Fields colliding after lowerCamel sanitization are not tolerated here:
    // they surface as errors from `validate_topics` instead.
    schema
        .properties
        .iter()
        .filter_map(|(name, subschema)| {
            let graphql_type = field_graphql_type(subschema, doc, object_types)?;
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

/// Resolve one property's GraphQL type. Tries, in order: a `Stamped`
/// envelope (`{ Value: <T>, TimeStamp: <string> }`; THRS wraps basically
/// every value in one of these), encoded as `"Stamped:<T>"` and picked up by
/// `graphql_type_ref` in graphql.rs and turned into the shared `Stamped<T>`
/// type so we keep the timestamp instead of throwing it away); a plain
/// scalar; and finally a composite object ref (`PidControllerValues` and
/// friends) via `resolve_object_type`, same as before.
fn field_graphql_type(
    subschema: &SubSchema,
    doc: &Document,
    object_types: &mut ObjectTypeRegistry,
) -> Option<String> {
    if let Some(inner) = stamped_value_subschema(subschema, doc) {
        let inner_type = graphql_type_for_subschema(&inner, doc)?;
        return Some(format!("Stamped:{inner_type}"));
    }
    if let Some(scalar) = graphql_type_for_subschema(subschema, doc) {
        return Some(scalar);
    }
    resolve_object_type(subschema, doc, object_types)
}

/// True if `subschema` is a Stamped envelope (properties exactly
/// `{Value, TimeStamp}`). Returns its `Value` subschema if so.
fn stamped_value_subschema(subschema: &SubSchema, doc: &Document) -> Option<SubSchema> {
    let schema = resolve_subschema_to_schema(subschema, doc)?;
    let keys: BTreeSet<&str> = schema.properties.keys().map(String::as_str).collect();
    if keys != BTreeSet::from(["Value", "TimeStamp"]) {
        return None;
    }
    schema.properties.get("Value").cloned()
}

/// Resolve `subschema` as a named composite object (not a scalar, not
/// Stamped) and register it once in `object_types`, recursing into its own
/// properties. Returns the `"Object:<Name>"` marker for `graphql_type_ref`,
/// or `None` if it has no title or no fields (e.g. `AdsorptionControllerState`
/// is legitimately empty for modules without PID/tank controllers, and you
/// can't make a GraphQL type with zero fields, so that field just gets
/// skipped).
///
/// Inserts a placeholder before recursing so a self-referential schema
/// can't loop forever.
fn resolve_object_type(
    subschema: &SubSchema,
    doc: &Document,
    object_types: &mut ObjectTypeRegistry,
) -> Option<String> {
    let schema = resolve_subschema_to_schema(subschema, doc)?;
    if schema.properties.is_empty() {
        return None;
    }
    let name = schema.title.clone()?;
    if !object_types.contains_key(&name) {
        object_types.insert(
            name.clone(),
            ObjectTypeDef {
                name: name.clone(),
                fields: Vec::new(),
            },
        );
        let fields = extract_fields_from_schema(&schema, doc, object_types);
        object_types.get_mut(&name).expect("just inserted").fields = fields;
    }
    Some(format!("Object:{name}"))
}

/// Union the properties of every `anyOf` branch into one field list --
/// first occurrence of a field name wins. Branches with an unresolvable
/// `$ref` are just skipped.
///
/// Two branches sharing a field name with the same type is fine (e.g.
/// `Setpoint` on both `Valve` and `Pump`). Same name, different type, or
/// two different names colliding after sanitization: that's a real
/// conflict and `validate_topic_fields` catches it later, not silently
/// dropped here.
fn extract_fields_from_any_of(
    any_of: &[SubSchema],
    doc: &Document,
    object_types: &mut ObjectTypeRegistry,
) -> Vec<FieldDef> {
    let mut merged: BTreeMap<String, FieldDef> = BTreeMap::new();
    for sub in any_of {
        let Some(branch_schema) = resolve_subschema_to_schema(sub, doc) else {
            continue;
        };
        for field in extract_fields_from_schema(&branch_schema, doc, object_types) {
            merged.entry(field.name.clone()).or_insert(field);
        }
    }
    merged.into_values().collect()
}

/// Resolve a subschema (inline or `$ref`) to its concrete `Schema`. Same
/// resolution as `graphql::graphql_type_for_subschema`, just returns the
/// schema itself instead of a mapped scalar type.
fn resolve_subschema_to_schema(sub: &SubSchema, doc: &Document) -> Option<Schema> {
    match sub {
        SubSchema::Bool(_) => None,
        SubSchema::Schema(boxed) => match boxed.as_ref() {
            RefOr::Item(schema) => Some(schema.clone()),
            RefOr::Reference(reference) => {
                match resolve_ref_to_entry(reference, "schemas", &doc.components.as_ref()?.schemas)?
                    .item()?
                {
                    SchemaOrMultiFormat::Schema(s) => Some((**s).clone()),
                    SchemaOrMultiFormat::MultiFormat(mf) => {
                        serde_json::from_value(mf.schema.clone()).ok()
                    }
                    SchemaOrMultiFormat::Bool(_) => None,
                }
            }
        },
    }
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

/// Parse an `x-ttl` string: plain seconds (`"300"`), a suffixed form
/// (`"30s"`, `"5m"`, `"1h"`) or `"unbounded"` (the value never expires).
/// Logs and returns `None` on unsupported values.
fn parse_ttl_str(s: &str) -> Option<u64> {
    if let Ok(n) = s.parse::<u64>() {
        return Some(n);
    }
    if s == "unbounded" {
        return Some(crate::config::TTL_UNBOUNDED_SECS);
    }
    let (num, mult) = if let Some(num) = s.strip_suffix('h') {
        (num, 3600)
    } else if let Some(num) = s.strip_suffix('m') {
        (num, 60)
    } else if let Some(num) = s.strip_suffix('s') {
        (num, 1)
    } else {
        warn!(
            "Unsupported x-ttl value '{s}' (expected seconds, '30s', '5m', '1h' or 'unbounded') — using default"
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
        Ok(load_specs_and_groups(dir.to_str().unwrap())?.topics)
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
    fn test_extract_params_strips_operation_role_suffix() {
        // Channel addresses end in a `:<Role>` suffix (`{field}:Publisher`).
        // Without stripping it the last placeholder reads as `{field}:Publisher`,
        // not a param, so the list comes back empty and per-field pinning never
        // fires (regression: group payloads then only hit the anyOf union).
        assert_eq!(
            extract_params("simulation/500000-thrs/thrusters/{field}:Publisher"),
            vec!["field".to_string()],
        );
        // Mid-address params with a suffix, and addresses without one, both work.
        assert_eq!(
            extract_params("thrs/controller/{module}/parameters:Publisher"),
            vec!["module".to_string()],
        );
        assert_eq!(
            extract_params("power-tags/{panel}/{slug}"),
            vec!["panel".to_string(), "slug".to_string()],
        );
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
        let fields = extract_fields_from_schema(&schema, &doc, &mut ObjectTypeRegistry::new());
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

    /// A channel with only a `receive` operation is a publish target, not a
    /// query topic; one with both directions is both, once each. Channels
    /// without operations are query topics (older specs).
    #[test]
    fn test_operations_decide_direction() {
        fn channel(address: &str, topic: &str) -> Value {
            json!({
                "address": address,
                "messages": {"Message": {"payload": {"type": "object", "properties": {"x": {"type": "number"}}}}},
                "bindings": {"mqtt": {"topic": topic, "qos": 0, "retain": false, "bindingVersion": "0.2.0"}}
            })
        }
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "channels": {
                "a.b:Publisher": channel("a/b:Publisher", "a/b"),
                "a.b:Handler": channel("a/b:Handler", "a/b"),
                "a.c:Handler": channel("a/c:Handler", "a/c"),
                "legacy": channel("a/d", "a/d"),
                "g.{p}.x:Publisher": channel("g/{p}/x:Publisher", "g/+/x"),
                "g.{p}.x:Handler": channel("g/{p}/x:Handler", "g/+/x")
            },
            "operations": {
                "a.b:Publisher": {"action": "send", "channel": {"$ref": "#/channels/a.b:Publisher"}},
                "a.b:HandlerSubscribe": {"action": "receive", "channel": {"$ref": "#/channels/a.b:Handler"}},
                "a.c:HandlerSubscribe": {"action": "receive", "channel": {"$ref": "#/channels/a.c:Handler"}},
                "g.{p}.x:Publisher": {"action": "send", "channel": {"$ref": "#/channels/g.{p}.x:Publisher"}},
                "g.{p}.x:HandlerSubscribe": {"action": "receive", "channel": {"$ref": "#/channels/g.{p}.x:Handler"}}
            }
        });
        let dir = std::env::temp_dir().join("mqtt-graphql-test-directions");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("t.json"), spec.to_string()).unwrap();
        let loaded = load_specs_and_groups(dir.to_str().unwrap()).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        let mut topics: Vec<&str> = loaded.topics.iter().map(|t| t.topic.as_str()).collect();
        topics.sort();
        assert_eq!(topics, vec!["a/b", "a/d"]);
        assert_eq!(loaded.groups.len(), 1);
        assert_eq!(loaded.groups[0].pattern, "g/+/x");
        let mut targets: Vec<&str> = loaded
            .publish_targets
            .iter()
            .map(|t| t.pattern.as_str())
            .collect();
        targets.sort();
        assert_eq!(targets, vec!["a/b", "a/c", "g/+/x"]);
        assert!(loaded.publish_targets[0].payload_schema.is_some());

        let op = &loaded.operations["g.{p}.x:HandlerSubscribe"];
        assert_eq!(op.action, OperationAction::Receive);
        assert_eq!(op.address, "g/{p}/x");
        assert_eq!(op.pattern, "g/+/x");
        let params = BTreeMap::from([("p".to_string(), "one".to_string())]);
        assert_eq!(op.topic(&params).unwrap(), "g/one/x");
        assert!(op.topic(&BTreeMap::new()).is_err());
        let extra = BTreeMap::from([
            ("p".to_string(), "one".to_string()),
            ("q".to_string(), "2".to_string()),
        ]);
        assert!(op.topic(&extra).is_err());
        assert_eq!(
            loaded.operations["a.b:Publisher"]
                .topic(&BTreeMap::new())
                .unwrap(),
            "a/b"
        );
    }

    /// With one channel per address, each direction's operation names the
    /// message it carries: the query side takes the sent payload (and its
    /// per-value schemas), the publish target the received one.
    #[test]
    fn test_operation_messages_select_the_payload_per_direction() {
        let spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "channels": {
                "ctl.mode": {
                    "address": "ctl/{module}/mode",
                    "parameters": {"module": {"enum": ["a"]}},
                    "messages": {
                        "sent": {"payload": {"type": "object", "properties": {"Mode": {"type": "string"}}},
                                 "x-module-schema": {"a": {"type": "object", "properties": {"Mode": {"type": "string"}}}}},
                        "received": {"payload": {"type": "object", "properties": {"Wrapped": {"type": "number"}}}}
                    }
                }
            },
            "operations": {
                "ctl.mode.send": {"action": "send", "channel": {"$ref": "#/channels/ctl.mode"},
                                  "messages": [{"$ref": "#/channels/ctl.mode/messages/sent"}]},
                "ctl.mode.receive": {"action": "receive", "channel": {"$ref": "#/channels/ctl.mode"},
                                     "messages": [{"$ref": "#/channels/ctl.mode/messages/received"}]}
            }
        });
        let dir = std::env::temp_dir().join("mqtt-graphql-test-messages");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("t.json"), spec.to_string()).unwrap();
        let loaded = load_specs_and_groups(dir.to_str().unwrap()).unwrap();
        let _ = std::fs::remove_dir_all(&dir);

        assert_eq!(loaded.groups.len(), 1);
        let group = &loaded.groups[0];
        assert_eq!(group.pattern, "ctl/+/mode");
        assert_eq!(group.fields[0].name, "Mode");
        assert_eq!(
            group.field_schemas.keys().collect::<Vec<_>>(),
            vec!["ctl/a/mode"]
        );
        let target = &loaded.publish_targets[0];
        assert_eq!(target.pattern, "ctl/+/mode");
        assert!(target.payload_schema.as_ref().unwrap()["properties"]["Wrapped"].is_object());
        assert_eq!(
            loaded.operations["ctl.mode.send"].address,
            "ctl/{module}/mode"
        );
    }

    #[test]
    fn test_topic_matches() {
        assert!(topic_matches("a/b", "a/b"));
        assert!(!topic_matches("a/b", "a/b/c"));
        assert!(topic_matches("a/+/c", "a/x/c"));
        assert!(!topic_matches("a/+/c", "a/x/y/c"));
        assert!(topic_matches("a/#", "a/x/y"));
        assert!(!topic_matches("a/+", "b/x"));
    }

    /// A document carrying the `x-mqtt-graphql` root extension yields it,
    /// resolved against the document's operations, next to its channels; a
    /// binding to an operation the document lacks fails the load like any
    /// invalid spec.
    #[test]
    fn test_load_specs_reads_graphql_extension() {
        let mut spec = json!({
            "asyncapi": "3.0.0",
            "info": {"title": "THRS", "version": "1.0.0"},
            "channels": {
                "ctl.parameters": {
                    "address": "ctl/{module}/parameters",
                    "parameters": {"module": {"enum": ["thrusters"]}},
                    "messages": {"message": {"payload": {"$ref": "#/components/schemas/Parameters"}}}
                },
                "ctl.parameters.set": {
                    "address": "ctl/{module}/parameters/set",
                    "parameters": {"module": {"enum": ["thrusters"]}},
                    "messages": {"message": {"payload": {"$ref": "#/components/schemas/Parameters"}}}
                }
            },
            "operations": {
                "ctl.parameters.send": {"action": "send", "channel": {"$ref": "#/channels/ctl.parameters"}},
                "ctl.parameters.set.receive": {"action": "receive", "channel": {"$ref": "#/channels/ctl.parameters.set"}}
            },
            "components": {"schemas": {"Parameters": {
                "type": "object", "properties": {"CoolingFlow": {"type": "number"}}}}},
            "x-mqtt-graphql": {
                "version": 2,
                "types": {"ThrustersParametersType": {"schema": {"$ref": "#/components/schemas/Parameters"}}},
                "views": [{
                    "gql": "modules", "typeName": "ControlModules",
                    "members": [{
                        "gql": "thrusters", "typeName": "ThrustersControlModule",
                        "sections": [{"kind": "object", "gql": "parameters", "typeName": "ThrustersParametersType",
                            "operation": {"operation": "ctl.parameters.send", "parameters": {"module": "thrusters"}}}],
                        "mutations": [{"gql": "thrustersParameterSetCoolingFlow", "kind": "setField",
                            "argName": "value", "key": "CoolingFlow", "returns": "parameters",
                            "state": {"operation": "ctl.parameters.send", "parameters": {"module": "thrusters"}},
                            "target": {"operation": "ctl.parameters.set.receive", "parameters": {"module": "thrusters"}}}]
                    }]
                }],
                "metadata": [{"operation": "ctl.parameters.send", "instances": {"thrusters": {"module": "thrusters"}}}]
            }
        });
        let dir = std::env::temp_dir().join("mqtt-graphql-test-x-mqtt-graphql");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("thrs-control.json");
        std::fs::write(&path, spec.to_string()).unwrap();
        let loaded = load_specs_and_groups(dir.to_str().unwrap()).unwrap();
        let extension = loaded.extension.expect("x-mqtt-graphql extension");
        let mutation = &extension.views[0].members[0].mutations[0];
        assert_eq!(mutation.arg_type, "Float");
        assert_eq!(mutation.state_topic, "ctl/thrusters/parameters");
        assert_eq!(mutation.set_topic, "ctl/thrusters/parameters/set");
        assert_eq!(extension.metadata_files[0].group, "ctl/parameters");
        assert_eq!(
            extension.metadata_files[0].topics[0].topic,
            "ctl/thrusters/parameters"
        );

        spec["x-mqtt-graphql"]["views"][0]["members"][0]["mutations"][0]["target"]["operation"] =
            json!("nope");
        std::fs::write(&path, spec.to_string()).unwrap();
        let err = load_specs_and_groups(dir.to_str().unwrap())
            .err()
            .expect("an unresolvable binding must fail the load");
        assert!(
            format!("{err:#}").contains("unknown operation 'nope'"),
            "{err:#}"
        );
        let _ = std::fs::remove_dir_all(&dir);
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
        let fields = extract_fields_from_schema(&schema, &doc, &mut ObjectTypeRegistry::new());
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
        let fields = extract_fields_from_schema(&schema, &doc, &mut ObjectTypeRegistry::new());
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
        assert_eq!(
            ttl_from_value(Some(&json!("unbounded"))),
            Some(crate::config::TTL_UNBOUNDED_SECS)
        );
        assert_eq!(ttl_from_value(Some(&json!(-1.5))), None);
        assert_eq!(ttl_from_value(Some(&json!(true))), None);
        assert_eq!(ttl_from_value(None), None);
    }
}
