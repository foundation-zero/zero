use std::collections::{BTreeMap, BTreeSet};
use std::iter::once;
use std::sync::Arc;

use crate::api_model::GraphqlType;
use crate::graphql::{graphql_type_ref, json_to_graphql_value};
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{Field, FieldValue, InputValue, Object, TypeRef};
use log::warn;
use serde_json::Value as JsonValue;

use crate::naming::{is_reserved_name, pascal_case_graphql_name, sanitize_to_graphql_name};
use crate::{
    api_model::{ApiModel, TopicGroupDef},
    cache::TopicCache,
};

/// A group's rows partitioned into buckets by the `group_by` metadata
/// attribute: bucket id → `(topic, metadata)` pairs.
type GroupedRows = BTreeMap<String, Vec<(String, BTreeMap<String, JsonValue>)>>;

pub(super) fn build_schema_groups(
    mut schema_object: Object,
    api: &ApiModel,
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
) -> anyhow::Result<(Object, Vec<Object>)> {
    // Group list queries: one merged list per parametrized channel whose
    // domain ships a metadata file (which enumerates the concrete topics).
    let (query_fields, group_objects): (Vec<_>, Vec<_>) = api
        .groups
        .iter()
        .map(|group| register_group_queries(group, used_query_fields, cache))
        .collect::<anyhow::Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .map(|parts| (parts.query_fields, parts.objects))
        .unzip();

    schema_object = query_fields
        .into_iter()
        .flatten()
        .fold(schema_object, Object::field);

    Ok((schema_object, group_objects.into_iter().flatten().collect()))
}

