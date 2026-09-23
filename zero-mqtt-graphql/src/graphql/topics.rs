use super::*;

/// Schema contributions of the concrete (non-grouped) topics.
#[derive(Default)]
pub(super) struct ConcreteTopics {
    pub(super) objects: Vec<Object>,
    /// `(type name, metadata)` pairs for `<Topic>Metadata` objects.
    pub(super) metadata_types: Vec<(String, BTreeMap<String, JsonValue>)>,
    /// Query fields returning each topic's whole cached payload.
    pub(super) query_fields: Vec<Field>,
}

/// Topics eligible for a queryable payload object: those with fields.
pub(super) fn queryable_topics(topics: &[TopicDef]) -> impl Iterator<Item = &TopicDef> {
    topics
        .iter()
        .filter(|topic_def| !topic_def.fields.is_empty())
}

/// `(type name, metadata)` for a topic with non-empty metadata.
pub(super) fn metadata_type(
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

/// Objects, metadata types and query fields for every concrete topic.
pub(super) fn register_concrete_topics(
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

/// A topic's `<Topic>` object, with a `metadata` field when annotated.
pub(super) fn topic_object(topic_def: &TopicDef, metadata_store: &Arc<MetadataByTopic>) -> Object {
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

/// The `<Topic>` query field; subfields project from the payload, so the cache is read once.
pub(super) fn topic_query_field(topic: &str, type_name: &str, cache: &Arc<TopicCache>) -> Field {
    let obj_ref = TypeRef::named(type_name);
    let topic = topic.to_string();
    let cache_for_query = cache.clone();
    Field::new(type_name, obj_ref, move |_ctx| {
        let val = cache_for_query.get(&topic);
        FieldFuture::new(async move { Ok(val.map(|json_val| json_to_graphql_value(&json_val))) })
    })
}

/// A scalar field projecting its raw name from the parent payload.
pub(super) fn payload_field(field: &FieldDef) -> Field {
    key_field(
        sanitize_to_graphql_name(&field.name),
        graphql_type_ref(&field.graphql_type),
        &field.name,
    )
}

/// The `metadata` field with a topic's static attributes.
pub(super) fn metadata_field(
    topic: &str,
    meta_type_name: &str,
    metadata_store: &Arc<MetadataByTopic>,
) -> Field {
    let store = metadata_store.clone();
    let topic = topic.to_string();
    Field::new("metadata", TypeRef::named(meta_type_name), move |_ctx| {
        let store = store.clone();
        let topic = topic.clone();
        FieldFuture::new(async move {
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

/// Validate that sanitized topic and field names are non-empty, unique and not reserved.
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

/// Validate one topic's field names, raw and sanitized.
pub(super) fn validate_topic_fields(topic: &str, fields: &[FieldDef]) -> anyhow::Result<()> {
    let mut seen_fields: BTreeMap<String, String> = BTreeMap::new();
    let mut seen_raw_fields: BTreeSet<String> = BTreeSet::new();
    for field in fields {
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
