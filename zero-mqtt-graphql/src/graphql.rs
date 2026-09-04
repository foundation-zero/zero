//! GraphQL schema for MQTT topics, topic groups, and buckets.
//!
//! # Terminology
//! - **Topic** (`TopicDef`): a single concrete MQTT topic with a fixed address
//!   and no wildcards, e.g. `termodinamica/compressor/temperature`. Each topic
//!   maps to one sanitized GraphQL query field returning its cached payload.
//! - **Group** (`TopicGroupDef`): a parametrized topic family declared by one
//!   AsyncAPI channel whose address contains `{param}` placeholders, e.g.
//!   `power-tags/{panel}/{slug}` with MQTT pattern `power-tags/+/+`. A group
//!   is enumerated by a `*-metadata.json` file listing its concrete topics and
//!   static attributes; the schema exposes one list query `<group>: [<Group>Topic]`
//!   (e.g. `powerTags: [PowerTagsTopic]`) whose rows merge that static metadata
//!   with live values from the cache.
//! - **Bucket**: a partition of a group's rows by the distinct value of the
//!   `group_by` metadata attribute declared in the group's metadata file. For
//!   example `group_by: "panel"` buckets `power-tags` rows into buckets `10P1`,
//!   `10P2`, … Each bucket exposes `{ id, <group>: [GroupTopic] }` and the
//!   schema exposes `<stem>Buckets: [Bucket]` (all buckets) and
//!   `<stem>Bucket(id: String): Bucket` (single bucket by id).

use std::collections::{BTreeMap, BTreeSet};
use std::iter::once;
use std::sync::Arc;

use async_graphql::dynamic::*;
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use log::warn;
use roas_asyncapi::common::reference::RefOr;
use roas_asyncapi::v3_0::schema::{
    Schema as AsyncApiSchema, SchemaOrMultiFormat, SchemaType, SubSchema,
};
use roas_asyncapi::v3_0::Document;
use serde_json::Value as JsonValue;

use crate::asyncapi::{FieldDef, TopicDef, TopicGroupDef};
use crate::cache::TopicCache;
use crate::metadata::{metadata_by_topic, MetadataByTopic, MetadataFile};
use crate::naming::*;

/// A group's rows partitioned into buckets by the `group_by` metadata
/// attribute: bucket id → `(topic, metadata)` pairs.
type GroupedRows = BTreeMap<String, Vec<(String, BTreeMap<String, JsonValue>)>>;

/// Build a dynamic GraphQL schema from topic definitions and the cache.
///
/// Sanitizes topic names to valid GraphQL identifiers and validates that no
/// two topics collide after sanitization. Returns an error if any sanitized
/// name is empty, duplicates another topic, or collides with a reserved
/// GraphQL name. Topics without scalar fields are not registered as query
/// types but stay visible through the `topics` introspection field.
///
/// Each topic group (a parametrized channel such as `power-tags/{panel}/{slug}`)
/// with at least one metadata entry gains a `<group>: [<Group>Topic]` list
/// query whose rows merge static metadata (`metadata { … }`) with live values
/// from the cache (`values { … }`). A group whose metadata file declares
/// `group_by: "<attr>"` additionally gains bucket queries
/// `<stem>Buckets` / `<stem>Bucket(id)` partitioning its rows by that
/// attribute. Concrete topics
/// annotated in the metadata store gain an additive `metadata { … }` field on
/// their own object type.
pub fn build_schema(
    topics: &[TopicDef],
    cache: Arc<TopicCache>,
    groups: &[TopicGroupDef],
    metadata: &[MetadataFile],
) -> anyhow::Result<Schema> {
    validate_topics(topics)?;

    let metadata_store = Arc::new(metadata_by_topic(metadata));
    let mut used_query_fields = initial_used_query_names(topics);

    let mut query = Object::new("Query");
    query = query.field(topics_introspection_field(topics));

    // Concrete topic objects and their query fields. Each query field returns
    // the topic's whole cached payload object; its scalar subfields project
    // from that object (see `payload_field`).
    let concrete = register_concrete_topics(topics, &cache, &metadata_store);
    let ConcreteTopics {
        objects,
        metadata_types,
        query_fields,
    } = concrete;
    for field in query_fields {
        query = query.field(field);
    }

    // Group list queries: one merged list per parametrized channel whose
    // domain ships a metadata file (which enumerates the concrete topics).
    let (query_fields, group_objects): (Vec<_>, Vec<_>) = groups
        .iter()
        .map(|group| register_group_queries(group, metadata, &mut used_query_fields, &cache))
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .map(|parts| (parts.query_fields, parts.objects))
        .unzip();
    query = query_fields
        .into_iter()
        .flatten()
        .fold(query, Object::field);

    finish_schema(
        query,
        group_objects.into_iter().flatten().collect(),
        objects,
        metadata_types,
    )
}

/// The read-only `topics: [String]` introspection field listing every topic.
fn topics_introspection_field(topics: &[TopicDef]) -> Field {
    let topic_list: Vec<String> = topics.iter().map(|t| t.topic.clone()).collect();
    Field::new("topics", TypeRef::named_list("String"), move |_ctx| {
        let names = topic_list.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let values: Vec<GraphQlValue> = names.into_iter().map(GraphQlValue::String).collect();
            Ok(Some(GraphQlValue::List(values)))
        })
    })
}

/// Query names already claimed before any group registers: every sanitized
/// topic name plus the built-in `topics` field.
fn initial_used_query_names(topics: &[TopicDef]) -> BTreeSet<String> {
    topics
        .iter()
        .map(|t| sanitize_to_graphql_name(&t.topic))
        .chain(std::iter::once("topics".to_string()))
        .collect()
}

/// The `<Topic>Metadata` object exposing one concrete topic's static
/// attributes as projected scalar fields.
fn concrete_metadata_object(type_name: &str, meta_map: &BTreeMap<String, JsonValue>) -> Object {
    let mut meta_obj = Object::new(type_name);
    for (key, value) in meta_map {
        meta_obj = meta_obj.field(row_projection_field(
            &sanitize_to_graphql_name(key),
            graphql_scalar_for_value(value),
        ));
    }
    meta_obj
}

