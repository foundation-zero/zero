use std::collections::{BTreeMap, BTreeSet};
use std::iter::once;
use std::sync::Arc;

use async_graphql::dynamic::*;
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use log::warn;
use serde_json::Value as JsonValue;

use crate::asyncapi::{FieldDef, ObjectTypeDef, TopicDef, TopicGroupDef};
use crate::cache::TopicCache;
use crate::metadata::{metadata_by_topic, MetadataByTopic, MetadataFile};
use crate::model::lifecycle::{DirectiveDef, LifecycleDef};
use crate::model::mutations::{ConfirmDef, DerivedLeaf, MutationDef, MutationKind};
use crate::model::views::{
    LeafDef, ObjectFieldDef, ObjectSectionDef, PlainFieldDef, PlainObjectDef, SectionDef,
    StampedFieldDef, StampedFieldsSection, SwitchSectionDef, ViewDef,
};
use crate::naming::*;

mod groups;
mod lifecycle;
mod mutations;
mod stamped;
#[cfg(test)]
mod tests;
mod topics;
mod views;

use groups::*;
use lifecycle::*;
use mutations::*;
use stamped::*;
pub use topics::validate_topics;
use topics::*;
use views::*;

/// RFC 3339 timestamp scalar, served as the wire carries it.
const DATETIME_SCALAR: &str = "DateTime";
/// Always-null scalar for `Empty` placeholders and directive mutations.
const VOID_SCALAR: &str = "Void";
/// Placeholder field on fieldless objects; thrs-api names it `Empty` and zero-ui selects it.
const EMPTY_FIELD: &str = "Empty";

/// Future returned by a [`TopicPublisher`] publish.
pub type PublishFuture =
    std::pin::Pin<Box<dyn std::future::Future<Output = anyhow::Result<()>> + Send>>;

/// Publishes a payload to an MQTT topic; abstracted so tests can capture publishes.
pub trait TopicPublisher: Send + Sync {
    fn publish(&self, topic: String, payload: String) -> PublishFuture;
}

/// A group's rows partitioned into buckets by the `group_by` metadata
/// attribute: bucket id → `(topic, metadata)` pairs.
type GroupedRows = BTreeMap<String, Vec<(String, BTreeMap<String, JsonValue>)>>;

/// Everything a schema is built from besides the cache. `Default` is empty and read-only.
#[derive(Default)]
pub struct SchemaInputs<'a> {
    /// Concrete topics, one sanitized query field each.
    pub topics: &'a [TopicDef],
    /// Parametrized topic families; queryable once `metadata` enumerates their topics.
    pub groups: &'a [TopicGroupDef],
    pub metadata: &'a [MetadataFile],
    pub object_types: &'a [ObjectTypeDef],
    pub views: &'a [ViewDef],
    /// Lifecycles; the write side needs a `publisher`.
    pub lifecycles: &'a [LifecycleDef],
    /// Where mutations publish; `None` keeps the schema read-only.
    pub publisher: Option<Arc<dyn TopicPublisher>>,
    /// Serve `sensorValues` per field instead of all-or-nothing.
    pub enable_optional_sensor_values: bool,
}

/// Build the dynamic GraphQL schema over the cache.
///
/// Errors when sanitized topic names are empty, collide, or hit a reserved name.
pub fn build_schema(cache: Arc<TopicCache>, inputs: SchemaInputs<'_>) -> anyhow::Result<Schema> {
    let SchemaInputs {
        topics,
        groups,
        metadata,
        object_types,
        views,
        lifecycles,
        publisher,
        enable_optional_sensor_values,
    } = inputs;
    validate_topics(topics)?;

    let metadata_store = Arc::new(metadata_by_topic(metadata));
    let mut used_query_fields = initial_used_query_names(topics);
    // A later registration of the same name overwrites an earlier one.
    let mut types: Vec<Type> = Vec::new();

    let mut query = Object::new("Query");
    query = query.field(topics_introspection_field(topics));

    let ConcreteTopics {
        objects,
        metadata_types,
        query_fields,
    } = register_concrete_topics(topics, &cache, &metadata_store);
    for field in query_fields {
        query = query.field(field);
    }

    for group in groups {
        let Some(parts) = register_group_queries(group, metadata, &mut used_query_fields, &cache)?
        else {
            continue;
        };
        query = parts.query_fields.into_iter().fold(query, Object::field);
        types.extend(parts.objects.into_iter().map(Type::from));
    }
    types.extend(objects.into_iter().map(Type::from));

    for parts in register_views(
        views,
        &cache,
        &mut used_query_fields,
        enable_optional_sensor_values,
    ) {
        query = query.field(parts.gql);
        types.extend(parts.objects.into_iter().map(Type::from));
    }

    types.extend(
        register_stamped_wrapper_objects(topics, groups, views, lifecycles)
            .into_iter()
            .map(Type::from),
    );
    types.extend(
        register_composite_object_types(object_types)
            .into_iter()
            .map(Type::from),
    );
    types.extend(
        metadata_types
            .into_iter()
            .map(|(type_name, meta_map)| concrete_metadata_object(&type_name, &meta_map).into()),
    );

    types.extend(shared_types(views, lifecycles));

    let has_mutations = views.iter().any(|v| v.mutations().next().is_some());
    let mut mutation = match &publisher {
        Some(publisher) if has_mutations => {
            let (mutation, mutation_types) = register_mutations(views, &cache, publisher.clone());
            types.extend(mutation_types);
            Some(mutation)
        }
        _ => None,
    };

    for lifecycle in lifecycles {
        let parts = register_lifecycle(lifecycle, &cache, publisher.clone());
        query = query.field(parts.gql);
        types.extend(parts.types);
        if !parts.mutation_fields.is_empty() {
            let obj = mutation.take().unwrap_or_else(|| Object::new("Mutation"));
            mutation = Some(parts.mutation_fields.into_iter().fold(obj, Object::field));
        }
    }

    finish_schema(query, mutation, types)
}

