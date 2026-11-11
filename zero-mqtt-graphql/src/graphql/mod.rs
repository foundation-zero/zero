//! GraphQL schema for MQTT topics, topic groups, and buckets.
//!
//! # Terminology
//! Both kinds below are a `TopicDef`, told apart by its `TopicKind`.
//! - **Topic** (`TopicKind::Single`): a single concrete MQTT topic with no
//!   wildcards, e.g. `termodinamica/compressor/temperature`. Each topic
//!   maps to one sanitized GraphQL query field returning its cached payload.
//! - **Group** (`TopicKind::Group`): a parametrized topic family declared by one
//!   AsyncAPI channel whose address contains `{param}` placeholders, e.g.
//!   `power-tags/{panel}/{slug}` with MQTT topic filter `power-tags/+/+`. A group
//!   is enumerated by the x-group-topic-metadata extension listing its concrete topics and
//!   static attributes; the schema exposes one list query `<group>: [<Group>Topic]`
//!   (e.g. `powerTags: [SchemaPowerTagsTopic]`) whose rows merge that static metadata
//!   with live values from the cache.
//! - **Bucket**: a partition of a group's rows by the distinct value of the
//!   `group_by` metadata attribute declared in the group's metadata file. For
//!   example `group_by: "panel"` buckets `power-tags` rows into buckets `10P1`,
//!   `10P2`, … Each bucket exposes `{ id, <group>: [GroupTopic] }` and the
//!   schema exposes `<stem>Buckets: [Bucket]` (all buckets) and
//!   `<stem>Bucket(id: String): Bucket` (single bucket by id).

use std::collections::{BTreeMap, HashMap};
use std::sync::Arc;

use anyhow::{Context, bail};
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use async_graphql::dynamic::{Field, FieldValue, Object, Schema, TypeRef};
use log::{info, warn};
use serde_json::Value as JsonValue;

use crate::graphql::groups::register_group_queries;
use crate::graphql::topics::payload_query_field;
use crate::naming::{pascal_case_graphql_name, sanitize_to_graphql_name};
use crate::{
    api_model::{Api, FieldType, GraphqlPath, PathNode, QueryTree, TopicKind},
    cache::TopicCache,
};

mod groups;
mod topics;

/// Build a dynamic GraphQL schema from the Specs' Query trees and the cache.
///
/// Each Topic is a field at the GraphQL path its MQTT address gives, with a
/// payload object type named after its Spec. Errors when two Specs share a
/// root field or two different types get the same name; Path conflicts
/// within a Spec are found when it is loaded. Topics without payload fields
/// are left out.
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
///
/// Each Spec builds its own fields; `Query` combines their root fields. For
/// now Specs are assumed not to overlap: two Specs with the same root field
/// are a Path conflict. A Mount by Spec name at the root may lift this later.
pub fn build_schema(api: &Api, cache: &Arc<TopicCache>) -> anyhow::Result<Schema> {
    let query = Object::new("Query");

    let mut schema_builder = Schema::build(query.type_name(), None, None);

    let mut known_types: HashMap<String, Object> = HashMap::new();

    let mut root_specs: HashMap<&str, &str> = HashMap::new();
    let mut query_fields = Vec::new();
    for spec in &api.specs {
        for root in spec.query_tree.keys() {
            if let Some(other) = root_specs.insert(root, &spec.name) {
                bail!(
                    "GraphQL path conflict: Specs '{other}' and '{}' both have root field '{root}'",
                    spec.name
                );
            }
        }
        query_fields.extend(tree_fields(
            &spec.name,
            &GraphqlPath::default(),
            &spec.query_tree,
            cache,
            &mut known_types,
        )?);
    }
    if query_fields.is_empty() {
        bail!("Query has no queryable children!");
    }
    schema_builder = known_types
        .into_iter()
        .fold(schema_builder, |builder, (_, t)| builder.register(t));

    let query = query_fields.into_iter().fold(query, Object::field);

    schema_builder
        .register(query)
        .finish()
        .with_context(|| "Schema building failed")
}

