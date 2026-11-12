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
//!   (e.g. `powerTags: [QueryPowerTagsTopic]`) whose rows merge that static metadata
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
use async_graphql::dynamic::{
    Enum, Field, FieldValue, Object, Scalar, Schema, SchemaBuilder, Type, TypeRef,
};
use log::{info, warn};

use crate::graphql::groups::register_group_queries;
pub use crate::graphql::mutations::{Mutations, PublishFuture, Publisher};
use crate::graphql::mutations::{equal_value, mutation_leaf};
use crate::graphql::topics::payload_query_field;
use crate::naming::{pascal_case_graphql_name, sanitize_to_graphql_name};
use crate::{
    api_model::{
        Api, Direction, EnumValue, FieldType, GraphqlPath, PathNode, TopicDef, TopicKind, Tree,
    },
    cache::TopicCache,
};

mod groups;
mod mutations;
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
///
/// With `mutations`, the schema also has a Mutation tree of the Receive
/// Topics, which publishes through it. A Receive Topic with a State topic
/// returns that topic's value once it shows the input; one without returns
/// `Boolean!`.
pub fn build_schema(
    api: &Api,
    cache: &Arc<TopicCache>,
    mutations: Option<&Mutations>,
) -> anyhow::Result<Schema> {
    check_root_fields(api)?;
    let mut known_types = HashMap::new();

    let query = root(
        "Query",
        api,
        &mut |spec, segment, path, topic| query_leaf(spec, segment, path, topic, cache),
        &mut known_types,
    )?;
    let Some(query) = query else {
        bail!(
            "Query has no queryable children: GraphQL needs at least one, even when there are Mutations"
        );
    };

    let mutation = match mutations {
        Some(mutations) => root(
            "Mutation",
            api,
            &mut |spec, segment, path, topic| {
                Ok(mutation_leaf(spec, segment, path, topic, cache, mutations))
            },
            &mut known_types,
        )?,
        None => None,
    };

    let schema_builder = Schema::build(
        query.type_name(),
        mutation.as_ref().map(Object::type_name),
        None,
    )
    .register(json_scalar())
    .register(date_time_scalar())
    .register(date_scalar())
    .register(time_scalar())
    .register(duration_scalar());
    known_types
        .into_values()
        .chain([query.into()])
        .chain(mutation.map(Type::from))
        .fold(schema_builder, SchemaBuilder::register)
        .finish()
        .with_context(|| "Schema building failed")
}

/// Errors when two Specs have the same root field. Both trees are laid out
/// from the Spec's tree, so this covers Query and Mutation alike.
fn check_root_fields(api: &Api) -> anyhow::Result<()> {
    let mut root_specs: HashMap<&str, &str> = HashMap::new();
    for spec in &api.specs {
        for root in spec.tree.keys() {
            if let Some(other) = root_specs.insert(root, &spec.name) {
                bail!(
                    "GraphQL path conflict: Specs '{other}' and '{}' both have root field '{root}'",
                    spec.name
                );
            }
        }
    }
    Ok(())
}

/// The root object `name` of one tree over every Spec, or `None` without
/// fields. Its branch types are named `name` plus their path; `leaf` gives
/// each Topic's fields, given the name of the Spec it is in.
fn root(
    name: &str,
    api: &Api,
    leaf: &mut impl FnMut(&str, &str, &GraphqlPath, &TopicDef) -> anyhow::Result<Leaf>,
    known_types: &mut HashMap<String, Type>,
) -> anyhow::Result<Option<Object>> {
    let mut fields = Vec::new();
    for spec in &api.specs {
        fields.extend(tree_fields(
            name,
            &GraphqlPath::default(),
            &spec.tree,
            &mut |segment, path, topic| leaf(&spec.name, segment, path, topic),
            known_types,
        )?);
    }
    Ok(object(name, fields))
}

