use std::sync::Arc;

use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{Field, FieldValue, TypeRef};

use crate::cache::TopicCache;
use crate::graphql::non_null;

/// The `<Topic>` query field, of the payload object type `type_name`:
/// resolves to the topic's whole cached MQTT payload object. The object's
/// scalar subfields project from this value (see [`payload_field`]), so the
/// payload is read from the cache exactly once per query.
pub(super) fn payload_query_field(
    name: &str,
    topic: &str,
    type_name: &str,
    cache: &Arc<TopicCache>,
) -> Field {
    let obj_ref = TypeRef::named(type_name);
    let topic = topic.to_string();
    let cache_for_query = cache.clone();
    Field::new(name, obj_ref, move |_ctx| {
        let val = cache_for_query.get(&topic);
        async_graphql::dynamic::FieldFuture::new(async move {
            let value = val.map(GraphQlValue::from_json).transpose()?;
            Ok(non_null(value))
        })
    })
}

/// The `<Topic>` query field of a payload of several formats, of the union
/// `type_name`: resolves to the cached payload as the arm its `discriminator`
/// names, with `arms` giving each arm's value and object type. A payload
/// without a known value is a field error, so a publisher that no longer
/// matches the Spec shows.
pub(super) fn union_query_field(
    name: &str,
    topic: &str,
    type_name: &str,
    discriminator: String,
    arms: Vec<(Option<serde_json::Value>, String)>,
    cache: &Arc<TopicCache>,
) -> Field {
    let topic = topic.to_string();
    let union_name = type_name.to_string();
    let cache = cache.clone();
    Field::new(name, TypeRef::named(type_name), move |_ctx| {
        let value = cache.get(&topic).filter(|value| !value.is_null());
        let discriminator = discriminator.clone();
        let arms = arms.clone();
        let union_name = union_name.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let Some(value) = value else {
                return Ok(None);
            };
            let found = value.get(&discriminator).cloned();
            let (_, arm_type) = arms
                .into_iter()
                .find(|(arm_value, _)| *arm_value == found)
                .ok_or_else(|| {
                    format!("{discriminator} {found:?} is not one of the formats of {union_name}")
                })?;
            let value = GraphQlValue::from_json(value)?;
            Ok(Some(FieldValue::with_type(
                FieldValue::value(value),
                arm_type,
            )))
        })
    })
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::api_model::{Api, Arm, Direction, FieldType, Payload, Spec, TopicDef, TopicKind};
    use crate::graphql::build_schema;
    use crate::http::router;
    use crate::topic_map::TopicMap;
    use axum::http::StatusCode;
    use serde_json::json;
    use tower::ServiceExt;

    fn api(topics: Vec<TopicDef>) -> Api {
        Api::new(vec![
            Spec::new(String::new(), topics, TopicMap::new()).unwrap(),
        ])
    }

    #[test_log::test]
    fn test_build_schema_for_one_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![
                    ("value".to_string(), FieldType::Float),
                    ("ok".to_string(), FieldType::Boolean),
                ]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        let _schema = build_schema(&api(topics), &cache, None).unwrap();
        // Schema builds without panicking
    }

    #[test_log::test]
    fn test_digit_prefixed_topic_is_valid() {
        let topics = vec![TopicDef {
            topic: "123/topic".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("x".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new()), None).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("Query123"), "{sdl}");
    }

    #[test_log::test]
    fn test_empty_topic_is_listed_but_not_queryable() {
        // A topic without scalar fields must not crash schema building;
        // it stays visible via `topics` but has no query type.
        let topics = vec![TopicDef {
            topic: "empty/topic".to_string(),
            payload: Some(Payload::object("payload", BTreeMap::new())),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let err = build_schema(&api(topics), &Arc::new(TopicCache::new()), None).unwrap_err();
        assert!(err.to_string().contains("Query has no queryable children"));
    }

    #[test_log::test]
    fn test_field_types_in_schema() {
        let topics = vec![TopicDef {
            topic: "t".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![
                    ("f_float".to_string(), FieldType::Float),
                    ("f_int".to_string(), FieldType::Int),
                    ("f_bool".to_string(), FieldType::Boolean),
                    ("f_str".to_string(), FieldType::String),
                ]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new()), None).unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("fFloat: Float"), "{sdl}");
        assert!(sdl.contains("fInt: Int"), "{sdl}");
        assert!(sdl.contains("fBool: Boolean"), "{sdl}");
        assert!(sdl.contains("fStr: String"), "{sdl}");
    }

    /// `sim/inputs`, one of a `Pvt` and a `Dhw`, told apart by `Kind`.
    fn union_topic() -> TopicDef {
        let arm = |name: &str, value: &str, field: &str| Arm {
            name: name.to_string(),
            value: Some(json!(value)),
            fields: BTreeMap::from([
                ("Kind".to_string(), FieldType::String),
                (field.to_string(), FieldType::Float),
            ]),
        };
        TopicDef {
            topic: "sim/inputs".to_string(),
            payload: Some(Payload {
                name: "Inputs".to_string(),
                discriminator: Some("Kind".to_string()),
                arms: vec![arm("Pvt", "pvt", "panels"), arm("Dhw", "dhw", "tank")],
            }),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }
    }

    const UNION_QUERY: &str =
        "{ sim { inputs { __typename ... on Pvt { panels } ... on Dhw { tank } } } }";

    #[tokio::test]
    #[test_log::test]
    async fn test_union_payload_resolves_to_the_arm_its_discriminator_names() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("sim/inputs", json!({"Kind": "dhw", "tank": 55.0}));
        let schema = build_schema(&api(vec![union_topic()]), &cache, None).unwrap();

        assert!(
            schema.sdl().contains("union Inputs = Pvt | Dhw"),
            "{}",
            schema.sdl()
        );
        let response = schema.execute(UNION_QUERY).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(
            data["sim"]["inputs"],
            json!({"__typename": "Dhw", "tank": 55.0})
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_union_payload_without_a_known_discriminator_is_an_error() {
        let cache = Arc::new(TopicCache::new());
        cache.insert("sim/inputs", json!({"Kind": "thrs", "tank": 55.0}));
        let schema = build_schema(&api(vec![union_topic()]), &cache, None).unwrap();

        let response = schema.execute(UNION_QUERY).await;
        assert_eq!(response.errors.len(), 1, "{:?}", response.errors);
        assert!(
            response.errors[0]
                .message
                .contains("is not one of the formats of Inputs"),
            "{:?}",
            response.errors
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_union_payload_without_a_value_is_null() {
        let schema = build_schema(
            &api(vec![union_topic()]),
            &Arc::new(TopicCache::new()),
            None,
        )
        .unwrap();

        let response = schema.execute(UNION_QUERY).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["sim"]["inputs"], json!(null));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![
                    ("value".to_string(), FieldType::Float),
                    ("ok".to_string(), FieldType::Boolean),
                    ("label".to_string(), FieldType::String),
                ]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "test/channel",
            json!({"value": 23.5, "ok": true, "label": "hello"}),
        );
        let schema = build_schema(&api(topics), &cache, None).unwrap();

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
    async fn test_query_returns_integers_above_i64_exactly() {
        // A `JSON` field, as `Int` is 32-bit and `Float` would round.
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from([("counter".to_string(), FieldType::Json)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"counter": u64::MAX}));
        let schema = build_schema(&api(topics), &cache, None).unwrap();

        let response = schema.execute("{ test { channel { counter } } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["test"]["channel"]["counter"], json!(u64::MAX));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_null_for_missing_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new()), None).unwrap();

        let response = schema.execute("{ test { channel { value } } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["test"]["channel"], json!(null));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_returns_null_for_null_payload() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!(null));
        let schema = build_schema(&api(topics), &cache, None).unwrap();

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
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"other": 1.0}));
        let schema = build_schema(&api(topics), &cache, None).unwrap();

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
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let schema = build_schema(&api(topics), &Arc::new(TopicCache::new()), None).unwrap();

        let response = schema.execute("{ test { channel { nope } } }").await;
        assert_ne!(response.errors, []);
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_query_multiple_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                payload: Some(Payload::object(
                    "payload1",
                    BTreeMap::from_iter(vec![("x".to_string(), FieldType::Float)]),
                )),
                operation: Direction::Send,
                ttl_secs: None,
                setter: None,
                kind: TopicKind::Single,
            },
            TopicDef {
                topic: "a/c".to_string(),
                payload: Some(Payload::object(
                    "payload2",
                    BTreeMap::from_iter(vec![("y".to_string(), FieldType::Float)]),
                )),
                operation: Direction::Send,
                ttl_secs: None,
                setter: None,
                kind: TopicKind::Single,
            },
        ];

        let cache = Arc::new(TopicCache::new());
        cache.insert("a/b", json!({"x": 1.5}));
        cache.insert("a/c", json!({"y": 2.5}));
        let schema = build_schema(&api(topics), &cache, None).unwrap();

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
            payload: Some(Payload::object(
                "payload",
                BTreeMap::from_iter(vec![("value".to_string(), FieldType::Float)]),
            )),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"value": 42.0}));
        let app = router(build_schema(&api(topics), &cache, None).unwrap());

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
