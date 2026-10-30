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
use std::sync::Arc;

use crate::api_model::GraphqlType;
use crate::graphql::groups::build_schema_groups;
use crate::graphql::topics::build_schema_topics;
use anyhow::Context;
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{Field, FieldValue, Object, Schema, SchemaBuilder, TypeRef};
use log::warn;
use serde_json::Value as JsonValue;

use crate::naming::{is_reserved_name, pascal_case_graphql_name, sanitize_to_graphql_name};
use crate::{
    api_model::{Api, TopicDef},
    cache::TopicCache,
};

mod groups;
mod topics;

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
pub fn build_schema(api: &Api, cache: &Arc<TopicCache>) -> anyhow::Result<Schema> {
    validate_topics(api)?;

    let mut query = Object::new("Query");
    let mut schema_builder = Schema::build(query.type_name(), None, None);

    for api_model in &api.models {
        let new_objects;
        (query, new_objects) = build_schema_topics(query, api_model, cache);
        schema_builder = new_objects
            .into_iter()
            .fold(schema_builder, SchemaBuilder::register);

        let group_objects;
        (query, group_objects) = build_schema_groups(query, api_model, cache)
            .with_context(|| "Error while building group schema")?;
        schema_builder = group_objects
            .into_iter()
            .fold(schema_builder, SchemaBuilder::register);
    }

    // Not really useful but prevents errors if no topics are defined
    query = query.field(topics_introspection_field(&api.topics()));

    schema_builder
        .register(query)
        .finish()
        .with_context(|| "Schema building failed")
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

/// One concrete topic's `<Topic>` payload object
fn payload_object(name: &str, fields: &BTreeMap<String, GraphqlType>) -> Vec<Object> {
    if fields.is_empty() {
        warn!("Object {name} can't have zero fields!");
    }

    let type_name = pascal_case_graphql_name(name);
    let (object, mut objects) = fields.iter().map(payload_field).fold(
        (Object::new(type_name.as_str()), Vec::new()),
        |(obj, mut objects): (Object, Vec<Object>), (field, new_objects)| {
            objects.extend(new_objects);
            (obj.field(field), objects)
        },
    );
    objects.insert(0, object);
    objects
}

/// One scalar payload field on a `<Topic>` object: projects the raw field
/// name from the object value returned by [`topic_query_field`].
fn payload_field(field: (&String, &GraphqlType)) -> (Field, Vec<Object>) {
    let field_name = sanitize_to_graphql_name(field.0);
    let raw_name = Name::new(field.0.clone());
    let (graphql_type, objects) = graphql_type_ref(field.0, field.1);

    let field = Field::new(field_name, graphql_type, move |ctx| {
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
    });

    (field, objects)
}

/// Map a GraphQL type name to an async-graphql TypeRef.
fn graphql_type_ref(name: &str, typ: &GraphqlType) -> (TypeRef, Vec<Object>) {
    #[allow(clippy::match_same_arms)]
    match typ {
        GraphqlType::Float => (TypeRef::named(TypeRef::FLOAT), vec![]),
        GraphqlType::Int => (TypeRef::named(TypeRef::INT), vec![]),
        GraphqlType::Boolean => (TypeRef::named(TypeRef::BOOLEAN), vec![]),
        GraphqlType::String => (TypeRef::named(TypeRef::STRING), vec![]),
        GraphqlType::Object(fields) => {
            let objects = payload_object(name, fields);
            (TypeRef::named(objects[0].type_name()), objects)
        }
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
///
pub fn validate_topics(api: &Api) -> anyhow::Result<()> {
    let topics = api.topics();

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
fn validate_topic_fields(
    topic: &str,
    fields: &BTreeMap<String, GraphqlType>,
) -> anyhow::Result<()> {
    let mut seen_fields: BTreeMap<String, String> = BTreeMap::new();
    let mut seen_raw_fields: BTreeSet<String> = BTreeSet::new();
    for field_name in fields.keys() {
        // Raw duplicate (should also be caught by sanitized check, but give clearer error)
        if !seen_raw_fields.insert(field_name.clone()) {
            anyhow::bail!("duplicate field name '{field_name}' in topic '{topic}'");
        }
        let sanitized_field = sanitize_to_graphql_name(field_name);
        if sanitized_field.is_empty() {
            anyhow::bail!(
                "field '{field_name}' in topic '{topic}' sanitizes to an empty GraphQL name"
            );
        }
        if let Some(prev) = seen_fields.get(&sanitized_field) {
            anyhow::bail!(
                "duplicate sanitized field name '{sanitized_field}' in topic '{topic}' from fields '{prev}' and '{field_name}'"
            );
        }
        seen_fields.insert(sanitized_field, field_name.clone());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::ApiModel;
    use crate::http::router;
    use crate::topic_map::TopicMap;
    use axum::http::StatusCode;
    use tower::ServiceExt;

    fn api() -> Api {
        Api::new(vec![ApiModel::new(
            "".to_string(),
            TopicMap::new(),
            vec![],
            vec![],
            TopicMap::new(),
        )])
    }

    #[tokio::test]
    async fn test_health_endpoint() {
        let app = router(build_schema(&api(), &Arc::new(TopicCache::new())).unwrap());

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
}