/// Add `types` to `known`, erroring when a name is already taken by a
/// different type.
fn register_types(known: &mut HashMap<String, Type>, types: Vec<Type>) -> anyhow::Result<()> {
    for new in types {
        let name = type_name(&new).to_string();
        let new_string = format!("{new:?}");
        if let Some(other) = known.insert(name.clone(), new) {
            let other_string = format!("{other:?}");
            if new_string != other_string {
                bail!(
                    "GraphQL type name clash: '{name}' is used by both '{other_string}' and '{new_string}'"
                );
            }
        }
    }
    Ok(())
}

/// The name of `ty`. `Type::name` is crate-private in async-graphql.
fn type_name(ty: &Type) -> &str {
    match ty {
        Type::Scalar(scalar) => scalar.type_name(),
        Type::Object(object) => object.type_name(),
        Type::InputObject(input) => input.type_name(),
        Type::Enum(enum_type) => enum_type.type_name(),
        Type::Interface(interface) => interface.type_name(),
        Type::Union(union) => union.type_name(),
        Type::Subscription(subscription) => subscription.type_name(),
        Type::Upload => TypeRef::UPLOAD,
    }
}

/// A Topic's fields and the types they need, output and input alike: GraphQL
/// has one namespace for both. Empty to leave the Topic out.
type Leaf = (Vec<Field>, Vec<Type>);

/// The fields for one level of a Spec's tree, collecting the types they
/// need into `known_types`. Query and Mutation both use it: `leaf` gives
/// each Topic's fields, and a branch is an object named `prefix` plus its
/// path, left out when nothing below it has a field.
fn tree_fields(
    prefix: &str,
    parent_path: &GraphqlPath,
    children: &Tree,
    leaf: &mut impl FnMut(&str, &GraphqlPath, &TopicDef) -> anyhow::Result<Leaf>,
    known_types: &mut HashMap<String, Type>,
) -> anyhow::Result<Vec<Field>> {
    let mut fields = Vec::new();
    for (segment, node) in children {
        let path = parent_path.child(segment);
        let (new_fields, types) = match node {
            PathNode::Branch(grandchildren) => {
                let type_name = prefixed_path_type_name(prefix, &path);
                let branch_fields = tree_fields(prefix, &path, grandchildren, leaf, known_types)?;
                let Some(branch) = object(&type_name, branch_fields) else {
                    info!("Branch '{path}' has no fields, leaving out {type_name}");
                    continue;
                };
                (vec![branch_field(segment, &type_name)], vec![branch.into()])
            }
            PathNode::Topic(topic) => leaf(segment, &path, topic)?,
        };
        register_types(known_types, types)?;
        fields.extend(new_fields);
    }
    Ok(fields)
}

/// An object named `name` with `fields`, or `None` without fields: GraphQL
/// has no objects without fields.
fn object(name: &str, fields: Vec<Field>) -> Option<Object> {
    (!fields.is_empty()).then(|| fields.into_iter().fold(Object::new(name), Object::field))
}

/// The Query fields of `topic` at `path`. A Topic only a client can set
/// belongs to Mutation alone. Payload types are named after `spec`.
fn query_leaf(
    spec: &str,
    segment: &str,
    path: &GraphqlPath,
    topic: &TopicDef,
    cache: &Arc<TopicCache>,
) -> anyhow::Result<Leaf> {
    if topic.operation != Direction::Send {
        return Ok(Leaf::default());
    }
    info!("Building schema for topic {}", topic.topic);
    let Some(payload) = topic.payload.as_ref() else {
        warn!("Topic {} without payload, ignoring", topic.topic);
        return Ok(Leaf::default());
    };
    if payload.name.is_empty() {
        warn!(
            "Topic {} would create an invalid payload type, ignoring",
            topic.topic
        );
        return Ok(Leaf::default());
    }

    match &topic.kind {
        TopicKind::Single => {
            let type_name = payload_type_name(spec, &payload.name);
            let field = payload_query_field(segment, &topic.topic, &type_name, cache);
            Ok((
                vec![field],
                payload_object(spec, &payload.name, &payload.fields),
            ))
        }
        TopicKind::Group(group) => {
            let leaf = register_group_queries(segment, path, &topic.topic, payload, group, cache)?;
            Ok(leaf.unwrap_or_default())
        }
    }
}