/// Assemble the final schema from the query object plus all supporting
/// object types (group objects, per-topic metadata objects, topic payloads).
fn finish_schema(
    query: Object,
    group_objects: Vec<Object>,
    concrete_objects: Vec<Object>,
    metadata_types: Vec<(String, BTreeMap<String, JsonValue>)>,
) -> anyhow::Result<Schema> {
    let schema_builder = Schema::build(query.type_name(), None, None).register(query);
    let schema_builder = group_objects
        .into_iter()
        .chain(concrete_objects)
        .chain(
            metadata_types
                .into_iter()
                .map(|(type_name, meta_map)| concrete_metadata_object(&type_name, &meta_map)),
        )
        .fold(schema_builder, |builder, object| builder.register(object));

    Ok(schema_builder.finish()?)
}

/// Schema contributions of the concrete (non-grouped) topics.
#[derive(Default)]
struct ConcreteTopics {
    /// `<Topic>` payload objects, one per topic with scalar fields.
    objects: Vec<Object>,
    /// `(type name, metadata)` pairs used to build `<Topic>Metadata` objects.
    metadata_types: Vec<(String, BTreeMap<String, JsonValue>)>,
    /// Query fields returning each topic's whole cached payload.
    query_fields: Vec<Field>,
}

/// Topics eligible for a queryable payload object: those with fields.
fn queryable_topics(topics: &[TopicDef]) -> impl Iterator<Item = &TopicDef> {
    topics
        .iter()
        .filter(|topic_def| !topic_def.fields.is_empty())
}

/// `(type name, metadata)` pair for a topic annotated with non-empty
/// metadata in the store.
fn metadata_type(
    topic_def: &TopicDef,
    metadata_store: &Arc<MetadataByTopic>,
) -> Option<(String, BTreeMap<String, JsonValue>)> {
    let (_, meta_map) = metadata_store.get(&topic_def.topic)?;
    (!meta_map.is_empty()).then(|| {
        (
            format!("{}Metadata", sanitize_to_graphql_name(&topic_def.topic)),
            meta_map.clone(),
        )
    })
}

/// Build the `<Topic>` object types and cached-payload query fields for
/// every concrete topic, plus an additive `metadata { … }` field for topics
/// annotated in the metadata store.
fn register_concrete_topics(
    topics: &[TopicDef],
    cache: &Arc<TopicCache>,
    metadata_store: &Arc<MetadataByTopic>,
) -> ConcreteTopics {
    ConcreteTopics {
        objects: queryable_topics(topics)
            .map(|topic_def| topic_object(topic_def, metadata_store))
            .collect(),
        metadata_types: queryable_topics(topics)
            .filter_map(|topic_def| metadata_type(topic_def, metadata_store))
            .collect(),
        query_fields: queryable_topics(topics)
            .map(|topic_def| {
                topic_query_field(
                    &topic_def.topic,
                    &sanitize_to_graphql_name(&topic_def.topic),
                    cache,
                )
            })
            .collect(),
    }
}

/// One concrete topic's `<Topic>` payload object, plus the additive
/// `metadata { … }` field when the topic is annotated in the metadata store.
fn topic_object(topic_def: &TopicDef, metadata_store: &Arc<MetadataByTopic>) -> Object {
    let type_name = sanitize_to_graphql_name(&topic_def.topic);
    let object = topic_def
        .fields
        .iter()
        .map(payload_field)
        .fold(Object::new(type_name.as_str()), |obj, field| {
            obj.field(field)
        });

    match metadata_type(topic_def, metadata_store) {
        Some((meta_type_name, _)) => object.field(metadata_field(
            &topic_def.topic,
            &meta_type_name,
            metadata_store,
        )),
        None => object,
    }
}

/// The `<Topic>` query field: resolves to the topic's whole cached MQTT
/// payload object. The object's scalar subfields project from this value
/// (see [`payload_field`]), so the payload is read from the cache exactly
/// once per query.
fn topic_query_field(topic: &str, type_name: &str, cache: &Arc<TopicCache>) -> Field {
    let obj_ref = TypeRef::named(type_name);
    let topic = topic.to_string();
    let cache_for_query = cache.clone();
    Field::new(type_name, obj_ref, move |_ctx| {
        let val = cache_for_query.get(&topic);
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(val.map(|json_val| json_to_graphql_value(&json_val)))
        })
    })
}

/// One scalar payload field on a `<Topic>` object: projects the raw field
/// name from the object value returned by [`topic_query_field`].
fn payload_field(field: &FieldDef) -> Field {
    let field_name = sanitize_to_graphql_name(&field.name);
    let raw_name = Name::new(field.name.clone());
    Field::new(
        field_name,
        graphql_type_ref(&field.graphql_type),
        move |ctx| {
            let raw_name = raw_name.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let parent = ctx.parent_value.try_to_value()?;
                let value = match parent {
                    GraphQlValue::Object(map) => {
                        map.get(&raw_name).cloned().unwrap_or(GraphQlValue::Null)
                    }
                    _ => GraphQlValue::Null,
                };
                Ok(Some(FieldValue::value(value)))
            })
        },
    )
}

