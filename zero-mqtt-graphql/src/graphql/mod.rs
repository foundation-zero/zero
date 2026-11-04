//! GraphQL schema for MQTT topics, topic groups, and buckets.
//!
//! # Terminology
//! - **Topic** (`TopicDef`): a single concrete MQTT topic with a fixed address
//!   and no wildcards, e.g. `termodinamica/compressor/temperature`. Each topic
//!   maps to one sanitized GraphQL query field returning its cached payload.
//! - **Group** (`TopicGroupDef`): a parametrized topic family declared by one
//!   AsyncAPI channel whose address contains `{param}` placeholders, e.g.
//!   `power-tags/{panel}/{slug}` with MQTT pattern `power-tags/+/+`. A group
//!   is enumerated by the x-group-topic-metadata extension listing its concrete topics and
//!   static attributes; the schema exposes one list query `<group>: [<Group>Topic]`
//!   (e.g. `powerTags: [PowerTagsTopic]`) whose rows merge that static metadata
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

use crate::graphql::graphql_path::GraphqlPath;
use crate::graphql::groups::register_group_queries;
use crate::graphql::topics::{payload_query_field, queryable_topic};
pub use crate::graphql::tree::{PathNode, graphql_tree};
use crate::naming::{pascal_case_graphql_name, sanitize_to_graphql_name};
use crate::{
    api_model::{Api, GraphqlType},
    cache::TopicCache,
};

mod graphql_path;
mod groups;
mod topics;
mod tree;

/// Build a dynamic GraphQL schema from topic definitions and the cache.
///
/// Sanitizes topic names to valid GraphQL identifiers and validates that no
/// two topics collide after sanitization. Returns an error if any sanitized
/// name is empty, duplicates another topic, or collides with a reserved
/// GraphQL name. Topics without scalar fields are not registered as query
/// types.
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
    let query = Object::new("Query");

    let mut schema_builder = Schema::build(query.type_name(), None, None);

    let mut known_types: HashMap<String, Object> = HashMap::new();

    let tree = graphql_tree(api)?;

    let query_fields = tree_fields(&GraphqlPath::default(), &tree, cache, &mut known_types)?;
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