/// The fields for one level of a Spec's tree, collecting the object types
/// they need into `known_types`. Payload types are named after `spec`.
fn tree_fields(
    spec: &str,
    parent_path: &GraphqlPath,
    children: &QueryTree,
    cache: &Arc<TopicCache>,
    known_types: &mut HashMap<String, Object>,
) -> anyhow::Result<Vec<Field>> {
    let fields: Vec<Field> = children
        .iter()
        .map(|(segment, node)| {
            let (fields, mut objects) = match node {
                PathNode::Branch(grandchildren) => {
                    let path = parent_path.child(segment);
                    let type_name = path_type_name(&path);
                    let fields = tree_fields(spec, &path, grandchildren, cache, known_types)?;
                    if fields.is_empty() {
                        warn!("Branch '{path}' has no queryable children, leaving it out");
                        return Ok(vec![]);
                    }
                    let branch = fields
                        .into_iter()
                        .fold(Object::new(type_name.as_str()), Object::field);

                    let field = branch_field(segment, &type_name);
                    (vec![field], vec![branch])
                }
                PathNode::Topic(topic) => {
                    info!("Building schema for topic {}", topic.topic);
                    let Some(payload) = topic.payload.as_ref() else {
                        warn!("Topic {} without payload, ignoring", topic.topic);
                        return Ok(vec![]);
                    };

                    if payload.name.is_empty() {
                        warn!("Topic {} would create an invalid payload type, ignoring", topic.topic);
                        return Ok(vec![]);
                    }

                    match &topic.kind {
                        TopicKind::Single => {
                            let payload_objects = payload_object(spec, &payload.name, &payload.fields);
                            let field = payload_query_field(
                                segment,
                                &topic.topic,
                                &payload_objects[0],
                                cache,
                            );
                            (vec![field], payload_objects)
                        }
                        TopicKind::Group(group) => register_group_queries(
                            segment,
                            &parent_path.child(segment),
                            &topic.topic,
                            payload,
                            group,
                            cache,
                        )?
                        .unwrap_or_else(|| (vec![], vec![])),
                    }
                }
            };

            for object in objects.drain(..) {
                let name = object.type_name().to_string();
                let object_string = format!("{object:?}" );
                if let Some(other) = known_types.insert(name.clone(), object) {
                    let other_string = format!("{other:?}" );

                    if object_string != other_string  {
                        bail!(
                            "GraphQL type name clash: '{name}' is used by both '{other_string}' and '{object_string}'"
                        );
                    }
                }
            }

            Ok(fields)
        })
        .collect::<anyhow::Result<Vec<_>>>()?.into_iter().flatten().collect();

    Ok(fields)
}

/// Type name of what sits at `path`: `Schema` plus the full path in
/// PascalCase (`marpower.freshWater` → `SchemaMarpowerFreshWater`). A
/// branch is named exactly this; a Group's types use it as a prefix.
fn path_type_name(path: &GraphqlPath) -> String {
    let base = pascal_case_graphql_name(
        &path
            .segments()
            .iter()
            .map(|s| s.trim_start_matches('_'))
            .collect::<Vec<&str>>()
            .join("-"),
    );
    format!("Schema{}", base.trim_start_matches('_'))
}