/// The additive `metadata` field exposing a concrete topic's static
/// attributes from the metadata store.
fn metadata_field(
    topic: &str,
    meta_type_name: &str,
    metadata_store: &Arc<MetadataByTopic>,
) -> Field {
    let store = metadata_store.clone();
    let topic = topic.to_string();
    Field::new("metadata", TypeRef::named(meta_type_name), move |_ctx| {
        let store = store.clone();
        let topic = topic.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let value = match store.get(&topic) {
                Some((_, meta)) => json_to_graphql_value(&JsonValue::Object(
                    meta.iter()
                        .map(|(key, value)| (sanitize_to_graphql_name(key), value.clone()))
                        .collect(),
                )),
                None => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// Schema contributions of one topic group.
struct GroupSchemaParts {
    /// The group's supporting object types plus its optional bucket type.
    objects: Vec<Object>,
    /// The list query field plus optional grouped-by query fields.
    query_fields: Vec<Field>,
}

/// A group's metadata-file entries as `(topic, metadata)` pairs.
fn collect_group_entries(
    metadata: &[MetadataFile],
    group_id: &str,
) -> Vec<(String, BTreeMap<String, JsonValue>)> {
    metadata
        .iter()
        .filter(|file| file.group == group_id)
        .flat_map(|file| {
            file.topics
                .iter()
                .map(|entry| (entry.topic.clone(), entry.metadata.clone()))
        })
        .collect()
}

/// Sanitize a group id into a fresh query field name, rejecting empty,
/// reserved, or already-claimed names.
fn claim_group_query_name(
    group: &TopicGroupDef,
    used_query_fields: &mut BTreeSet<String>,
) -> anyhow::Result<String> {
    let query_field_name = sanitize_to_graphql_name(&group.group);
    if query_field_name.is_empty()
        || is_reserved_name(&query_field_name)
        || !used_query_fields.insert(query_field_name.clone())
    {
        anyhow::bail!(
            "topic group '{}' resolves to a reserved or duplicate query name '{}'",
            group.group,
            query_field_name
        );
    }
    Ok(query_field_name)
}

/// Union of a group's sanitized metadata keys minus the reserved `values`
/// key — occupied by the live-field descriptors, so a static attribute of
/// that name would panic on duplicate field registration. Returns `None`
/// when the group has no metadata to project.
fn group_metadata_fields(
    group: &TopicGroupDef,
    entries: &[(String, BTreeMap<String, JsonValue>)],
) -> anyhow::Result<Option<Vec<(String, TypeRef)>>> {
    let fields = union_metadata_fields(entries);
    if fields.is_empty() {
        warn!(
            "Topic group '{}' metadata is empty — no list query exposed",
            group.group
        );
        return Ok(None);
    }
    if fields.iter().any(|(name, _)| name == "values") {
        anyhow::bail!(
            "topic group '{}' metadata key 'values' is reserved",
            group.group
        );
    }
    Ok(Some(fields))
}

/// A group's supporting object types, derived from its Pascal-case stem.
fn build_group_objects(
    pascal: &str,
    metadata_fields: &[(String, TypeRef)],
    group: &TopicGroupDef,
) -> Vec<Object> {
    let item_type = format!("{pascal}Topic");
    let meta_type = format!("{pascal}Metadata");
    let values_type = format!("{pascal}Values");
    let value_meta_type = format!("{pascal}ValueMeta");

    let item_obj = [
        ("topic", TypeRef::named(TypeRef::STRING)),
        ("metadata", TypeRef::named(meta_type.as_str())),
        ("values", TypeRef::named(values_type.as_str())),
    ]
    .into_iter()
    .map(|(name, type_ref)| row_projection_field(name, type_ref))
    .fold(Object::new(item_type.as_str()), |obj, field| {
        obj.field(field)
    });

    let meta_obj = metadata_fields
        .iter()
        .map(|(name, type_ref)| row_projection_field(name, type_ref.clone()))
        .chain(once(row_projection_field(
            "values",
            TypeRef::named_list(value_meta_type.as_str()),
        )))
        .fold(Object::new(meta_type.as_str()), |obj, field| {
            obj.field(field)
        });

    let values_obj = group
        .fields
        .iter()
        .map(|field| {
            row_projection_field(
                &sanitize_to_graphql_name(&field.name),
                graphql_type_ref(&field.graphql_type),
            )
        })
        .fold(Object::new(values_type.as_str()), |obj, field| {
            obj.field(field)
        });

    let value_meta_obj = value_meta_descriptor_fields(group)
        .fold(Object::new(value_meta_type.as_str()), |obj, field| {
            obj.field(field)
        });

    vec![item_obj, meta_obj, values_obj, value_meta_obj]
}

/// Union of a group's collected `x-*` extension keys across all its payload
/// fields, in stable order.
fn extension_keys(group: &TopicGroupDef) -> Vec<String> {
    group
        .value_extensions
        .values()
        .flat_map(|extensions| extensions.keys().cloned())
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

/// Descriptor fields for the `<Group>ValueMeta` object: the reserved `name`
/// plus every collected `x-*` schema extension (e.g. `unit`) as a string
/// field.
fn value_meta_descriptor_fields(group: &TopicGroupDef) -> impl Iterator<Item = Field> + '_ {
    let group_id = group.group.clone();
    once(row_projection_field("name", TypeRef::named(TypeRef::STRING))).chain(
        extension_keys(group)
            .into_iter()
            .filter_map(move |key| {
                let sanitized = sanitize_to_graphql_name(&key);
                if sanitized.is_empty() {
                    warn!(
                        "Skipping group '{group_id}' value extension 'x-{key}' with empty GraphQL name"
                    );
                    return None;
                }
                if sanitized == "name" {
                    warn!(
                        "Group '{group_id}' value extension 'x-{key}' collides with the reserved 'name' descriptor, skipping"
                    );
                    return None;
                }
                Some(row_projection_field(
                    &sanitized,
                    TypeRef::named(TypeRef::STRING),
                ))
            }),
    )
}

/// A row's bucket id for the `group_by` attribute, defaulting to
/// `"unknown"` when absent or not a string.
fn bucket_attribute<'a>(meta: &'a BTreeMap<String, JsonValue>, group_by: &'a str) -> &'a str {
    meta.get(group_by)
        .and_then(JsonValue::as_str)
        .unwrap_or("unknown")
}

/// Bucket a group's rows by their `group_by` attribute value; rows without
/// it land in the `"unknown"` bucket.
fn bucket_rows_by(
    entries: &[(String, BTreeMap<String, JsonValue>)],
    group_by: &str,
) -> GroupedRows {
    entries
        .iter()
        .map(|(_, meta)| bucket_attribute(meta, group_by))
        .collect::<BTreeSet<_>>()
        .into_iter()
        .map(|attribute| {
            let rows = entries
                .iter()
                .filter(|(_, meta)| bucket_attribute(meta, group_by) == attribute)
                .map(|(topic, meta)| (topic.clone(), meta.clone()))
                .collect();
            (attribute.to_string(), rows)
        })
        .collect()
}

/// The bucket object (`<stem>Bucket`): bucket `id` plus the bucket's group rows.
fn bucket_object(pascal: &str, rows_field: &str) -> Object {
    [
        ("id", TypeRef::named(TypeRef::STRING)),
        (rows_field, TypeRef::named_list(format!("{pascal}Topic"))),
    ]
    .into_iter()
    .map(|(name, type_ref)| row_projection_field(name, type_ref))
    .fold(
        Object::new(format!("{pascal}Bucket").as_str()),
        |obj, field| obj.field(field),
    )
}

/// Build one topic group's schema parts: the merged
/// `<group>: [<Group>Topic]` list query with its supporting object types,
/// and — when the group's metadata declares `group_by` — grouped-by
/// bucket queries. Returns `None` when the group must be skipped entirely
/// (no usable metadata or a reserved/duplicate query name); claims all
/// used query names in `used_query_fields`.
fn register_group_queries(
    group: &TopicGroupDef,
    metadata: &[MetadataFile],
    used_query_fields: &mut BTreeSet<String>,
    cache: &Arc<TopicCache>,
) -> anyhow::Result<Option<GroupSchemaParts>> {
    let entries = collect_group_entries(metadata, &group.group);
    if group.fields.is_empty() {
        anyhow::bail!("topic group '{}' has no payload fields", group.group);
    }
    let query_field_name = claim_group_query_name(group, used_query_fields)?;
    let Some(metadata_fields) = group_metadata_fields(group, &entries)? else {
        return Ok(None);
    };
    let value_meta_json = value_metadata_json(group);
    let pascal = pascal_case(&group.group);

    let (bucket_object, bucket_fields) = register_bucket_queries(
        group,
        metadata,
        &entries,
        value_meta_json.clone(),
        cache,
        used_query_fields,
    )
    .map(|parts| (Some(parts.object), parts.query_fields))
    .unwrap_or_else(|| (None, Vec::new()));

    Ok(Some(GroupSchemaParts {
        query_fields: [group_query_field(
            &query_field_name,
            &format!("{pascal}Topic"),
            entries.clone(),
            group,
            value_meta_json,
            cache.clone(),
        )]
        .into_iter()
        .chain(bucket_fields)
        .collect(),
        objects: build_group_objects(&pascal, &metadata_fields, group)
            .into_iter()
            .chain(bucket_object)
            .collect(),
    }))
}

/// Schema contributions of a group's grouped-by bucket queries.
struct BucketSchemaParts {
    /// The bucket object type (`<stem>Bucket`).
    object: Object,
    /// The `<stem>Buckets` list field plus the `<stem>Bucket(id)` singleton.
    query_fields: Vec<Field>,
}

/// Build the grouped-by bucket schema parts: a `<stem>Buckets` list of
/// buckets plus a `<stem>Bucket(id)` singleton, enabled by a `group_by`
/// attribute in the group's metadata file. Returns `None` when the group
/// declares no `group_by` or the derived query names collide.
fn register_bucket_queries(
    group: &TopicGroupDef,
    metadata: &[MetadataFile],
    entries: &[(String, BTreeMap<String, JsonValue>)],
    value_meta_json: JsonValue,
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
) -> Option<BucketSchemaParts> {
    let group_by = metadata
        .iter()
        .filter(|file| file.group == group.group)
        .find_map(|file| file.group_by.clone())?;

    let group_stem = singular_group_stem(&group.group);
    let buckets_field = format!("{group_stem}Buckets");
    let bucket_field = format!("{group_stem}Bucket");
    if !used_query_fields.insert(buckets_field.clone())
        || !used_query_fields.insert(bucket_field.clone())
    {
        warn!("Duplicate grouped-by query name '{buckets_field}'");
        return None;
    }

    let pascal = pascal_case(&group.group);
    let rows_field = sanitize_to_graphql_name(&group.group);
    let bucket_type = format!("{pascal}Bucket");
    let buckets = bucket_rows_by(entries, &group_by);
    let fields = group.fields.clone();

    // `<stem>Buckets`: every bucket with its materialized group rows.
    let buckets_for_list = buckets.clone();
    let fields_for_list = fields.clone();
    let value_meta_for_list = value_meta_json.clone();
    let rows_for_list = rows_field.clone();
    let cache_for_list = cache.clone();
    let list_field = Field::new(
        buckets_field,
        TypeRef::named_list(bucket_type.clone()),
        move |_ctx| {
            let buckets = buckets_for_list.clone();
            let fields = fields_for_list.clone();
            let value_meta_json = value_meta_for_list.clone();
            let rows_field = rows_for_list.clone();
            let cache = cache_for_list.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let values =
                    bucket_rows_json(&buckets, &fields, &value_meta_json, &cache, &rows_field);
                Ok(Some(FieldValue::value(json_to_graphql_value(
                    &JsonValue::Array(values),
                ))))
            })
        },
    );

    // `<stem>Bucket(id)`: a single bucket by id, resolving to `None` for
    // unknown ids.
    let value_meta_for_bucket = value_meta_json;
    let rows_for_bucket = rows_field.clone();
    let cache_for_bucket = cache.clone();
    let singleton_field = Field::new(bucket_field, TypeRef::named(bucket_type), move |ctx| {
        let buckets = buckets.clone();
        let fields = fields.clone();
        let value_meta_json = value_meta_for_bucket.clone();
        let rows_field = rows_for_bucket.clone();
        let cache = cache_for_bucket.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let id = ctx.args.try_get("id")?.string()?;
            match buckets.get(id) {
                Some(rows) => {
                    let single = BTreeMap::from([(id.to_string(), rows.clone())]);
                    let values =
                        bucket_rows_json(&single, &fields, &value_meta_json, &cache, &rows_field);
                    Ok(values
                        .into_iter()
                        .next()
                        .map(|bucket| FieldValue::value(json_to_graphql_value(&bucket))))
                }
                None => Ok(None),
            }
        })
    })
    .argument(InputValue::new("id", TypeRef::named(TypeRef::STRING)));

    Some(BucketSchemaParts {
        object: bucket_object(&pascal, &rows_field),
        query_fields: vec![list_field, singleton_field],
    })
}