/// Type name of what sits at `path` in the Query tree: `Query` plus the
/// full path in PascalCase (`marpower.freshWater` →
/// `QueryMarpowerFreshWater`). A branch is named exactly this; a Group's
/// types use it as a prefix.
fn path_type_name(path: &GraphqlPath) -> String {
    prefixed_path_type_name("Query", path)
}

/// Type name of the branch at `path` in a tree whose types start with
/// `prefix` (`Mutation`, `marpower.freshWater` → `MutationMarpowerFreshWater`).
fn prefixed_path_type_name(prefix: &str, path: &GraphqlPath) -> String {
    let base = pascal_case_graphql_name(
        &path
            .segments()
            .iter()
            .map(|s| s.trim_start_matches('_'))
            .collect::<Vec<&str>>()
            .join("-"),
    );
    format!("{prefix}{}", base.trim_start_matches('_'))
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

/// The type name of a payload object, or of an enum, named `name` in a
/// Spec or Group named `name_prefix`.
fn payload_type_name(name_prefix: &str, name: &str) -> String {
    pascal_case_graphql_name(&format!("{name_prefix}-{name}"))
}

/// One concrete topic's `<Topic>` payload object, named
/// [`payload_type_name`], followed by the types of its nested fields.
fn payload_object(
    name_prefix: &str,
    name: &str,
    fields: &BTreeMap<String, FieldType>,
) -> Vec<Type> {
    if fields.is_empty() {
        warn!("Object {name} can't have zero fields!");
    }

    let type_name = payload_type_name(name_prefix, name);
    let (object, mut types) = fields
        .iter()
        .filter_map(|(name, field_type)| payload_field(name_prefix, name, field_type))
        .fold(
            (Object::new(type_name.as_str()), Vec::new()),
            |(obj, mut types), (field, new_types)| {
                types.extend(new_types);
                (obj.field(field), types)
            },
        );
    types.insert(0, object.into());
    types
}

/// One payload field on a `<Topic>` object: projects the raw field name
/// from the object value returned by [`topic_query_field`].
fn payload_field(
    name_prefix: &str,
    name: &str,
    field_type: &FieldType,
) -> Option<(Field, Vec<Type>)> {
    let field_name = sanitize_to_graphql_name(name);

    if field_name.is_empty() {
        warn!("Skipping field '{name}' sanitizes to empty GraphQL name");
        return None;
    }

    let raw_name = Name::new(name);
    let (type_ref, types) = graphql_type_ref(name_prefix, field_type);
    let field_type = field_type.clone();

    let field = Field::new(field_name, type_ref, move |ctx| {
        let raw_name = raw_name.clone();
        let field_type = field_type.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map.get(&raw_name).cloned(),
                _ => None,
            };
            non_null(value)
                .map(|value| output_value(&field_type, value).map(FieldValue::value))
                .transpose()
        })
    });

    Some((field, types))
}

/// `value` as the output of a field of `field_type`: enum values by their
/// GraphQL name. Errors on a value that is not one of the enum's, so a Spec
/// that no longer matches what is published shows.
fn output_value(
    field_type: &FieldType,
    value: GraphQlValue,
) -> async_graphql::Result<GraphQlValue> {
    match (field_type, value) {
        (FieldType::Enum(name, values), value) => {
            let raw = value.clone().into_json().ok();
            values
                .iter()
                .find(|enum_value| {
                    raw.as_ref()
                        .is_some_and(|raw| equal_value(raw, &enum_value.raw, None))
                })
                .map(|enum_value| GraphQlValue::Enum(Name::new(&enum_value.name)))
                .ok_or_else(|| format!("{value} is not one of the values of enum {name}").into())
        }
        (FieldType::List(element), GraphQlValue::List(items)) => items
            .into_iter()
            .map(|item| match item {
                GraphQlValue::Null => Ok(GraphQlValue::Null),
                item => output_value(element, item),
            })
            .collect::<async_graphql::Result<_>>()
            .map(GraphQlValue::List),
        (_, value) => Ok(value),
    }
}

