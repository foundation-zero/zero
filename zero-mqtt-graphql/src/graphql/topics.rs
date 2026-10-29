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

use std::collections::BTreeSet;
use std::sync::Arc;

use crate::api_model::GraphqlType;
use crate::graphql::graphql_type_ref;
use crate::graphql::json_to_graphql_value;
use crate::roas_asyncapi::OperationAction;
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{Field, FieldValue, Object, TypeRef};
use log::info;

use crate::naming::sanitize_to_graphql_name;
use crate::{
    api_model::{ApiModel, TopicDef},
    cache::TopicCache,
};

pub(super) fn build_schema_topics(
    mut schema_object: Object,
    api: &ApiModel,
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
) -> (Object, Vec<Object>) {
    let topics = &api.topics;

    let mut objects = Vec::with_capacity(topics.len());

    for topic_def in queryable_topics(topics) {
        info!("Building schema for topic {}", topic_def.topic);
        let object_type = topic_object(topic_def);

        let field_name = object_type.type_name();
        let field = topic_query_field(&topic_def.topic, &field_name, cache);

        used_query_fields.insert(field_name.to_string());
        objects.push(object_type);
        schema_object = schema_object.field(field);
    }

    (schema_object, objects)
}

/// Topics eligible for a queryable payload object: those with fields.
fn queryable_topics(topics: &[TopicDef]) -> impl Iterator<Item = &TopicDef> {
    topics.iter().filter(|topic_def| {
        !topic_def.fields.is_empty() && topic_def.action == OperationAction::Send
    })
}

/// One concrete topic's `<Topic>` payload object, plus the additive
/// `metadata { … }` field when the topic is annotated in the metadata store.
fn topic_object(topic_def: &TopicDef) -> Object {
    let type_name = sanitize_to_graphql_name(&topic_def.topic);
    topic_def
        .fields
        .iter()
        .map(payload_field)
        .fold(Object::new(type_name.as_str()), |obj, field| {
            obj.field(field)
        })
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
fn payload_field(field: (&String, &GraphqlType)) -> Field {
    let field_name = sanitize_to_graphql_name(field.0);
    let raw_name = Name::new(field.0.clone());
    Field::new(field_name, graphql_type_ref(field.1), move |ctx| {
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
    })
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::api_model::{Api, ApiModel};
    use crate::graphql::build_schema;
    use crate::http::router;
    use crate::roas_asyncapi::OperationAction;
    use crate::topic_map::TopicMap;
    use axum::http::StatusCode;
    use serde_json::json;
    use tower::ServiceExt;

    fn api(topics: Vec<TopicDef>) -> Api {
        Api::new(vec![ApiModel::new(
            "".to_string(),
            TopicMap::new(),
            topics,
            vec![],
            TopicMap::new(),
        )])
    }

    #[test_log::test]
    fn test_build_schema_for_one_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: BTreeMap::from_iter(vec![
                ("value".to_string(), GraphqlType::Float),
                ("ok".to_string(), GraphqlType::Boolean),
            ]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        let _schema = build_schema(&api(topics), &cache).unwrap();
        // Schema builds without panicking
    }

    #[test_log::test]
    fn test_colliding_sanitized_topics_error() {
        // "a/b" and "a-b" both sanitize to "a_b" — should error rather than suffix
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: BTreeMap::from_iter(vec![("x".to_string(), GraphqlType::Float)]),
                payload_schema_ref: None,
                action: OperationAction::Send,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "a-b".to_string(),
                fields: BTreeMap::from_iter(vec![("y".to_string(), GraphqlType::Float)]),
                payload_schema_ref: None,
                action: OperationAction::Send,
                ttl_secs: 300,
            },
        ];

        let err = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert!(
            err.to_string().contains("duplicate sanitized topic name"),
            "{err}"
        );
    }

    #[test_log::test]
    fn test_reserved_topic_name_errors() {
        let topics = vec![TopicDef {
            topic: "Query".to_string(),
            fields: BTreeMap::from_iter(vec![("x".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let err = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert!(err.to_string().contains("reserved"), "{err}");
    }

    #[test_log::test]
    fn test_digit_prefixed_topic_is_valid() {
        let topics = vec![TopicDef {
            topic: "123/topic".to_string(),
            fields: BTreeMap::from_iter(vec![("x".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("_123Topic"), "{sdl}");
    }

    #[test_log::test]
    fn test_empty_topic_is_listed_but_not_queryable() {
        // A topic without scalar fields must not crash schema building;
        // it stays visible via `topics` but has no query type.
        let topics = vec![TopicDef {
            topic: "empty/topic".to_string(),
            fields: BTreeMap::new(),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("emptyTopic"), "{sdl}");
    }

    #[test_log::test]
    fn test_field_types_in_schema() {
        let topics = vec![TopicDef {
            topic: "t".to_string(),
            fields: BTreeMap::from_iter(vec![
                ("f_float".to_string(), GraphqlType::Float),
                ("f_int".to_string(), GraphqlType::Int),
                ("f_bool".to_string(), GraphqlType::Boolean),
                ("f_str".to_string(), GraphqlType::String),
            ]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("fFloat: Float"), "{sdl}");
        assert!(sdl.contains("fInt: Int"), "{sdl}");
        assert!(sdl.contains("fBool: Boolean"), "{sdl}");
        assert!(sdl.contains("fStr: String"), "{sdl}");
    }

    #[tokio::test]
    async fn test_query_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: BTreeMap::from_iter(vec![
                ("value".to_string(), GraphqlType::Float),
                ("ok".to_string(), GraphqlType::Boolean),
                ("label".to_string(), GraphqlType::String),
            ]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "test/channel",
            json!({"value": 23.5, "ok": true, "label": "hello"}),
        );
        let schema = build_schema(&api(topics), &cache).unwrap();

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
            fields: BTreeMap::from_iter(vec![("value".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"], json!(null));
    }

    #[tokio::test]
    async fn test_query_returns_null_for_missing_field() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: BTreeMap::from_iter(vec![("value".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"other": 1.0}));
        let schema = build_schema(&api(topics), &cache).unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"]["value"], json!(null));
    }

    #[tokio::test]
    async fn test_query_unknown_field_errors() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: BTreeMap::from_iter(vec![("value".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();

        let response = schema.execute("{ testChannel { nope } }").await;
        assert!(!response.errors.is_empty());
    }

    #[tokio::test]
    async fn test_query_multiple_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: BTreeMap::from_iter(vec![("x".to_string(), GraphqlType::Float)]),
                payload_schema_ref: None,
                action: OperationAction::Send,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "c/d".to_string(),
                fields: BTreeMap::from_iter(vec![("y".to_string(), GraphqlType::Float)]),
                payload_schema_ref: None,
                action: OperationAction::Send,
                ttl_secs: 300,
            },
        ];

        let cache = Arc::new(TopicCache::new());
        cache.insert("a/b", json!({"x": 1.5}));
        cache.insert("c/d", json!({"y": 2.5}));
        let schema = build_schema(&api(topics), &cache).unwrap();

        let response = schema.execute("{ aB { x } cD { y } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["aB"]["x"], json!(1.5));
        assert_eq!(data["cD"]["y"], json!(2.5));
    }

    #[tokio::test]
    async fn test_graphql_endpoint_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: BTreeMap::from_iter(vec![("value".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"value": 42.0}));
        let app = router(build_schema(&api(topics), &cache).unwrap());

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