/// A field resolver that returns the named key of its parent row object.
fn row_projection_field(name: &str, type_ref: TypeRef) -> Field {
    let key = Name::new(name);
    Field::new(name, type_ref, move |ctx| {
        let key = key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map.get(&key).cloned().unwrap_or(GraphQlValue::Null),
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// The `<group>: [<Group>Topic]` query field.
///
/// Rows are materialized at resolution time: the metadata file enumerates
/// the concrete topics, static attributes come from that enumeration, and
/// live values come from the cache keyed by concrete topic.
fn group_query_field(
    query_field_name: &str,
    item_type: &str,
    entries: Vec<(String, BTreeMap<String, JsonValue>)>,
    group: &TopicGroupDef,
    value_meta_json: JsonValue,
    cache: Arc<TopicCache>,
) -> Field {
    let fields = group.fields.clone();
    Field::new(
        query_field_name,
        TypeRef::named_list(item_type),
        move |_ctx| {
            let entries = entries.clone();
            let fields = fields.clone();
            let value_meta_json = value_meta_json.clone();
            let cache = cache.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let rows: Vec<GraphQlValue> = entries
                    .iter()
                    .map(|(topic, meta)| {
                        json_to_graphql_value(&group_row(
                            topic,
                            meta,
                            &fields,
                            &cache,
                            Some(&value_meta_json),
                        ))
                    })
                    .collect();
                Ok(Some(FieldValue::value(GraphQlValue::List(rows))))
            })
        },
    )
}

/// Materialize bucket objects (`<Group>Bucket`: `{ id, <rows_key>: [row…] }`):
/// one per bucket id, each holding that bucket's group rows.
fn bucket_rows_json(
    buckets: &GroupedRows,
    fields: &[FieldDef],
    value_meta_json: &JsonValue,
    cache: &TopicCache,
    rows_key: &str,
) -> Vec<JsonValue> {
    buckets
        .iter()
        .map(|(id, rows)| {
            let group_rows: Vec<JsonValue> = rows
                .iter()
                .map(|(topic, meta)| group_row(topic, meta, fields, cache, Some(value_meta_json)))
                .collect();
            let mut bucket = serde_json::json!({ "id": id });
            bucket[rows_key] = JsonValue::Array(group_rows);
            bucket
        })
        .collect()
}

/// Per-field descriptors for a group: camelCase GraphQL name plus every
/// collected `x-*` schema extension (e.g. `unit`), keyed by sanitized name.
fn value_metadata_json(group: &TopicGroupDef) -> JsonValue {
    JsonValue::Array(
        group
            .fields
            .iter()
            .map(|field| {
                let descriptors = group
                    .value_extensions
                    .get(&field.name)
                    .into_iter()
                    .flatten()
                    .map(|(key, value)| {
                        (
                            sanitize_to_graphql_name(key),
                            JsonValue::String(value.clone()),
                        )
                    })
                    .filter(|(name, _)| !name.is_empty() && name != "name");

                JsonValue::Object(
                    once((
                        "name".to_string(),
                        JsonValue::String(sanitize_to_graphql_name(&field.name)),
                    ))
                    .chain(descriptors)
                    .collect(),
                )
            })
            .collect(),
    )
}

/// Materialize one group row: topic + static metadata (with the live-field
/// descriptors injected under `metadata.values` when given) + live values.
fn group_row(
    topic: &str,
    metadata: &BTreeMap<String, JsonValue>,
    fields: &[crate::asyncapi::FieldDef],
    cache: &TopicCache,
    value_meta: Option<&JsonValue>,
) -> JsonValue {
    let metadata_json: serde_json::Map<String, JsonValue> = metadata
        .iter()
        .map(|(key, value)| (sanitize_to_graphql_name(key), value.clone()))
        .chain(value_meta.map(|meta| ("values".to_string(), meta.clone())))
        .collect();

    let values_json: serde_json::Map<String, JsonValue> = fields
        .iter()
        .map(|field| {
            (
                sanitize_to_graphql_name(&field.name),
                cache
                    .get_field(topic, &field.name)
                    .unwrap_or(JsonValue::Null),
            )
        })
        .collect();

    serde_json::json!({
        "topic": topic,
        "metadata": metadata_json,
        "values": values_json,
    })
}

/// Union of sanitized metadata keys across a group's entries, typed by the
/// first non-null value seen.
fn union_metadata_fields(
    entries: &[(String, BTreeMap<String, JsonValue>)],
) -> Vec<(String, TypeRef)> {
    let mut fields: BTreeMap<String, Option<TypeRef>> = BTreeMap::new();
    for (_, metadata) in entries {
        for (key, value) in metadata {
            let name = sanitize_to_graphql_name(key);
            let slot = fields.entry(name).or_insert(None);
            if slot.is_none() && !value.is_null() {
                *slot = Some(graphql_scalar_for_value(value));
            }
        }
    }
    fields
        .into_iter()
        .map(|(name, type_ref)| {
            (
                name,
                type_ref.unwrap_or_else(|| TypeRef::named(TypeRef::STRING)),
            )
        })
        .collect()
}

/// GraphQL scalar for an arbitrary JSON value.
fn graphql_scalar_for_value(value: &JsonValue) -> TypeRef {
    match value {
        JsonValue::Bool(_) => TypeRef::named(TypeRef::BOOLEAN),
        JsonValue::Number(_) => TypeRef::named(TypeRef::FLOAT),
        _ => TypeRef::named(TypeRef::STRING),
    }
}

/// Query-name stem for grouped-by (bucket) queries: camelCase group name
/// with the plural "s" of its final word dropped (`power-tags` → `powerTag`),
/// so bucket queries are exposed as `<stem>Buckets` / `<stem>Bucket`.
fn singular_group_stem(group_id: &str) -> String {
    let camel = sanitize_to_graphql_name(group_id);
    match camel.strip_suffix('s') {
        Some(stem) => stem.to_string(),
        None => camel,
    }
}

/// Convert a JSON value to an async-graphql Value.
fn json_to_graphql_value(val: &JsonValue) -> GraphQlValue {
    match val {
        JsonValue::Null => GraphQlValue::Null,
        JsonValue::Bool(b) => GraphQlValue::Boolean(*b),
        JsonValue::Number(n) => {
            if let Some(i) = n.as_i64() {
                GraphQlValue::Number(i.into())
            } else if let Some(f) = n.as_f64() {
                GraphQlValue::Number(async_graphql::Number::from_f64(f).unwrap_or_else(|| 0.into()))
            } else {
                GraphQlValue::Null
            }
        }
        JsonValue::String(s) => GraphQlValue::String(s.clone()),
        JsonValue::Array(arr) => {
            GraphQlValue::List(arr.iter().map(json_to_graphql_value).collect())
        }
        JsonValue::Object(map) => GraphQlValue::Object(
            map.iter()
                .map(|(k, v)| (Name::new(k.clone()), json_to_graphql_value(v)))
                .collect(),
        ),
    }
}

/// Evict expired entries from the cache periodically.
pub fn spawn_eviction(cache: std::sync::Arc<TopicCache>) {
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(std::time::Duration::from_secs(30));
        loop {
            interval.tick().await;
            cache.evict_expired();
        }
    });
}