/// The enum type of a field of type [`FieldType::Enum`].
fn enum_type(name_prefix: &str, name: &str, values: &[EnumValue]) -> Enum {
    Enum::new(payload_type_name(name_prefix, name))
        .items(values.iter().map(|value| value.name.as_str()))
}

/// `value` unless it is missing or `null`. A resolver must return `None`
/// for those: `Some(Null)` on an object-typed field resolves the object
/// against a `null` parent, giving an object with only `null` fields.
fn non_null(value: Option<GraphQlValue>) -> Option<GraphQlValue> {
    value.filter(|value| *value != GraphQlValue::Null)
}

/// The output type of a field of `field_type`, with the object and enum
/// types it needs.
fn graphql_type_ref(name_prefix: &str, field_type: &FieldType) -> (TypeRef, Vec<Type>) {
    #[allow(clippy::match_same_arms)]
    match field_type {
        FieldType::Float => (TypeRef::named(TypeRef::FLOAT), vec![]),
        FieldType::Int => (TypeRef::named(TypeRef::INT), vec![]),
        FieldType::Boolean => (TypeRef::named(TypeRef::BOOLEAN), vec![]),
        FieldType::String => (TypeRef::named(TypeRef::STRING), vec![]),
        FieldType::Object(name, fields) => (
            TypeRef::named(payload_type_name(name_prefix, name)),
            payload_object(name_prefix, name, fields),
        ),
        FieldType::Enum(name, values) => {
            let enum_type = enum_type(name_prefix, name, values);
            (
                TypeRef::named(enum_type.type_name()),
                vec![enum_type.into()],
            )
        }
        FieldType::List(element) => {
            let (element, types) = graphql_type_ref(name_prefix, element);
            (TypeRef::List(Box::new(element)), types)
        }
        FieldType::Json => (TypeRef::named(JSON_SCALAR), vec![]),
        FieldType::DateTime => (TypeRef::named(DATE_TIME_SCALAR), vec![]),
        FieldType::Date => (TypeRef::named(DATE_SCALAR), vec![]),
        FieldType::Time => (TypeRef::named(TIME_SCALAR), vec![]),
        FieldType::Duration => (TypeRef::named(DURATION_SCALAR), vec![]),
    }
}

/// The scalar for values without a known GraphQL type: any JSON.
const JSON_SCALAR: &str = "JSON";

/// The [`JSON_SCALAR`] type. It accepts any value; inputs are still
/// validated against the topic's JSON Schema before publishing.
fn json_scalar() -> Scalar {
    Scalar::new(JSON_SCALAR)
        .description("Any JSON value, for a list whose element type the Spec does not declare")
}

/// The scalars for strings in a date or time `format`. Like [`JSON_SCALAR`],
/// their values pass through as the strings on the wire; inputs are
/// validated against the topic's JSON Schema before publishing.
const DATE_TIME_SCALAR: &str = "DateTime";
const DATE_SCALAR: &str = "Date";
const TIME_SCALAR: &str = "Time";
const DURATION_SCALAR: &str = "Duration";

/// The [`DATE_TIME_SCALAR`] type, for `format: date-time`.
fn date_time_scalar() -> Scalar {
    Scalar::new(DATE_TIME_SCALAR).description("An RFC 3339 timestamp, such as 2026-11-10T09:30:00Z")
}

/// The [`DATE_SCALAR`] type, for `format: date`.
fn date_scalar() -> Scalar {
    Scalar::new(DATE_SCALAR).description("An RFC 3339 full-date, such as 2026-11-10")
}