/// A branch field: resolves to an empty object so its children resolve.
fn branch_field(name: &str, type_name: &str) -> Field {
    Field::new(name, TypeRef::named(type_name), |_ctx| {
        async_graphql::dynamic::FieldFuture::new(async {
            Ok(Some(FieldValue::value(GraphQlValue::Object(
                async_graphql::indexmap::IndexMap::default(),
            ))))
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
fn payload_object(
    name_prefix: &str,
    name: &str,
    fields: &BTreeMap<String, FieldType>,
) -> Vec<Object> {
    if fields.is_empty() {
        warn!("Object {name} can't have zero fields!");
    }

    let type_name = pascal_case_graphql_name(&format!("{name_prefix}-{name}"));
    let (object, mut objects) = fields
        .iter()
        .filter_map(|(name, graphql_type)| payload_field(name_prefix, name, graphql_type))
        .fold(
            (Object::new(type_name.as_str()), Vec::new()),
            |(obj, mut objects), (field, new_objects)| {
                objects.extend(new_objects);
                (obj.field(field), objects)
            },
        );
    objects.insert(0, object);
    objects
}

/// One scalar payload field on a `<Topic>` object: projects the raw field
/// name from the object value returned by [`topic_query_field`].
fn payload_field(
    name_prefix: &str,
    name: &str,
    graphql_type: &FieldType,
) -> Option<(Field, Vec<Object>)> {
    let field_name = sanitize_to_graphql_name(name);

    if field_name.is_empty() {
        warn!("Skipping field '{name}' sanitizes to empty GraphQL name");
        return None;
    }

    let raw_name = Name::new(name);
    let (graphql_type, objects) = graphql_type_ref(name_prefix, graphql_type);

    let field = Field::new(field_name, graphql_type, move |ctx| {
        let raw_name = raw_name.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map.get(&raw_name).cloned(),
                _ => None,
            };
            Ok(non_null(value).map(FieldValue::value))
        })
    });

    Some((field, objects))
}

/// `value` unless it is missing or `null`. A resolver must return `None`
/// for those: `Some(Null)` on an object-typed field resolves the object
/// against a `null` parent, giving an object with only `null` fields.
fn non_null(value: Option<GraphQlValue>) -> Option<GraphQlValue> {
    value.filter(|value| *value != GraphQlValue::Null)
}

/// Map a GraphQL type name to an async-graphql TypeRef.
fn graphql_type_ref(name_prefix: &str, typ: &FieldType) -> (TypeRef, Vec<Object>) {
    #[allow(clippy::match_same_arms)]
    match typ {
        FieldType::Float => (TypeRef::named(TypeRef::FLOAT), vec![]),
        FieldType::Int => (TypeRef::named(TypeRef::INT), vec![]),
        FieldType::Boolean => (TypeRef::named(TypeRef::BOOLEAN), vec![]),
        FieldType::String => (TypeRef::named(TypeRef::STRING), vec![]),
        FieldType::Object(name, fields) => {
            let objects = payload_object(name_prefix, name, fields);
            (TypeRef::named(objects[0].type_name()), objects)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::{Direction, Payload, Spec, TopicDef};
    use crate::topic_map::TopicMap;
    use serde_json::json;

    fn spec(name: &str, topics: Vec<TopicDef>) -> Spec {
        Spec::new(name.to_string(), topics, TopicMap::new()).unwrap()
    }

    fn mock_api(topics: Vec<TopicDef>) -> Api {
        Api::new(vec![spec("", topics)])
    }

    /// Helper for a Send Topic with one Float field.
    fn mock_topic(topic: &str, field: &str) -> TopicDef {
        TopicDef {
            topic: topic.to_string(),
            payload: Some(Payload {
                name: format!("{field}payload"),
                fields: BTreeMap::from_iter(vec![(field.to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }
    }

    #[test_log::test]
    fn test_branch_types_are_named_after_their_full_graphql_path() {
        let topics = vec![mock_topic(
            "marpower/250000-fresh-water/cold/cold-flow",
            "x",
        )];

        let sdl = build_schema(&mock_api(topics), &Arc::new(TopicCache::new()))
            .unwrap()
            .sdl();
        assert!(sdl.contains("marpower: SchemaMarpower\n"), "{sdl}");
        assert!(
            sdl.contains("_250000FreshWater: SchemaMarpower250000FreshWater\n"),
            "{sdl}"
        );
        assert!(
            sdl.contains("cold: SchemaMarpower250000FreshWaterCold\n"),
            "{sdl}"
        );
    }

    #[test_log::test]
    fn test_wildcard_addresses_are_left_out_of_the_tree() {
        let topics = vec![
            mock_topic("logs/#", "x"),
            mock_topic("sensors/+/temp", "x"),
            mock_topic("a/b", "y"),
        ];

        let schema = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("logs"), "{sdl}");
        assert!(!sdl.contains("sensors"), "{sdl}");
        assert!(sdl.contains("a: SchemaA"), "{sdl}");
    }

    #[test_log::test]
    fn test_branch_type_name_clashing_with_a_payload_type_errors() {
        // Payload type of `aB/c` is `SchemaA`; the branch at `a/b` is also `SchemaA`.
        let topics = vec![
            mock_topic("a/b", "x"),
            TopicDef {
                topic: "aB/c".to_string(),
                payload: Some(Payload {
                    name: "schema-a".to_string(),
                    fields: BTreeMap::from_iter(vec![("field".to_string(), FieldType::Float)]),
                }),
                operation: Direction::Send,
                ttl_secs: None,
                kind: TopicKind::Single,
            },
        ];

        let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert!(
            err.to_string()
                .contains("GraphQL type name clash: 'SchemaA' is used by both"),
        );
    }

    #[test_log::test]
    fn test_two_branches_with_the_same_type_name_error() {
        // The branch at `aB` and the branch at `a/b` are both named `SchemaAB`.
        let topics = vec![mock_topic("aB/x/y", "v"), mock_topic("a/b/y/z", "v")];

        let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert!(
            err.to_string()
                .contains("GraphQL type name clash: 'SchemaAB' is used by both"),
        );
    }

    #[test_log::test]
    fn test_address_level_without_a_graphql_name_ok() {
        for address in ["/a/b", "a//b", "a/-/b"] {
            let topics = vec![mock_topic(address, "v")];

            let schema = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap();
            let sdl = schema.sdl();
            assert!(sdl.contains("a: SchemaA"), "{sdl}");
            assert!(sdl.contains("b: Vpayload"), "{sdl}");
        }
    }

    #[test_log::test]
    fn test_specs_sharing_a_root_field_conflict() {
        let api = Api::new(vec![
            spec("one", vec![mock_topic("thrs/controller/pcm", "x")]),
            spec("two", vec![mock_topic("thrs/simulator/step", "y")]),
        ]);

        let err = build_schema(&api, &Arc::new(TopicCache::new())).unwrap_err();
        assert_eq!(
            err.to_string(),
            "GraphQL path conflict: Specs 'one' and 'two' both have root field 'thrs'"
        );
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_specs_combine_into_one_query() {
        let api = Api::new(vec![
            spec("one", vec![mock_topic("thrs/controller/pcm", "x")]),
            spec("two", vec![mock_topic("simulator/step", "y")]),
        ]);
        let cache = Arc::new(TopicCache::new());
        cache.insert("thrs/controller/pcm", json!({"x": 1.0}));
        cache.insert("simulator/step", json!({"y": 2.0}));
        let schema = build_schema(&api, &cache).unwrap();

        let response = schema
            .execute("{ thrs { controller { pcm { x } } } simulator { step { y } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["thrs"]["controller"]["pcm"]["x"], json!(1.0));
        assert_eq!(data["simulator"]["step"]["y"], json!(2.0));
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_null_or_missing_nested_object_is_null() {
        let topic = TopicDef {
            topic: "a/b".to_string(),
            payload: Some(Payload {
                name: "payload".to_string(),
                fields: BTreeMap::from([
                    (
                        "inner".to_string(),
                        FieldType::Object(
                            "inner".to_string(),
                            Box::new(BTreeMap::from([("x".to_string(), FieldType::Float)])),
                        ),
                    ),
                    ("y".to_string(), FieldType::Float),
                ]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        };
        let schema_with = |payload| {
            let cache = Arc::new(TopicCache::new());
            cache.insert("a/b", payload);
            build_schema(&mock_api(vec![topic.clone()]), &cache).unwrap()
        };

        for payload in [json!({"inner": null, "y": 1.0}), json!({"y": 1.0})] {
            let response = schema_with(payload.clone())
                .execute("{ a { b { inner { x } y } } }")
                .await;
            assert!(response.errors.is_empty(), "{:?}", response.errors);
            let data: serde_json::Value = response.data.into_json().unwrap();
            assert_eq!(
                data["a"]["b"],
                json!({"inner": null, "y": 1.0}),
                "for {payload}"
            );
        }
    }
}