/// Map a GraphQL type name to an async-graphql TypeRef.
fn graphql_type_ref(typ: &str) -> TypeRef {
    match typ {
        "Float" => TypeRef::named(TypeRef::FLOAT),
        "Int" => TypeRef::named(TypeRef::INT),
        "Boolean" => TypeRef::named(TypeRef::BOOLEAN),
        "String" => TypeRef::named(TypeRef::STRING),
        _ => TypeRef::named(TypeRef::STRING),
    }
}

/// Validate that sanitized topic and field names are unique and not reserved.
///
/// Returns an error if:
/// - any topic sanitizes to an empty name
/// - any topic sanitizes to a reserved GraphQL name
/// - two topics sanitize to the same GraphQL name
/// - any field sanitizes to an empty name
/// - two fields within the same topic sanitize to the same name
pub fn validate_topics(topics: &[TopicDef]) -> anyhow::Result<()> {
    let mut seen_topics: BTreeMap<String, String> = BTreeMap::new();

    for td in topics {
        let sanitized = sanitize_to_graphql_name(&td.topic);
        if sanitized.is_empty() {
            anyhow::bail!("topic '{}' sanitizes to an empty GraphQL name", td.topic);
        }
        if is_reserved_name(&sanitized) {
            anyhow::bail!(
                "topic '{}' sanitizes to reserved GraphQL name '{}'",
                td.topic,
                sanitized
            );
        }
        if let Some(prev) = seen_topics.get(&sanitized) {
            anyhow::bail!(
                "duplicate sanitized topic name '{}' from topics '{}' and '{}'",
                sanitized,
                prev,
                td.topic
            );
        }
        seen_topics.insert(sanitized.clone(), td.topic.clone());

        validate_topic_fields(&td.topic, &td.fields)?;
    }

    Ok(())
}

