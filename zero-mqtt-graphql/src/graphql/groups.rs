use super::*;

/// Schema contributions of one topic group.
pub(super) struct GroupSchemaParts {
    /// The group's supporting object types plus its optional bucket type.
    pub(super) objects: Vec<Object>,
    /// The list query field plus optional grouped-by query fields.
    pub(super) query_fields: Vec<Field>,
}

/// A group's metadata-file entries as `(topic, metadata)` pairs.
pub(super) fn collect_group_entries(
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

/// Sanitize a group id into an unclaimed, non-reserved query field name.
pub(super) fn claim_group_query_name(
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

/// A group's sanitized metadata keys minus `values`, which the live-field
/// descriptors occupy (a duplicate would panic on registration).
pub(super) fn group_metadata_fields(
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
pub(super) fn build_group_objects(
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

/// Union of a group's `x-*` extension keys across its payload fields.
pub(super) fn extension_keys(group: &TopicGroupDef) -> Vec<String> {
    group
        .value_extensions
        .values()
        .flat_map(|extensions| extensions.keys().cloned())
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

/// `<Group>ValueMeta` fields: `name` plus every `x-*` extension (e.g. `unit`).
pub(super) fn value_meta_descriptor_fields(
    group: &TopicGroupDef,
) -> impl Iterator<Item = Field> + '_ {
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

/// A row's `group_by` value, or `"unknown"` when absent or not a string.
pub(super) fn bucket_attribute<'a>(
    meta: &'a BTreeMap<String, JsonValue>,
    group_by: &'a str,
) -> &'a str {
    meta.get(group_by)
        .and_then(JsonValue::as_str)
        .unwrap_or("unknown")
}

/// Bucket a group's rows by their `group_by` attribute value.
pub(super) fn bucket_rows_by(
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

/// The `<stem>Bucket` object: `id` plus the bucket's rows.
pub(super) fn bucket_object(pascal: &str, rows_field: &str) -> Object {
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

/// A group's list query, types and optional bucket queries; `None` when skipped
/// for lack of metadata or a clashing name.
pub(super) fn register_group_queries(
    group: &TopicGroupDef,
    metadata: &[MetadataFile],
    used_query_fields: &mut BTreeSet<String>,
    cache: &Arc<TopicCache>,
) -> anyhow::Result<Option<GroupSchemaParts>> {
    let entries = collect_group_entries(metadata, &group.group);
    if group.fields.is_empty() {
        // A fieldless group (e.g. `{module}/control-mode`) is served via its view;
        // only with metadata is it a misconfiguration.
        if entries.is_empty() {
            warn!(
                "Topic group '{}' has no scalar payload fields — no list query exposed",
                group.group
            );
            return Ok(None);
        }
        anyhow::bail!("topic group '{}' has no payload fields", group.group);
    }
    // anyOf branches union their fields; a name conflict must error, not panic.
    validate_topic_fields(&group.group, &group.fields)?;
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
pub(super) struct BucketSchemaParts {
    /// The bucket object type (`<stem>Bucket`).
    object: Object,
    /// The `<stem>Buckets` list field plus the `<stem>Bucket(id)` singleton.
    query_fields: Vec<Field>,
}

/// `<stem>Buckets` and `<stem>Bucket(id)` for a group with `group_by`; `None`
/// without it or on a name collision.
pub(super) fn register_bucket_queries(
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
            FieldFuture::new(async move {
                let values =
                    bucket_rows_json(&buckets, &fields, &value_meta_json, &cache, &rows_field);
                Ok(Some(FieldValue::value(json_to_graphql_value(
                    &JsonValue::Array(values),
                ))))
            })
        },
    );

    let value_meta_for_bucket = value_meta_json;
    let rows_for_bucket = rows_field.clone();
    let cache_for_bucket = cache.clone();
    let singleton_field = Field::new(bucket_field, TypeRef::named(bucket_type), move |ctx| {
        let buckets = buckets.clone();
        let fields = fields.clone();
        let value_meta_json = value_meta_for_bucket.clone();
        let rows_field = rows_for_bucket.clone();
        let cache = cache_for_bucket.clone();
        FieldFuture::new(async move {
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
pub(super) fn row_projection_field(name: &str, type_ref: TypeRef) -> Field {
    key_field(name, type_ref, name)
}

/// The `<group>: [<Group>Topic]` query field; rows are materialized per resolve.
pub(super) fn group_query_field(
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
            FieldFuture::new(async move {
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

/// Materialize one `{ id, <rows_key>: [row…] }` object per bucket.
pub(super) fn bucket_rows_json(
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

/// Per-field descriptors (name plus `x-*` extensions), keyed by sanitized name.
pub(super) fn value_metadata_json(group: &TopicGroupDef) -> JsonValue {
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

/// Materialize one row: topic, metadata (descriptors under `metadata.values`) and live values.
pub(super) fn group_row(
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

/// Sanitized metadata keys across entries, typed by the first non-null value.
pub(super) fn union_metadata_fields(
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

/// Bucket query stem: camelCase group name singularized (`power-tags` → `powerTag`).
pub(super) fn singular_group_stem(group_id: &str) -> String {
    let camel = sanitize_to_graphql_name(group_id);
    match camel.strip_suffix('s') {
        Some(stem) => stem.to_string(),
        None => camel,
    }
}