/// Schema contributions of one topic group.
struct GroupSchemaParts {
    /// The group's supporting object types plus its optional bucket type.
    objects: Vec<Object>,
    /// The list query field plus optional grouped-by query fields.
    query_fields: Vec<Field>,
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
fn group_metadata_fields(group: &TopicGroupDef) -> anyhow::Result<Option<Vec<(String, TypeRef)>>> {
    let fields = union_metadata_fields(&group.topic_metadata);
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

    // let values_obj = payload_object(&values_type, &group.fields);
    let values_obj = group
        .fields
        .iter()
        .map(|(field_name, graphql_type)| {
            row_projection_field(
                &sanitize_to_graphql_name(field_name),
                graphql_type_ref(graphql_type),
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
fn bucket_rows_by(group: &TopicGroupDef) -> GroupedRows {
    group
        .topic_metadata
        .values()
        .map(|meta| bucket_attribute(meta, &group.group_by))
        .collect::<BTreeSet<_>>()
        .into_iter()
        .map(|attribute| {
            let rows = group
                .topic_metadata
                .iter()
                .filter(|(_, meta)| bucket_attribute(meta, &group.group_by) == attribute)
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
        Object::field,
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
    used_query_fields: &mut BTreeSet<String>,
    cache: &Arc<TopicCache>,
) -> anyhow::Result<Option<GroupSchemaParts>> {
    if group.fields.is_empty() {
        anyhow::bail!("topic group '{}' has no payload fields", group.group);
    }
    let query_field_name = claim_group_query_name(group, used_query_fields)?;
    let Some(metadata_fields) = group_metadata_fields(group)? else {
        warn!("No metadata for this group, ignoring");
        return Ok(None);
    };
    let value_meta_json = value_metadata_json(group);
    let pascal = pascal_case_graphql_name(&group.group);

    let (bucket_object, bucket_fields) =
        register_bucket_queries(group, value_meta_json.clone(), cache, used_query_fields)
            .map_or_else(
                || (None, Vec::new()),
                |parts| (Some(parts.object), parts.query_fields),
            );

    Ok(Some(GroupSchemaParts {
        query_fields: [group_query_field(
            &query_field_name,
            &format!("{pascal}Topic"),
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
#[allow(clippy::similar_names)]
fn register_bucket_queries(
    group: &TopicGroupDef,
    value_meta_json: JsonValue,
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
) -> Option<BucketSchemaParts> {
    let group_stem = singular_group_stem(&group.group);
    let buckets_field = format!("{group_stem}Buckets");
    let bucket_field = format!("{group_stem}Bucket");
    if !used_query_fields.insert(buckets_field.clone())
        || !used_query_fields.insert(bucket_field.clone())
    {
        warn!("Duplicate grouped-by query name '{buckets_field}'");
        return None;
    }

    let pascal = pascal_case_graphql_name(&group.group);
    let rows_field = sanitize_to_graphql_name(&group.group);
    let bucket_type = format!("{pascal}Bucket");
    let buckets = bucket_rows_by(group);
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
    group: &TopicGroupDef,
    value_meta_json: JsonValue,
    cache: Arc<TopicCache>,
) -> Field {
    let fields = group.fields.clone();
    let metadata = group.topic_metadata.clone();
    Field::new(
        query_field_name,
        TypeRef::named_list(item_type),
        move |_ctx| {
            let entries = metadata.clone();
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
    fields: &BTreeMap<String, GraphqlType>,
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
            .keys()
            .map(|field_name| {
                let descriptors = group
                    .value_extensions
                    .get(field_name)
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
                        JsonValue::String(sanitize_to_graphql_name(field_name)),
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
    fields: &BTreeMap<String, GraphqlType>,
    cache: &TopicCache,
    value_meta: Option<&JsonValue>,
) -> JsonValue {
    let metadata_json: serde_json::Map<String, JsonValue> = metadata
        .iter()
        .map(|(key, value)| (sanitize_to_graphql_name(key), value.clone()))
        .chain(value_meta.map(|meta| ("values".to_string(), meta.clone())))
        .collect();

    let values_json: serde_json::Map<String, JsonValue> = fields
        .keys()
        .map(|field_name| {
            (
                sanitize_to_graphql_name(field_name),
                cache
                    .get_field(topic, field_name)
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
    entries: &BTreeMap<String, BTreeMap<String, JsonValue>>,
) -> Vec<(String, TypeRef)> {
    let mut fields: BTreeMap<String, Option<TypeRef>> = BTreeMap::new();
    for metadata in entries.values() {
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

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::api_model::{Api, ApiModel};
    use crate::graphql::build_schema;
    use crate::metadata::MetadataByTopic;
    use crate::roas_asyncapi::OperationAction;
    use crate::topic_map::TopicMap;
    use serde_json::json;

    fn api(groups: Vec<TopicGroupDef>) -> Api {
        Api::new(vec![ApiModel::new(
            "".to_string(),
            TopicMap::new(),
            vec![],
            groups,
            TopicMap::new(),
        )])
    }

    fn power_tag_group(metadata: MetadataByTopic) -> Vec<TopicGroupDef> {
        vec![TopicGroupDef {
            group: "power-tags".to_string(),
            pattern: "power-tags/+/+".to_string(),
            fields: BTreeMap::from_iter(vec![
                ("active_power_total".to_string(), GraphqlType::Float),
                ("current_a".to_string(), GraphqlType::Float),
            ]),
            payload_schema_ref: None,
            action: OperationAction::Send,
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
            topic_metadata: metadata,
            group_by: "panel".to_string(),
        }]
    }

    fn power_tag_metadata() -> MetadataByTopic {
        serde_json::from_value(json!({
            "power-tags/10P1/test-consumer": {
                "panel": "10P1",
                "slug": "test-consumer",
                "component": "150F01",
                "consumer": "TEST CONSUMER"
            },
            "power-tags/10P2/no-data":  {
                "component": "151F01", "slug": "no-data"
            }
        }))
        .unwrap()
    }

    #[tokio::test]
    async fn test_group_list_returns_metadata_and_values() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(&api(power_tag_group(power_tag_metadata())), &cache).unwrap();

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
            &api(power_tag_group(power_tag_metadata())),
            &Arc::new(TopicCache::new()),
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
        let schema = build_schema(
            &api(power_tag_group(BTreeMap::new())),
            &Arc::new(TopicCache::new()),
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("powerTags"), "{sdl}");
    }

    #[tokio::test]
    async fn test_group_live_values_expire_to_null() {
        let per_topic = [("power-tags/10P1/test-consumer".to_string(), 0u64)]
            .into_iter()
            .collect();
        let cache = Arc::new(TopicCache::with_ttl(60, per_topic));
        cache.insert("power-tags/10P1/test-consumer", json!({"current_a": 1.0}));
        let schema = build_schema(&api(power_tag_group(power_tag_metadata())), &cache).unwrap();

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
        let metadata = power_tag_metadata();
        // metadata[0].group_by = Some("panel".to_string());
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(&api(power_tag_group(metadata)), &cache).unwrap();

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
        let metadata = serde_json::from_value(json!({
            "fuel-tags/T01/test-consumer": {
                "tank": "T01",
                "slug": "test-consumer",
                "component": "150F01",
                "consumer": "TEST CONSUMER"
            },
            "fuel-tags/T02/no-data":  {
                "component": "151F01", "slug": "no-data"
            }
        }))
        .unwrap();

        let mut group = power_tag_group(metadata)[0].clone();
        group.group = "fuel-tags".to_string();
        group.group_by = "tank".to_string();

        let cache = Arc::new(TopicCache::new());
        let schema = build_schema(&api(vec![group]), &cache).unwrap();

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
            json!("fuel-tags/T01/test-consumer")
        );
        assert_eq!(buckets[1]["id"], json!("unknown"));
        assert_eq!(data["fuelTagBucket"]["id"], json!("T01"));
    }
}