/// Validate one topic's payload fields: unique raw names, plus non-empty
/// and unique sanitized GraphQL names.
fn validate_topic_fields(topic: &str, fields: &[FieldDef]) -> anyhow::Result<()> {
    let mut seen_fields: BTreeMap<String, String> = BTreeMap::new();
    let mut seen_raw_fields: BTreeSet<String> = BTreeSet::new();
    for field in fields {
        // Raw duplicate (should also be caught by sanitized check, but give clearer error)
        if !seen_raw_fields.insert(field.name.clone()) {
            anyhow::bail!("duplicate field name '{}' in topic '{}'", field.name, topic);
        }
        let sanitized_field = sanitize_to_graphql_name(&field.name);
        if sanitized_field.is_empty() {
            anyhow::bail!(
                "field '{}' in topic '{}' sanitizes to an empty GraphQL name",
                field.name,
                topic
            );
        }
        if let Some(prev) = seen_fields.get(&sanitized_field) {
            anyhow::bail!(
                "duplicate sanitized field name '{}' in topic '{}' from fields '{}' and '{}'",
                sanitized_field,
                topic,
                prev,
                field.name
            );
        }
        seen_fields.insert(sanitized_field, field.name.clone());
    }
    Ok(())
}

/// Derive a GraphQL scalar type name from a (possibly `$ref`'d) subschema.
pub(crate) fn graphql_type_for_subschema(sub: &SubSchema, doc: &Document) -> Option<String> {
    match sub {
        SubSchema::Bool(_) => None,
        SubSchema::Schema(boxed) => match boxed.as_ref() {
            RefOr::Item(schema) => type_from_schema(schema, doc),
            RefOr::Reference(r) => {
                let key = r.component_key("schemas")?;
                let entry = doc.components.as_ref()?.schemas.get(&key)?;
                let resolved = entry.item()?;
                match resolved {
                    SchemaOrMultiFormat::Schema(s) => type_from_schema(s, doc),
                    SchemaOrMultiFormat::MultiFormat(mf) => {
                        let schema: AsyncApiSchema =
                            serde_json::from_value(mf.schema.clone()).ok()?;
                        type_from_schema(&schema, doc)
                    }
                    SchemaOrMultiFormat::Bool(_) => None,
                }
            }
        },
    }
}

fn type_from_schema(schema: &AsyncApiSchema, doc: &Document) -> Option<String> {
    if let Some(schema_type) = &schema.schema_type {
        return match schema_type {
            SchemaType::Single(t) => map_json_type_to_graphql(t),
            SchemaType::Multiple(types) => {
                for t in types {
                    if t == "null" {
                        continue;
                    }
                    if let Some(gql) = map_json_type_to_graphql(t) {
                        return Some(gql.to_string());
                    }
                }
                None
            }
        };
    }

    // Handle nullable via anyOf / oneOf / allOf
    if let Some(any_of) = &schema.any_of {
        for sub in any_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }
    if let Some(one_of) = &schema.one_of {
        for sub in one_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }
    if let Some(all_of) = &schema.all_of {
        for sub in all_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }

    None
}