/// Enums (deduped by name) and scalars shared by the read and write side.
fn shared_types(views: &[ViewDef], lifecycles: &[LifecycleDef]) -> Vec<Type> {
    let mut enums: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut add = |name: &Option<String>, values: &Option<BTreeMap<String, String>>| {
        if let (Some(name), Some(values)) = (name, values) {
            enums
                .entry(name.clone())
                .or_default()
                .extend(values.values().cloned());
        }
    };
    for leaf in views.iter().flat_map(|v| v.leaves()) {
        add(&leaf.enum_type, &leaf.enum_values);
    }
    for f in views
        .iter()
        .flat_map(|v| v.mutations())
        .flat_map(|(_, d)| d.input_fields.iter())
    {
        add(&f.enum_type, &f.enum_values);
    }
    for lifecycle in lifecycles {
        for leaf in lifecycle.leaves() {
            add(&leaf.enum_type, &leaf.enum_values);
        }
        for f in lifecycle
            .mutations()
            .flat_map(|(_, d)| d.input_fields.iter())
        {
            add(&f.enum_type, &f.enum_values);
        }
    }
    let mut types: Vec<Type> = vec![
        Scalar::new(DATETIME_SCALAR).into(),
        Scalar::new(VOID_SCALAR).into(),
    ];
    for (name, members) in enums {
        let en = members
            .into_iter()
            .fold(Enum::new(name), |en, member| en.item(member));
        types.push(en.into());
    }
    types
}

/// Composite object types; their cached JSON has a topic payload's shape.
fn register_composite_object_types(object_types: &[ObjectTypeDef]) -> Vec<Object> {
    object_types
        .iter()
        .map(|def| {
            def.fields
                .iter()
                .map(payload_field)
                .fold(Object::new(def.name.as_str()), Object::field)
        })
        .collect()
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

/// Query names claimed before any group registers.
fn initial_used_query_names(topics: &[TopicDef]) -> BTreeSet<String> {
    topics
        .iter()
        .map(|t| sanitize_to_graphql_name(&t.topic))
        .chain(std::iter::once("topics".to_string()))
        .collect()
}

/// The `<Topic>Metadata` object with one topic's static attributes.
fn concrete_metadata_object(type_name: &str, meta_map: &BTreeMap<String, JsonValue>) -> Object {
    let mut meta_obj = Object::new(type_name);
    for (key, value) in meta_map {
        meta_obj = meta_obj.field(row_projection_field(
            &sanitize_to_graphql_name(key),
            graphql_scalar_for_value(value),
        ));
    }
    meta_obj
}

fn finish_schema(
    query: Object,
    mutation: Option<Object>,
    types: Vec<Type>,
) -> anyhow::Result<Schema> {
    let mutation_name = mutation.as_ref().map(|m| m.type_name().to_string());
    let builder = Schema::build(query.type_name(), mutation_name.as_deref(), None).register(query);
    // Components can share an input type name; the first wins, as in thrs-api.
    let mut seen_inputs: BTreeSet<String> = BTreeSet::new();
    let builder = types.into_iter().fold(builder, |builder, ty| match ty {
        Type::InputObject(input) if !seen_inputs.insert(input.type_name().to_string()) => {
            warn!(
                "input type '{}' defined twice — keeping the first definition",
                input.type_name()
            );
            builder
        }
        ty => builder.register(ty),
    });
    let builder = match mutation {
        Some(mutation) => builder.register(mutation),
        None => builder,
    };
    Ok(builder.finish()?)
}

/// GraphQL scalar for an arbitrary JSON value.
fn graphql_scalar_for_value(value: &JsonValue) -> TypeRef {
    match value {
        JsonValue::Bool(_) => TypeRef::named(TypeRef::BOOLEAN),
        JsonValue::Number(_) => TypeRef::named(TypeRef::FLOAT),
        _ => TypeRef::named(TypeRef::STRING),
    }
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

/// Evict expired entries from the cache periodically.
pub fn spawn_eviction(cache: std::sync::Arc<TopicCache>) {
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(std::time::Duration::from_secs(30));
        loop {
            interval.tick().await;
            cache.evict_expired();
        }
    });
}

/// Map a type name (incl. `Stamped:`/`Object:` markers) to a TypeRef.
fn graphql_type_ref(typ: &str) -> TypeRef {
    if let Some(inner) = typ.strip_prefix("Stamped:") {
        return TypeRef::named(stamped_wrapper_type_name(inner));
    }
    if let Some(name) = typ.strip_prefix("Object:") {
        return TypeRef::named(name);
    }
    match typ {
        "Float" => TypeRef::named(TypeRef::FLOAT),
        "Int" => TypeRef::named(TypeRef::INT),
        "Boolean" => TypeRef::named(TypeRef::BOOLEAN),
        "String" => TypeRef::named(TypeRef::STRING),
        _ => TypeRef::named(TypeRef::STRING),
    }
}
/// Null as `None`: an enum-typed field rejects `Value::Null`.
fn nullable(value: GraphQlValue) -> Option<FieldValue<'static>> {
    match value {
        GraphQlValue::Null => None,
        v => Some(FieldValue::value(v)),
    }
}