/// The [`TIME_SCALAR`] type, for `format: time`.
fn time_scalar() -> Scalar {
    Scalar::new(TIME_SCALAR).description("An RFC 3339 full-time, such as 09:30:00Z")
}

/// The [`DURATION_SCALAR`] type, for `format: duration`.
fn duration_scalar() -> Scalar {
    Scalar::new(DURATION_SCALAR).description("An ISO 8601 duration, such as PT1M30S")
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
            setter: None,
            kind: TopicKind::Single,
        }
    }

    #[test_log::test]
    fn test_branch_types_are_named_after_their_full_graphql_path() {
        let topics = vec![mock_topic(
            "marpower/250000-fresh-water/cold/cold-flow",
            "x",
        )];

        let sdl = build_schema(&mock_api(topics), &Arc::new(TopicCache::new()), None)
            .unwrap()
            .sdl();
        assert!(sdl.contains("marpower: QueryMarpower\n"), "{sdl}");
        assert!(
            sdl.contains("_250000FreshWater: QueryMarpower250000FreshWater\n"),
            "{sdl}"
        );
        assert!(
            sdl.contains("cold: QueryMarpower250000FreshWaterCold\n"),
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

        let schema = build_schema(&mock_api(topics), &Arc::new(TopicCache::new()), None).unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("logs"), "{sdl}");
        assert!(!sdl.contains("sensors"), "{sdl}");
        assert!(sdl.contains("a: QueryA"), "{sdl}");
    }

    #[test_log::test]
    fn test_branch_type_name_clashing_with_a_payload_type_errors() {
        // Payload type of `aB/c` is `QueryA`; the branch at `a/b` is also `QueryA`.
        let topics = vec![
            mock_topic("a/b", "x"),
            TopicDef {
                topic: "aB/c".to_string(),
                payload: Some(Payload {
                    name: "query-a".to_string(),
                    fields: BTreeMap::from_iter(vec![("field".to_string(), FieldType::Float)]),
                }),
                operation: Direction::Send,
                ttl_secs: None,
                setter: None,
                kind: TopicKind::Single,
            },
        ];

        let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new()), None).unwrap_err();
        assert!(
            err.to_string()
                .contains("GraphQL type name clash: 'QueryA' is used by both"),
        );
    }

    #[test_log::test]
    fn test_two_branches_with_the_same_type_name_error() {
        // The branch at `aB` and the branch at `a/b` are both named `QueryAB`.
        let topics = vec![mock_topic("aB/x/y", "v"), mock_topic("a/b/y/z", "v")];

        let err = build_schema(&mock_api(topics), &Arc::new(TopicCache::new()), None).unwrap_err();
        assert!(
            err.to_string()
                .contains("GraphQL type name clash: 'QueryAB' is used by both"),
        );
    }

    #[test_log::test]
    fn test_address_level_without_a_graphql_name_ok() {
        for address in ["/a/b", "a//b", "a/-/b"] {
            let topics = vec![mock_topic(address, "v")];

            let schema =
                build_schema(&mock_api(topics), &Arc::new(TopicCache::new()), None).unwrap();
            let sdl = schema.sdl();
            assert!(sdl.contains("a: QueryA"), "{sdl}");
            assert!(sdl.contains("b: Vpayload"), "{sdl}");
        }
    }

    #[test_log::test]
    fn test_specs_sharing_a_root_field_conflict() {
        let api = Api::new(vec![
            spec("one", vec![mock_topic("thrs/controller/pcm", "x")]),
            spec("two", vec![mock_topic("thrs/simulator/step", "y")]),
        ]);

        let err = build_schema(&api, &Arc::new(TopicCache::new()), None).unwrap_err();
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
        let schema = build_schema(&api, &cache, None).unwrap();

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
            setter: None,
            kind: TopicKind::Single,
        };
        let schema_with = |payload| {
            let cache = Arc::new(TopicCache::new());
            cache.insert("a/b", payload);
            build_schema(&mock_api(vec![topic.clone()]), &cache, None).unwrap()
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
