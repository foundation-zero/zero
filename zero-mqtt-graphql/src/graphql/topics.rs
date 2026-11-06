use std::sync::Arc;

use async_graphql::dynamic::{Field, Object, TypeRef};

use crate::cache::TopicCache;
use crate::graphql::json_to_graphql_value;

/// The `<Topic>` query field: resolves to the topic's whole cached MQTT
/// payload object. The object's scalar subfields project from this value
/// (see [`payload_field`]), so the payload is read from the cache exactly
/// once per query.
pub(super) fn payload_query_field(
    name: &str,
    topic: &str,
    graphql_type: &Object,
    cache: &Arc<TopicCache>,
) -> Field {
    let obj_ref = TypeRef::named(graphql_type.type_name());
    let topic = topic.to_string();
    let cache_for_query = cache.clone();
    Field::new(name, obj_ref, move |_ctx| {
        let val = cache_for_query.get(&topic);
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(val.map(|json_val| json_to_graphql_value(&json_val)))
        })
    })
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::api_model::{Api, Direction, FieldType, Payload, Spec, TopicDef, TopicKind};
    use crate::graphql::build_schema;
    use crate::http::router;
    use crate::topic_map::TopicMap;
    use axum::http::StatusCode;
    use serde_json::json;
    use tower::ServiceExt;

    fn api(topics: Vec<TopicDef>) -> Api {
        Api::new(vec![
            Spec::new(String::new(), TopicMap::new(), topics, TopicMap::new()).unwrap(),
        ])
    }

    #[test_log::test]
    fn test_build_schema_for_one_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![
                    ("value".to_string(), FieldType::Float),
                    ("ok".to_string(), FieldType::Boolean),
                ]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        let _schema = build_schema(&api(topics), &cache).unwrap();
        // Schema builds without panicking
    }

    #[test_log::test]
    fn test_digit_prefixed_topic_is_valid() {
        let topics = vec![TopicDef {
            topic: "123/topic".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![("x".to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("Schema123"), "{sdl}");
    }

    #[test_log::test]
    fn test_empty_topic_is_listed_but_not_queryable() {
        // A topic without scalar fields must not crash schema building;
        // it stays visible via `topics` but has no query type.
        let topics = vec![TopicDef {
            topic: "empty/topic".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::new(),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let err = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert!(err.to_string().contains("Query has no queryable children!"));
    }

    #[test_log::test]
    fn test_field_types_in_schema() {
        let topics = vec![TopicDef {
            topic: "t".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![
                    ("f_float".to_string(), FieldType::Float),
                    ("f_int".to_string(), FieldType::Int),
                    ("f_bool".to_string(), FieldType::Boolean),
                    ("f_str".to_string(), FieldType::String),
                ]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("fFloat: Float"), "{sdl}");
        assert!(sdl.contains("fInt: Int"), "{sdl}");
        assert!(sdl.contains("fBool: Boolean"), "{sdl}");
        assert!(sdl.contains("fStr: String"), "{sdl}");
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![
                    ("value".to_string(), FieldType::Float),
                    ("ok".to_string(), FieldType::Boolean),
                    ("label".to_string(), FieldType::String),
                ]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "test/channel",
            json!({"value": 23.5, "ok": true, "label": "hello"}),
        );
        let schema = build_schema(&api(topics), &cache).unwrap();

        let response = schema
            .execute("{ test { channel { value ok label } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["test"]["channel"]["value"], json!(23.5));
        assert_eq!(data["test"]["channel"]["ok"], json!(true));
        assert_eq!(data["test"]["channel"]["label"], json!("hello"));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_null_for_missing_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();

        let response = schema.execute("{ test { channel { value } } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["test"]["channel"], json!(null));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_null_for_missing_field() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"other": 1.0}));
        let schema = build_schema(&api(topics), &cache).unwrap();

        let response = schema.execute("{ test { channel { value } } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["test"]["channel"]["value"], json!(null));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_unknown_field_errors() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new())).unwrap();

        let response = schema.execute("{ test { channel { nope } } }").await;
        assert_ne!(response.errors, []);
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_multiple_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                payload: Some(Payload {
                    name: "payload1".to_string(),
                    fields: BTreeMap::from_iter(vec![("x".to_string(), FieldType::Float)]),
                }),
                operation: Direction::Send,
                ttl_secs: None,
                kind: TopicKind::Single,
            },
            TopicDef {
                topic: "a/c".to_string(),
                payload: Some(Payload {
                    name: "payload2".to_string(),
                    fields: BTreeMap::from_iter(vec![("y".to_string(), FieldType::Float)]),
                }),
                operation: Direction::Send,
                ttl_secs: None,
                kind: TopicKind::Single,
            },
        ];

        let cache = Arc::new(TopicCache::new());
        cache.insert("a/b", json!({"x": 1.5}));
        cache.insert("a/c", json!({"y": 2.5}));
        let schema = build_schema(&api(topics), &cache).unwrap();

        // Topics sharing a prefix share one branch.
        let response = schema.execute("{ a { b { x } c { y } } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["a"]["b"]["x"], json!(1.5));
        assert_eq!(data["a"]["c"]["y"], json!(2.5));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_graphql_endpoint_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"value": 42.0}));
        let app = router(build_schema(&api(topics), &cache).unwrap());

        let request = axum::http::Request::builder()
            .method("POST")
            .uri("/graphql")
            .header("content-type", "application/json")
            .body(axum::body::Body::from(
                r#"{"query": "{ test { channel { value } } }"}"#,
            ))
            .unwrap();

        let response = app.oneshot(request).await.unwrap();
        assert_eq!(response.status(), StatusCode::OK);

        let body = axum::body::to_bytes(response.into_body(), 1024 * 1024)
            .await
            .unwrap();
        let data: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert_eq!(data["data"]["test"]["channel"]["value"], json!(42.0));
    }
}