fn map_json_type_to_graphql(t: &str) -> Option<String> {
    match t {
        "number" => Some("Float".to_string()),
        "integer" => Some("Int".to_string()),
        "boolean" => Some("Boolean".to_string()),
        "string" => Some("String".to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::asyncapi::FieldDef;
    use crate::http::router;
    use axum::http::StatusCode;
    use serde_json::json;
    use tower::ServiceExt;

    #[test]
    fn test_build_schema_for_one_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![
                FieldDef {
                    name: "value".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "ok".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        let _schema = build_schema(&topics, cache, &[], &[]).unwrap();
        // Schema builds without panicking
    }

    #[test]
    fn test_colliding_sanitized_topics_error() {
        // "a/b" and "a-b" both sanitize to "a_b" — should error rather than suffix
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![FieldDef {
                    name: "x".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "a-b".to_string(),
                fields: vec![FieldDef {
                    name: "y".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let err = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap_err();
        assert!(
            err.to_string().contains("duplicate sanitized topic name"),
            "{err}"
        );
    }

    #[test]
    fn test_reserved_topic_name_errors() {
        let topics = vec![TopicDef {
            topic: "Query".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let err = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap_err();
        assert!(err.to_string().contains("reserved"), "{err}");
    }

    #[test]
    fn test_digit_prefixed_topic_is_valid() {
        let topics = vec![TopicDef {
            topic: "123/topic".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("_123Topic"), "{sdl}");
    }

    #[test]
    fn test_empty_topic_is_listed_but_not_queryable() {
        // A topic without scalar fields must not crash schema building;
        // it stays visible via `topics` but has no query type.
        let topics = vec![TopicDef {
            topic: "empty/topic".to_string(),
            fields: vec![],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("emptyTopic"), "{sdl}");
    }

    #[test]
    fn test_field_types_in_schema() {
        let topics = vec![TopicDef {
            topic: "t".to_string(),
            fields: vec![
                FieldDef {
                    name: "f_float".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "f_int".to_string(),
                    graphql_type: "Int".to_string(),
                },
                FieldDef {
                    name: "f_bool".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
                FieldDef {
                    name: "f_str".to_string(),
                    graphql_type: "String".to_string(),
                },
                FieldDef {
                    name: "f_unknown".to_string(),
                    graphql_type: "DateTime".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("fFloat: Float"), "{sdl}");
        assert!(sdl.contains("fInt: Int"), "{sdl}");
        assert!(sdl.contains("fBool: Boolean"), "{sdl}");
        assert!(sdl.contains("fStr: String"), "{sdl}");
        // Unknown types fall back to String
        assert!(sdl.contains("fUnknown: String"), "{sdl}");
    }

    #[tokio::test]
    async fn test_query_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![
                FieldDef {
                    name: "value".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "ok".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
                FieldDef {
                    name: "label".to_string(),
                    graphql_type: "String".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "test/channel",
            json!({"value": 23.5, "ok": true, "label": "hello"}),
        );
        let schema = build_schema(&topics, cache, &[], &[]).unwrap();

        let response = schema.execute("{ testChannel { value ok label } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"]["value"], json!(23.5));
        assert_eq!(data["testChannel"]["ok"], json!(true));
        assert_eq!(data["testChannel"]["label"], json!("hello"));
    }

    #[tokio::test]
    async fn test_query_returns_null_for_missing_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"], json!(null));
    }

    #[tokio::test]
    async fn test_query_returns_null_for_missing_field() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"other": 1.0}));
        let schema = build_schema(&topics, cache, &[], &[]).unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"]["value"], json!(null));
    }

    #[tokio::test]
    async fn test_query_unknown_field_errors() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();

        let response = schema.execute("{ testChannel { nope } }").await;
        assert!(!response.errors.is_empty());
    }

    #[tokio::test]
    async fn test_topics_field_lists_all_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "c/d".to_string(),
                fields: vec![],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let schema = build_schema(&topics, Arc::new(TopicCache::new()), &[], &[]).unwrap();

        let response = schema.execute("{ topics }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["topics"], json!(["a/b", "c/d"]));
    }

    #[tokio::test]
    async fn test_query_multiple_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![FieldDef {
                    name: "x".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "c/d".to_string(),
                fields: vec![FieldDef {
                    name: "y".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let cache = Arc::new(TopicCache::new());
        cache.insert("a/b", json!({"x": 1.5}));
        cache.insert("c/d", json!({"y": 2.5}));
        let schema = build_schema(&topics, cache, &[], &[]).unwrap();

        let response = schema.execute("{ aB { x } cD { y } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["aB"]["x"], json!(1.5));
        assert_eq!(data["cD"]["y"], json!(2.5));
    }

    fn power_tag_group() -> Vec<TopicGroupDef> {
        vec![TopicGroupDef {
            group: "power-tags".to_string(),
            pattern: "power-tags/+/+".to_string(),
            params: vec!["panel".to_string(), "slug".to_string()],
            fields: vec![
                FieldDef {
                    name: "active_power_total".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "current_a".to_string(),
                    graphql_type: "Float".to_string(),
                },
            ],
            payload_schema: None,
            value_extensions: BTreeMap::from([
                (
                    "active_power_total".to_string(),
                    BTreeMap::from([("unit".to_string(), "W".to_string())]),
                ),
                (
                    "current_a".to_string(),
                    BTreeMap::from([("unit".to_string(), "A".to_string())]),
                ),
            ]),
            ttl_secs: 300,
        }]
    }

    fn power_tag_metadata() -> Vec<MetadataFile> {
        serde_json::from_value(json!([
            {
                "group": "power-tags",
                "topics": [
                    {
                        "topic": "power-tags/10P1/test-consumer",
                        "metadata": {
                            "panel": "10P1",
                            "slug": "test-consumer",
                            "component": "150F01",
                            "consumer": "TEST CONSUMER"
                        }
                    },
                    {
                        "topic": "power-tags/10P2/no-data",
                        "metadata": {"component": "151F01", "slug": "no-data"}
                    }
                ]
            }
        ]))
        .unwrap()
    }

    #[tokio::test]
    async fn test_group_list_returns_metadata_and_values() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(&[], cache, &power_tag_group(), &power_tag_metadata()).unwrap();

        let response = schema
            .execute(
                "{ powerTags { topic \
                 metadata { panel component consumer values { name unit } } \
                 values { activePowerTotal } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let rows = data["powerTags"].as_array().unwrap();
        assert_eq!(rows.len(), 2);

        assert_eq!(rows[0]["topic"], json!("power-tags/10P1/test-consumer"));
        assert_eq!(rows[0]["metadata"]["panel"], json!("10P1"));
        assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
        assert_eq!(rows[0]["metadata"]["consumer"], json!("TEST CONSUMER"));
        assert_eq!(
            rows[0]["metadata"]["values"],
            json!([
                {"name": "activePowerTotal", "unit": "W"},
                {"name": "currentA", "unit": "A"}
            ])
        );
        assert_eq!(rows[0]["values"]["activePowerTotal"], json!(42.0));

        // Second row has no cached MQTT data: static fields present, live null
        assert_eq!(rows[1]["topic"], json!("power-tags/10P2/no-data"));
        assert_eq!(rows[1]["metadata"]["panel"], json!(null));
        assert_eq!(rows[1]["metadata"]["component"], json!("151F01"));
        assert_eq!(rows[1]["values"]["activePowerTotal"], json!(null));
    }

    #[tokio::test]
    async fn test_group_without_mqtt_data_serves_static() {
        let schema = build_schema(
            &[],
            Arc::new(TopicCache::new()),
            &power_tag_group(),
            &power_tag_metadata(),
        )
        .unwrap();

        let response = schema
            .execute("{ powerTags { metadata { component slug } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let rows = data["powerTags"].as_array().unwrap();
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
        assert_eq!(rows[0]["metadata"]["slug"], json!("test-consumer"));
    }

    #[tokio::test]
    async fn test_group_without_metadata_omits_query_field() {
        // Without metadata there is no enumeration source, so no list field
        // (empty object types would be invalid GraphQL).
        let schema =
            build_schema(&[], Arc::new(TopicCache::new()), &power_tag_group(), &[]).unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("powerTags"), "{sdl}");
    }

    #[tokio::test]
    async fn test_group_live_values_expire_to_null() {
        let per_topic =
            std::collections::HashMap::from([("power-tags/10P1/test-consumer".to_string(), 0u64)]);
        let cache = Arc::new(TopicCache::with_ttl(60, per_topic));
        cache.insert("power-tags/10P1/test-consumer", json!({"current_a": 1.0}));
        let schema = build_schema(
            &[],
            cache.clone(),
            &power_tag_group(),
            &power_tag_metadata(),
        )
        .unwrap();

        let response = schema
            .execute("{ powerTags { values { currentA } } }")
            .await;
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTags"][0]["values"]["currentA"], json!(null));

        // A topic without a zero-TTL override keeps serving its cached value
        cache.insert("power-tags/10P2/no-data", json!({"current_a": 2.5}));
        let response = schema
            .execute("{ powerTags { values { currentA } } }")
            .await;
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTags"][1]["values"]["currentA"], json!(2.5));
    }

    #[tokio::test]
    async fn test_power_tag_bucket_grouping() {
        // `group_by: "panel"` on the group's metadata file enables bucket queries.
        let mut metadata = power_tag_metadata();
        metadata[0].group_by = Some("panel".to_string());
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(&[], cache, &power_tag_group(), &metadata).unwrap();

        let response = schema
            .execute(
                "{ powerTagBuckets { id powerTags { topic values { activePowerTotal } } } \
                 powerTagBucket(id: \"10P1\") { id powerTags { topic } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();

        // Entries without the `group_by` attribute land in the "unknown" bucket.
        let buckets = data["powerTagBuckets"].as_array().unwrap();
        assert_eq!(buckets.len(), 2);
        assert_eq!(buckets[0]["id"], json!("10P1"));
        assert_eq!(
            buckets[0]["powerTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );
        assert_eq!(
            buckets[0]["powerTags"][0]["values"]["activePowerTotal"],
            json!(42.0)
        );
        assert_eq!(buckets[1]["id"], json!("unknown"));
        assert_eq!(
            buckets[1]["powerTags"][0]["topic"],
            json!("power-tags/10P2/no-data")
        );

        assert_eq!(
            data["powerTagBucket"]["powerTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );

        // Unknown bucket ids resolve to null.
        let response = schema
            .execute("{ powerTagBucket(id: \"nope\") { id } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTagBucket"], json!(null));
    }

    #[tokio::test]
    async fn test_grouped_by_queries_are_generic() {
        // Any group whose metadata file declares `group_by` gains grouped
        // queries — the names derive from group + attribute, not from a
        // hardcoded domain.
        let mut group = power_tag_group()[0].clone();
        group.group = "fuel-tags".to_string();
        group.pattern = "fuel-tags/+/+".to_string();
        let mut metadata = power_tag_metadata();
        metadata[0].group = "fuel-tags".to_string();
        metadata[0].group_by = Some("tank".to_string());
        metadata[0].topics[0]
            .metadata
            .insert("tank".to_string(), json!("T01"));

        let cache = Arc::new(TopicCache::new());
        let schema = build_schema(&[], cache, &[group], &metadata).unwrap();

        let response = schema
            .execute(
                "{ fuelTagBuckets { id fuelTags { topic } } \
                 fuelTagBucket(id: \"T01\") { id } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();

        // Entries without a `tank` attribute land in the "unknown" bucket.
        let buckets = data["fuelTagBuckets"].as_array().unwrap();
        assert_eq!(buckets.len(), 2);
        assert_eq!(buckets[0]["id"], json!("T01"));
        assert_eq!(
            buckets[0]["fuelTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );
        assert_eq!(buckets[1]["id"], json!("unknown"));
        assert_eq!(data["fuelTagBucket"]["id"], json!("T01"));
    }

    #[tokio::test]
    async fn test_concrete_topic_gains_metadata_field() {
        let topics = vec![TopicDef {
            topic: "sensor/temp".to_string(),
            fields: vec![FieldDef {
                name: "celsius".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];
        let metadata: Vec<MetadataFile> = serde_json::from_value(json!([
            {
                "group": "sensors",
                "topics": [
                    {"topic": "sensor/temp", "metadata": {"room": "galley"}}
                ]
            }
        ]))
        .unwrap();

        let cache = Arc::new(TopicCache::new());
        cache.insert("sensor/temp", json!({"celsius": 21.5}));
        let schema = build_schema(&topics, cache, &[], &metadata).unwrap();

        let response = schema
            .execute("{ sensorTemp { celsius metadata { room } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["sensorTemp"]["celsius"], json!(21.5));
        assert_eq!(data["sensorTemp"]["metadata"]["room"], json!("galley"));
    }

    #[tokio::test]
    async fn test_health_endpoint() {
        let app = router(build_schema(&[], Arc::new(TopicCache::new()), &[], &[]).unwrap());

        let response = app
            .oneshot(
                axum::http::Request::builder()
                    .uri("/health")
                    .body(axum::body::Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_graphql_endpoint_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"value": 42.0}));
        let app = router(build_schema(&topics, cache, &[], &[]).unwrap());

        let request = axum::http::Request::builder()
            .method("POST")
            .uri("/graphql")
            .header("content-type", "application/json")
            .body(axum::body::Body::from(
                r#"{"query": "{ testChannel { value } }"}"#,
            ))
            .unwrap();

        let response = app.oneshot(request).await.unwrap();
        assert_eq!(response.status(), StatusCode::OK);

        let body = axum::body::to_bytes(response.into_body(), 1024 * 1024)
            .await
            .unwrap();
        let data: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert_eq!(data["data"]["testChannel"]["value"], json!(42.0));
    }
}