/// The fields for one level of the tree, collecting the object types they
/// need into `known_types`.
fn tree_fields(
    parent_path: &GraphqlPath,
    children: &BTreeMap<String, PathNode<'_>>,
    cache: &Arc<TopicCache>,
    known_types: &mut HashMap<String, Object>,
) -> anyhow::Result<Vec<Field>> {
    let fields: Vec<Field> = children
        .iter()
        .map(|(segment, node)| {
            let (fields, mut objects) = match node {
                PathNode::Branch(grandchildren) => {
                    let path = parent_path.child(segment);
                    let type_name = path.type_name();
                    let fields = tree_fields(&path, grandchildren, cache, known_types)?;
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
                PathNode::Topic { spec, topic } => {
                    info!("Building schema for topic {}", topic.topic);
                    let Some(payload_schema_ref) = topic.payload_schema_ref.as_ref() else {
                        warn!("Topic {} without payload, ignoring", topic.topic);
                        return Ok(vec![]);
                    };

                    let name = payload_schema_ref.replace("#/components/schemas/", "");
                    if name.is_empty() {
                        warn!(
                            "Topic {} would create an invalid payload type, ignoring",
                            topic.topic
                        );
                        return Ok(vec![]);
                    }

                    let payload_objects = payload_object(spec, &name, &topic.fields);
                    let field =
                        payload_query_field(segment, &topic.topic, &payload_objects[0], cache);
                    (vec![field], payload_objects)
                }
                PathNode::Group { spec: _, group } => {
                    info!("Building schema for group {}", group.pattern);
                    let Some(payload_schema_ref) = group.payload_schema_ref.as_ref() else {
                        warn!("Group {} without payload, ignoring", group.pattern);
                        return Ok(vec![]);
                    };

                    let name = payload_schema_ref.replace("#/components/schemas/", "");
                    if name.is_empty() {
                        warn!("Group {} would create an invalid payload type, ignoring", group.pattern);
                        return Ok(vec![]);
                    }
                    let (fields, objects) = register_group_queries( group, cache)?.unwrap_or_else(|| (vec![], vec![])) ;
                    (fields, objects)
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
    fields: &BTreeMap<String, GraphqlType>,
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
    graphql_type: &GraphqlType,
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
                GraphQlValue::Object(map) => {
                    map.get(&raw_name).cloned().unwrap_or(GraphQlValue::Null)
                }
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    });

    Some((field, objects))
}

/// Map a GraphQL type name to an async-graphql TypeRef.
fn graphql_type_ref(name_prefix: &str, typ: &GraphqlType) -> (TypeRef, Vec<Object>) {
    #[allow(clippy::match_same_arms)]
    match typ {
        GraphqlType::Float => (TypeRef::named(TypeRef::FLOAT), vec![]),
        GraphqlType::Int => (TypeRef::named(TypeRef::INT), vec![]),
        GraphqlType::Boolean => (TypeRef::named(TypeRef::BOOLEAN), vec![]),
        GraphqlType::String => (TypeRef::named(TypeRef::STRING), vec![]),
        GraphqlType::Object(name, fields) => {
            let objects = payload_object(name_prefix, name, fields);
            (TypeRef::named(objects[0].type_name()), objects)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::{ApiModel, TopicDef};
    use crate::roas_asyncapi::OperationAction;
    use crate::topic_map::TopicMap;
    use serde_json::json;

    fn mock_api(topics: Vec<TopicDef>) -> Api {
        Api::new(vec![ApiModel::new(
            String::new(),
            TopicMap::new(),
            topics,
            vec![],
            TopicMap::new(),
        )])
    }

    /// Helper for a Send Topic with one Float field.
    fn mock_topic(topic: &str, field: &str) -> TopicDef {
        TopicDef {
            topic: topic.to_string(),
            fields: BTreeMap::from_iter(vec![(field.to_string(), GraphqlType::Float)]),
            payload_schema_ref: Some(format!("#/components/schemas/{field}payload")),
            action: OperationAction::Send,
            ttl_secs: None,
        }
    }

    #[test_log::test]
    fn test_topics_on_the_same_graphql_path_conflict() {
        // `b-c` and `b_c` both sanitize to `bC`.
        let topics = vec![mock_topic("a/b-c", "x"), mock_topic("a/b_c", "y")];

        let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap_err();
        assert_eq!(
            err.to_string(),
            "GraphQL path conflict: topic 'a/b_c' conflicts with topic 'a/b-c'"
        );
    }

    #[test_log::test]
    fn test_topic_that_is_also_a_parent_conflicts_in_either_order() {
        for topics in [
            vec![mock_topic("a/b", "x"), mock_topic("a/b/c", "y")],
            vec![mock_topic("a/b/c", "y"), mock_topic("a/b", "x")],
        ] {
            let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap_err();
            assert_eq!(
                err.to_string(),
                "GraphQL path conflict: topic 'a/b' conflicts with topic 'a/b/c'"
            );
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
                fields: BTreeMap::from_iter(vec![("field".to_string(), GraphqlType::Float)]),
                payload_schema_ref: Some("#/components/schemas/schema-a".to_string()),
                action: OperationAction::Send,
                ttl_secs: None,
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
    fn test_address_empty_errors() {
        for address in ["//", ""] {
            let topics = vec![mock_topic(address, "v")];

            let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new())).unwrap_err();
            assert_eq!(
                err.to_string(),
                format!("topic '{address}' would result in an empty GraphQL name")
            );
        }
    }

    fn spec(name: &str, topics: Vec<TopicDef>) -> ApiModel {
        ApiModel::new(
            name.to_string(),
            TopicMap::new(),
            topics,
            vec![],
            TopicMap::new(),
        )
    }

    #[tokio::test]
    #[test_log::test]
    async fn test_specs_sharing_a_prefix_merge_into_one_branch() {
        let api = Api::new(vec![
            spec("one", vec![mock_topic("thrs/controller/pcm", "x")]),
            spec("two", vec![mock_topic("thrs/simulator/step", "y")]),
        ]);
        let cache = Arc::new(TopicCache::new());
        cache.insert("thrs/controller/pcm", json!({"x": 1.0}));
        cache.insert("thrs/simulator/step", json!({"y": 2.0}));
        let schema = build_schema(&api, &cache).unwrap();

        let response = schema
            .execute("{ thrs { controller { pcm { x } } simulator { step { y } } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["thrs"]["controller"]["pcm"]["x"], json!(1.0));
        assert_eq!(data["thrs"]["simulator"]["step"]["y"], json!(2.0));
    }
}
