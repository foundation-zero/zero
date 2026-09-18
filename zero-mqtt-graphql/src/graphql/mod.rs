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
use std::iter::once;
use std::sync::Arc;

use async_graphql::dynamic::*;
use async_graphql::Name;
use async_graphql::Value as GraphQlValue;
use log::warn;
use roas_asyncapi::common::reference::RefOr;
use roas_asyncapi::v3_0::schema::{
    Schema as AsyncApiSchema, SchemaOrMultiFormat, SchemaType, SubSchema,
};
use roas_asyncapi::v3_0::Document;
use serde_json::Value as JsonValue;

use crate::asyncapi::{FieldDef, ObjectTypeDef, TopicDef, TopicGroupDef};
use crate::cache::TopicCache;
use crate::config::ComputedMode;
use crate::metadata::{metadata_by_topic, MetadataByTopic, MetadataFile};
use crate::modules_view::{
    ControlModeDef, ModuleFieldDef, ModuleLeafDef, ModuleView, ObjectFieldDef, ObjectSectionDef,
    PlainFieldDef, PlainObjectDef,
};
use crate::mutations_view::{Bounds, DerivedLeaf, ModuleMutations, MutationDef};
use crate::simulation_view::{DirectiveDef, SimulationView};

mod modules;
mod mutations;
mod simulation;

use modules::*;
use mutations::*;
use simulation::*;

/// thrs-api's timestamp scalar (Strawberry `DateTime`). Values are ISO-8601
/// strings, normalized to Python `isoformat` shape (see `normalize_timestamp`).
const DATETIME_SCALAR: &str = "DateTime";
/// thrs-api's `Void` scalar: the type of an `Empty` placeholder field and of
/// the simulation directive mutations. Always resolves to null.
const VOID_SCALAR: &str = "Void";
/// Placeholder field thrs-api (Strawberry) puts on a fieldless pydantic model
/// (`empty_pydantic_type_to_strawberry_type` adds `_empty`, which Strawberry's
/// name converter exposes as `Empty`). zero-ui selects it verbatim.
const EMPTY_FIELD: &str = "Empty";
use crate::naming::*;

/// Future returned by a [`TopicPublisher`] publish.
pub type PublishFuture =
    std::pin::Pin<Box<dyn std::future::Future<Output = anyhow::Result<()>> + Send>>;

/// Publishes a payload to an MQTT topic. Abstracted so the mutation resolvers
/// don't depend on the MQTT client directly (and so tests can capture publishes
/// without a broker). The production impl wraps the subscriber's `AsyncClient`
/// (see `crate::mqtt::MqttPublisher`).
pub trait TopicPublisher: Send + Sync {
    fn publish(&self, topic: String, payload: String) -> PublishFuture;
}

/// A group's rows partitioned into buckets by the `group_by` metadata
/// attribute: bucket id → `(topic, metadata)` pairs.
type GroupedRows = BTreeMap<String, Vec<(String, BTreeMap<String, JsonValue>)>>;

/// Everything a schema is built from besides the cache. `Default` is the empty,
/// read-only, relay-mode schema, so a caller sets only what it has.
#[derive(Default)]
pub struct SchemaInputs<'a> {
    /// Concrete topics, one sanitized query field each (see [`validate_topics`]).
    pub topics: &'a [TopicDef],
    /// Parametrized topic families; a group gains a list query once `metadata`
    /// enumerates its concrete topics.
    pub groups: &'a [TopicGroupDef],
    pub metadata: &'a [MetadataFile],
    pub object_types: &'a [ObjectTypeDef],
    /// The nested `modules { <module> { … } }` view (`*-module.json`, see
    /// [`crate::modules_view`]) - the shape the THRS UI reads.
    pub module_views: &'a [ModuleView],
    /// thrs-api's module mutations (`*-mutations.json`, see
    /// [`crate::mutations_view`]); served only with a `publisher`.
    pub mutations: &'a [ModuleMutations],
    /// thrs-api's `simulation` query, directives and input mutations
    /// (`thrs-simulation.json`, see [`crate::simulation_view`]). The read side
    /// is always served; the write side needs a `publisher`.
    pub simulation: Option<&'a SimulationView>,
    /// Where mutations publish. `None` keeps the schema read-only whatever
    /// `mutations`/`simulation` declare (`ENABLE_MUTATIONS` gates this at the
    /// call site).
    pub publisher: Option<Arc<dyn TopicPublisher>>,
    /// How computed sensor fields are served (see [`crate::recompute`]).
    pub computed_mode: ComputedMode,
    /// Serve `sensorValues` per field instead of all-or-nothing (see
    /// [`crate::config::AppConfig::enable_optional_sensor_values`]).
    pub enable_optional_sensor_values: bool,
}

/// Build a dynamic GraphQL schema over the cache from [`SchemaInputs`].
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
/// attribute. Concrete topics annotated in the metadata store gain an additive
/// `metadata { … }` field on their own object type.
///
/// The module views, mutations and simulation spec add thrs-api's nested
/// surface on top, named exactly as thrs-api names it.
pub fn build_schema(cache: Arc<TopicCache>, inputs: SchemaInputs<'_>) -> anyhow::Result<Schema> {
    let SchemaInputs {
        topics,
        groups,
        metadata,
        object_types,
        module_views,
        mutations,
        simulation,
        publisher,
        computed_mode,
        enable_optional_sensor_values,
    } = inputs;
    validate_topics(topics)?;

    let metadata_store = Arc::new(metadata_by_topic(metadata));
    let mut used_query_fields = initial_used_query_names(topics);
    // Every supporting type, registered in this order (a later registration of
    // the same name overwrites an earlier one; the only duplicates are
    // identical definitions shared by the read and write side).
    let mut types: Vec<Type> = Vec::new();

    let mut query = Object::new("Query");
    query = query.field(topics_introspection_field(topics));

    // Concrete topic objects and their query fields. Each query field returns
    // the topic's whole cached payload object; its scalar subfields project
    // from that object (see `payload_field`).
    let ConcreteTopics {
        objects,
        metadata_types,
        query_fields,
    } = register_concrete_topics(topics, &cache, &metadata_store);
    for field in query_fields {
        query = query.field(field);
    }

    // Group list queries: one merged list per parametrized channel whose
    // domain ships a metadata file (which enumerates the concrete topics).
    for group in groups {
        let Some(parts) = register_group_queries(group, metadata, &mut used_query_fields, &cache)?
        else {
            continue;
        };
        query = parts.query_fields.into_iter().fold(query, Object::field);
        types.extend(parts.objects.into_iter().map(Type::from));
    }
    types.extend(objects.into_iter().map(Type::from));

    // Nested per-module view. Additive: `module_views` is empty unless
    // `*-module.json` specs are loaded, so the flat schema stays the same.
    if let Some(parts) = register_modules_query(
        module_views,
        &cache,
        &mut used_query_fields,
        computed_mode,
        enable_optional_sensor_values,
    ) {
        query = query.field(parts.query_field);
        types.extend(parts.objects.into_iter().map(Type::from));
    }

    types.extend(
        register_stamped_wrapper_objects(topics, groups, module_views, simulation)
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

    // Types shared by the read and write side and named exactly as thrs-api
    // names them: the enum types every enum leaf/input uses (`ControlMode`,
    // `PumpControlMode`, ...), and the `DateTime`/`Void` scalars.
    types.extend(shared_types(module_views, mutations, simulation));

    // Mutation type (write-path). Only built when a publisher is present and at
    // least one mutation is declared, so read-only deployments stay read-only.
    // Mutations bring their own supporting types: parameter/control return
    // objects and control input types.
    let has_mutations = mutations.iter().any(|m| !m.mutations.is_empty());
    let mut mutation = match &publisher {
        Some(publisher) if has_mutations => {
            let (mutation, mutation_types) =
                register_mutations(mutations, &cache, publisher.clone());
            types.extend(mutation_types);
            Some(mutation)
        }
        _ => None,
    };

    // Simulation (thrs-api `simulation { status time inputs outputs }`, the
    // play/pause/step directives and the input mutations). Read side always;
    // write side only with a publisher, joining the Mutation type.
    if let Some(sim) = simulation {
        let parts = register_simulation(sim, &cache, publisher.clone());
        query = query.field(parts.query_field);
        types.extend(parts.types);
        if !parts.mutation_fields.is_empty() {
            let obj = mutation.take().unwrap_or_else(|| Object::new("Mutation"));
            mutation = Some(parts.mutation_fields.into_iter().fold(obj, Object::field));
        }
    }

    finish_schema(query, mutation, types)
}

/// The types both the read and the write side refer to by thrs-api's exact
/// names: one GraphQL `Enum` per Python enum class (members = the member names
/// in `enum_values`), plus the `DateTime` and `Void` scalars. Collected across
/// every module view, mutation spec and the simulation spec, deduped by name
/// (the same class is reused across modules and simulations).
fn shared_types(
    module_views: &[ModuleView],
    mutations: &[ModuleMutations],
    simulation: Option<&SimulationView>,
) -> Vec<Type> {
    let mut enums: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut add = |name: &Option<String>, values: &Option<BTreeMap<String, String>>| {
        if let (Some(name), Some(values)) = (name, values) {
            enums
                .entry(name.clone())
                .or_default()
                .extend(values.values().cloned());
        }
    };
    for view in module_views {
        for leaf in view.sensor_values.iter().flat_map(|f| f.leaves.iter()) {
            add(&leaf.enum_type, &leaf.enum_values);
        }
        for leaf in [
            &view.control_values,
            &view.parameters,
            &view.controller_state,
        ]
        .into_iter()
        .flatten()
        .flat_map(|s| s.fields.iter())
        .flat_map(|f| f.leaves.iter())
        {
            add(&leaf.enum_type, &leaf.enum_values);
        }
    }
    for f in mutations
        .iter()
        .flat_map(|m| m.mutations.iter())
        .flat_map(|d| d.input_fields.iter())
    {
        add(&f.enum_type, &f.enum_values);
    }
    if let Some(sim) = simulation {
        for leaf in sim
            .simulations
            .iter()
            .flat_map(|s| s.inputs.fields.iter().chain(s.outputs.fields.iter()))
            .flat_map(|f| f.leaves.iter())
        {
            add(&leaf.enum_type, &leaf.enum_values);
        }
        for f in sim.mutations().flat_map(|(_, d)| d.input_fields.iter()) {
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

/// Composite object types from `asyncapi::resolve_object_type`, each
/// turned into a GraphQL object with one field per `FieldDef`. Reuses
/// `payload_field` since the cached JSON shape (raw PascalCase keys,
/// projected to sanitized field names) is the same as a concrete topic's
/// payload.
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

/// Query names already claimed before any group registers: every sanitized
/// topic name plus the built-in `topics` field.
fn initial_used_query_names(topics: &[TopicDef]) -> BTreeSet<String> {
    topics
        .iter()
        .map(|t| sanitize_to_graphql_name(&t.topic))
        .chain(std::iter::once("topics".to_string()))
        .collect()
}

/// The `<Topic>Metadata` object exposing one concrete topic's static
/// attributes as projected scalar fields.
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

/// Assemble the final schema from the query object, the optional mutation
/// object and every supporting type.
fn finish_schema(
    query: Object,
    mutation: Option<Object>,
    types: Vec<Type>,
) -> anyhow::Result<Schema> {
    let mutation_name = mutation.as_ref().map(|m| m.type_name().to_string());
    let builder = Schema::build(query.type_name(), mutation_name.as_deref(), None).register(query);
    // thrs-api names a component's input type after its Python class
    // (`AdsorptionChillerInputType`), and two different components can share a
    // class name (control vs. simulation `AdsorptionChiller`). Strawberry then
    // serves the first definition it registered (the module's control input);
    // the later, differently-shaped one is silently dropped and its mutation
    // takes the winner's shape. Mirror that: keep the first input object per
    // name instead of letting a later registration replace it.
    let mut seen_inputs: BTreeSet<String> = BTreeSet::new();
    let builder = types.into_iter().fold(builder, |builder, ty| match ty {
        Type::InputObject(input) if !seen_inputs.insert(input.type_name().to_string()) => {
            warn!(
                "input type '{}' defined twice — keeping the first definition (thrs-api's Strawberry does the same)",
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

/// Schema contributions of the concrete (non-grouped) topics.
#[derive(Default)]
struct ConcreteTopics {
    /// `<Topic>` payload objects, one per topic with scalar fields.
    objects: Vec<Object>,
    /// `(type name, metadata)` pairs used to build `<Topic>Metadata` objects.
    metadata_types: Vec<(String, BTreeMap<String, JsonValue>)>,
    /// Query fields returning each topic's whole cached payload.
    query_fields: Vec<Field>,
}

/// Topics eligible for a queryable payload object: those with fields.
fn queryable_topics(topics: &[TopicDef]) -> impl Iterator<Item = &TopicDef> {
    topics
        .iter()
        .filter(|topic_def| !topic_def.fields.is_empty())
}

/// `(type name, metadata)` pair for a topic annotated with non-empty
/// metadata in the store.
fn metadata_type(
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

/// Build the `<Topic>` object types and cached-payload query fields for
/// every concrete topic, plus an additive `metadata { … }` field for topics
/// annotated in the metadata store.
fn register_concrete_topics(
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

/// One concrete topic's `<Topic>` payload object, plus the additive
/// `metadata { … }` field when the topic is annotated in the metadata store.
fn topic_object(topic_def: &TopicDef, metadata_store: &Arc<MetadataByTopic>) -> Object {
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
fn payload_field(field: &FieldDef) -> Field {
    let field_name = sanitize_to_graphql_name(&field.name);
    let raw_name = Name::new(field.name.clone());
    Field::new(
        field_name,
        graphql_type_ref(&field.graphql_type),
        move |ctx| {
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
        },
    )
}

/// The additive `metadata` field exposing a concrete topic's static
/// attributes from the metadata store.
fn metadata_field(
    topic: &str,
    meta_type_name: &str,
    metadata_store: &Arc<MetadataByTopic>,
) -> Field {
    let store = metadata_store.clone();
    let topic = topic.to_string();
    Field::new("metadata", TypeRef::named(meta_type_name), move |_ctx| {
        let store = store.clone();
        let topic = topic.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
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

/// Schema contributions of one topic group.
struct GroupSchemaParts {
    /// The group's supporting object types plus its optional bucket type.
    objects: Vec<Object>,
    /// The list query field plus optional grouped-by query fields.
    query_fields: Vec<Field>,
}

/// A group's metadata-file entries as `(topic, metadata)` pairs.
fn collect_group_entries(
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

/// Sanitize a group id into a fresh query field name, rejecting empty,
/// reserved, or already-claimed names.
fn claim_group_query_name(
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

/// Union of a group's sanitized metadata keys minus the reserved `values`
/// key — occupied by the live-field descriptors, so a static attribute of
/// that name would panic on duplicate field registration. Returns `None`
/// when the group has no metadata to project.
fn group_metadata_fields(
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
fn build_group_objects(
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

/// Union of a group's collected `x-*` extension keys across all its payload
/// fields, in stable order.
fn extension_keys(group: &TopicGroupDef) -> Vec<String> {
    group
        .value_extensions
        .values()
        .flat_map(|extensions| extensions.keys().cloned())
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

/// Descriptor fields for the `<Group>ValueMeta` object: the reserved `name`
/// plus every collected `x-*` schema extension (e.g. `unit`) as a string
/// field.
fn value_meta_descriptor_fields(group: &TopicGroupDef) -> impl Iterator<Item = Field> + '_ {
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

/// A row's bucket id for the `group_by` attribute, defaulting to
/// `"unknown"` when absent or not a string.
fn bucket_attribute<'a>(meta: &'a BTreeMap<String, JsonValue>, group_by: &'a str) -> &'a str {
    meta.get(group_by)
        .and_then(JsonValue::as_str)
        .unwrap_or("unknown")
}

/// Bucket a group's rows by their `group_by` attribute value; rows without
/// it land in the `"unknown"` bucket.
fn bucket_rows_by(
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

/// The bucket object (`<stem>Bucket`): bucket `id` plus the bucket's group rows.
fn bucket_object(pascal: &str, rows_field: &str) -> Object {
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

/// Build one topic group's schema parts: the merged
/// `<group>: [<Group>Topic]` list query with its supporting object types,
/// and — when the group's metadata declares `group_by` — grouped-by
/// bucket queries. Returns `None` when the group must be skipped entirely
/// (no usable metadata or a reserved/duplicate query name); claims all
/// used query names in `used_query_fields`.
fn register_group_queries(
    group: &TopicGroupDef,
    metadata: &[MetadataFile],
    used_query_fields: &mut BTreeSet<String>,
    cache: &Arc<TopicCache>,
) -> anyhow::Result<Option<GroupSchemaParts>> {
    let entries = collect_group_entries(metadata, &group.group);
    if group.fields.is_empty() {
        // A group whose payload is an object without scalar fields (e.g. THRS's
        // `{module}/control-mode`, `{"AutomaticMode": {...} | null}`) has no
        // list query to offer; without metadata it wouldn't get one anyway, so
        // skip it - it is still subscribed and served through the module view.
        // With metadata present it is a real misconfiguration.
        if entries.is_empty() {
            warn!(
                "Topic group '{}' has no scalar payload fields — no list query exposed",
                group.group
            );
            return Ok(None);
        }
        anyhow::bail!("topic group '{}' has no payload fields", group.group);
    }
    // anyOf groups (asyncapi::extract_fields_from_any_of) union their
    // branches' fields into one column set. Validate that union the same
    // way a topic's fields get validated, so a real name conflict between
    // branches is a clean error instead of a panic when the schema tries
    // to register two fields under one name.
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
struct BucketSchemaParts {
    /// The bucket object type (`<stem>Bucket`).
    object: Object,
    /// The `<stem>Buckets` list field plus the `<stem>Bucket(id)` singleton.
    query_fields: Vec<Field>,
}

/// Build the grouped-by bucket schema parts: a `<stem>Buckets` list of
/// buckets plus a `<stem>Bucket(id)` singleton, enabled by a `group_by`
/// attribute in the group's metadata file. Returns `None` when the group
/// declares no `group_by` or the derived query names collide.
fn register_bucket_queries(
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

    // `<stem>Buckets`: every bucket with its materialized group rows.
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
            async_graphql::dynamic::FieldFuture::new(async move {
                let values =
                    bucket_rows_json(&buckets, &fields, &value_meta_json, &cache, &rows_field);
                Ok(Some(FieldValue::value(json_to_graphql_value(
                    &JsonValue::Array(values),
                ))))
            })
        },
    );

    // `<stem>Bucket(id)`: a single bucket by id, resolving to `None` for
    // unknown ids.
    let value_meta_for_bucket = value_meta_json;
    let rows_for_bucket = rows_field.clone();
    let cache_for_bucket = cache.clone();
    let singleton_field = Field::new(bucket_field, TypeRef::named(bucket_type), move |ctx| {
        let buckets = buckets.clone();
        let fields = fields.clone();
        let value_meta_json = value_meta_for_bucket.clone();
        let rows_field = rows_for_bucket.clone();
        let cache = cache_for_bucket.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
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
fn row_projection_field(name: &str, type_ref: TypeRef) -> Field {
    let key = Name::new(name);
    Field::new(name, type_ref, move |ctx| {
        let key = key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map.get(&key).cloned().unwrap_or(GraphQlValue::Null),
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// The `<group>: [<Group>Topic]` query field.
///
/// Rows are materialized at resolution time: the metadata file enumerates
/// the concrete topics, static attributes come from that enumeration, and
/// live values come from the cache keyed by concrete topic.
fn group_query_field(
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
            async_graphql::dynamic::FieldFuture::new(async move {
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

/// Materialize bucket objects (`<Group>Bucket`: `{ id, <rows_key>: [row…] }`):
/// one per bucket id, each holding that bucket's group rows.
fn bucket_rows_json(
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

/// Per-field descriptors for a group: camelCase GraphQL name plus every
/// collected `x-*` schema extension (e.g. `unit`), keyed by sanitized name.
fn value_metadata_json(group: &TopicGroupDef) -> JsonValue {
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

/// Materialize one group row: topic + static metadata (with the live-field
/// descriptors injected under `metadata.values` when given) + live values.
fn group_row(
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

/// Union of sanitized metadata keys across a group's entries, typed by the
/// first non-null value seen.
fn union_metadata_fields(
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

/// GraphQL scalar for an arbitrary JSON value.
fn graphql_scalar_for_value(value: &JsonValue) -> TypeRef {
    match value {
        JsonValue::Bool(_) => TypeRef::named(TypeRef::BOOLEAN),
        JsonValue::Number(_) => TypeRef::named(TypeRef::FLOAT),
        _ => TypeRef::named(TypeRef::STRING),
    }
}

/// Query-name stem for grouped-by (bucket) queries: camelCase group name
/// with the plural "s" of its final word dropped (`power-tags` → `powerTag`),
/// so bucket queries are exposed as `<stem>Buckets` / `<stem>Bucket`.
fn singular_group_stem(group_id: &str) -> String {
    let camel = sanitize_to_graphql_name(group_id);
    match camel.strip_suffix('s') {
        Some(stem) => stem.to_string(),
        None => camel,
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

/// Map a GraphQL type name to an async-graphql TypeRef. `Stamped:<T>` and
/// `Object:<Name>` markers (see `asyncapi::field_graphql_type`) resolve to
/// their wrapper/composite object types instead of a scalar.
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

/// Wrapper type name for a Stamped value of scalar type `inner`, e.g.
/// `Float` -> `StampedFloat`.
fn stamped_wrapper_type_name(inner: &str) -> String {
    format!("Stamped{inner}")
}

/// The `Stamped<T>` type: `{ value: T, timestamp: String }`, projected
/// from the raw cached JSON's `Value`/`TimeStamp` keys.
fn stamped_wrapper_object(inner: &str) -> Object {
    let type_name = stamped_wrapper_type_name(inner);
    // Field names match THRS's own Stamped[T] GraphQL type: "value" and
    // "timestamp" (not "timeStamp": the python field is just `timestamp`,
    // "TimeStamp" is only the wire alias).
    Object::new(type_name.as_str())
        .field(stamped_wrapper_field(
            "value",
            "Value",
            stamped_value_type_ref(inner),
        ))
        .field(stamped_timestamp_field(false))
}

/// The `timestamp` leaf field. Reads the raw `TimeStamp` wire key and normalizes
/// it to thrs-api's shape: thrs-api parses the wire timestamp into a datetime and
/// re-serializes it, so a UTC `...Z` becomes `...+00:00` (Strawberry/Python
/// `datetime.isoformat`). We match that so the two APIs' timestamps are byte
/// identical; timestamps that already carry an explicit offset pass through.
fn stamped_timestamp_field(non_null: bool) -> Field {
    let type_ref = if non_null {
        TypeRef::named_nn(DATETIME_SCALAR)
    } else {
        TypeRef::named(DATETIME_SCALAR)
    };
    Field::new("timestamp", type_ref, move |ctx| {
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => match map.get(&Name::new("TimeStamp")) {
                    Some(GraphQlValue::String(s)) => GraphQlValue::String(normalize_timestamp(s)),
                    Some(other) => other.clone(),
                    None => GraphQlValue::Null,
                },
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// Normalize a wire timestamp to Python `datetime.isoformat` shape, matching
/// thrs-api. A trailing `Z` (UTC) becomes `+00:00`; an all-zero fractional part
/// is dropped (Python omits microseconds when zero). Anything already carrying a
/// numeric offset is returned unchanged.
fn normalize_timestamp(s: &str) -> String {
    let Some(body) = s.strip_suffix('Z') else {
        return s.to_string();
    };
    // Drop a fractional second that is entirely zeros (`.0`, `.000000`, ...),
    // which Python's isoformat leaves off.
    let body = match body.split_once('.') {
        Some((head, frac)) if frac.chars().all(|c| c == '0') => head,
        _ => body,
    };
    format!("{body}+00:00")
}

/// One `Stamped<T>` field: reads `raw_key` (the published JSON key, e.g.
/// `"Value"`) off the parent and exposes it as GraphQL field `name` (e.g.
/// `"value"`).
fn stamped_wrapper_field(name: &str, raw_key: &str, type_ref: TypeRef) -> Field {
    let raw_key = raw_key.to_string();
    Field::new(name, type_ref, move |ctx| {
        let raw_key = raw_key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map
                    .get(&Name::new(&raw_key))
                    .cloned()
                    .unwrap_or(GraphQlValue::Null),
                _ => GraphQlValue::Null,
            };
            Ok(nullable(value))
        })
    })
}

/// A resolved value as a `FieldValue`, with JSON null as GraphQL null (an
/// enum-typed field rejects `Value::Null` as "not an item").
fn nullable(value: GraphQlValue) -> Option<FieldValue<'static>> {
    match value {
        GraphQlValue::Null => None,
        v => Some(FieldValue::value(v)),
    }
}

/// Every distinct `Stamped<T>` type used across topics and groups,
/// deduped by inner scalar type so each one is registered exactly once.
fn register_stamped_wrapper_objects(
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    module_views: &[ModuleView],
    simulation: Option<&SimulationView>,
) -> Vec<Object> {
    let mut inner_types: BTreeSet<String> = BTreeSet::new();
    let all_fields = topics
        .iter()
        .flat_map(|t| t.fields.iter())
        .chain(groups.iter().flat_map(|g| g.fields.iter()));
    for field in all_fields {
        if let Some(inner) = field.graphql_type.strip_prefix("Stamped:") {
            inner_types.insert(inner.to_string());
        }
    }
    // Module-view leaves are Stamped<Inner> too; the inner scalar comes
    // straight from the spec (`ModuleLeafDef::type`). This covers sensorValues
    // fields and the component fields of the whole-object sections
    // (controlValues/controllerState), which share the same leaf shape.
    let section_leaves = module_views
        .iter()
        .flat_map(|v| {
            [&v.control_values, &v.parameters, &v.controller_state]
                .into_iter()
                .flatten()
        })
        .flat_map(|s| s.fields.iter())
        .flat_map(|f| f.leaves.iter());
    let simulation_leaves = simulation
        .into_iter()
        .flat_map(|sim| sim.simulations.iter())
        .flat_map(|s| s.inputs.fields.iter().chain(s.outputs.fields.iter()))
        .flat_map(|f| f.leaves.iter());
    // View leaves get thrs-api's own wrapper types (named and nullable exactly
    // like Strawberry's `FloatStampedType` etc.), one per distinct name.
    let mut view_wrappers: BTreeMap<String, Object> = BTreeMap::new();
    for leaf in module_views
        .iter()
        .flat_map(|v| v.sensor_values.iter())
        .flat_map(|f| f.leaves.iter())
        .chain(section_leaves)
        .chain(simulation_leaves)
    {
        view_wrappers
            .entry(view_stamped_type_name(leaf))
            .or_insert_with(|| view_stamped_object(leaf));
    }
    inner_types
        .into_iter()
        .map(|inner| stamped_wrapper_object(&inner))
        .chain(view_wrappers.into_values())
        .collect()
}

/// Validate that sanitized topic and field names are unique and not reserved.
///
/// Returns an error if:
/// - any topic sanitizes to an empty name
/// - any topic sanitizes to a reserved GraphQL name
/// - two topics sanitize to the same GraphQL name
/// - any field sanitizes to an empty name
/// - two fields within the same topic sanitize to the same name
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

/// Validate one topic's payload fields: unique raw names, plus non-empty
/// and unique sanitized GraphQL names.
fn validate_topic_fields(topic: &str, fields: &[FieldDef]) -> anyhow::Result<()> {
    let mut seen_fields: BTreeMap<String, String> = BTreeMap::new();
    let mut seen_raw_fields: BTreeSet<String> = BTreeSet::new();
    for field in fields {
        // Raw duplicate (should also be caught by sanitized check, but give clearer error)
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

/// Derive a GraphQL scalar type name from a (possibly `$ref`'d) subschema.
pub(crate) fn graphql_type_for_subschema(sub: &SubSchema, doc: &Document) -> Option<String> {
    match sub {
        SubSchema::Bool(_) => None,
        SubSchema::Schema(boxed) => match boxed.as_ref() {
            RefOr::Item(schema) => type_from_schema(schema, doc),
            RefOr::Reference(r) => {
                let key = r.component_key("schemas")?;
                let entry = doc.components.as_ref()?.schemas.get(&key)?;
                let resolved = entry.item()?;
                match resolved {
                    SchemaOrMultiFormat::Schema(s) => type_from_schema(s, doc),
                    SchemaOrMultiFormat::MultiFormat(mf) => {
                        let schema: AsyncApiSchema =
                            serde_json::from_value(mf.schema.clone()).ok()?;
                        type_from_schema(&schema, doc)
                    }
                    SchemaOrMultiFormat::Bool(_) => None,
                }
            }
        },
    }
}

fn type_from_schema(schema: &AsyncApiSchema, doc: &Document) -> Option<String> {
    if let Some(schema_type) = &schema.schema_type {
        return match schema_type {
            SchemaType::Single(t) => map_json_type_to_graphql(t),
            SchemaType::Multiple(types) => {
                for t in types {
                    if t == "null" {
                        continue;
                    }
                    if let Some(gql) = map_json_type_to_graphql(t) {
                        return Some(gql.to_string());
                    }
                }
                None
            }
        };
    }

    // Handle nullable via anyOf / oneOf / allOf
    if let Some(any_of) = &schema.any_of {
        for sub in any_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }
    if let Some(one_of) = &schema.one_of {
        for sub in one_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }
    if let Some(all_of) = &schema.all_of {
        for sub in all_of {
            if let Some(t) = graphql_type_for_subschema(sub, doc) {
                return Some(t);
            }
        }
    }

    None
}

fn map_json_type_to_graphql(t: &str) -> Option<String> {
    match t {
        "number" => Some("Float".to_string()),
        "integer" => Some("Int".to_string()),
        "boolean" => Some("Boolean".to_string()),
        "string" => Some("String".to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::asyncapi::FieldDef;
    use crate::http::router;
    use axum::http::StatusCode;
    use serde_json::json;
    use tower::ServiceExt;

    #[test]
    fn test_check_bounds_accepts_in_range_and_rejects_out_of_range() {
        use crate::mutations_view::Bounds;
        let b = Bounds {
            min: Some(0.0),
            max: Some(360.0),
            exclusive_min: None,
            exclusive_max: None,
        };
        assert!(check_bounds(&b, 0.0).is_ok());
        assert!(check_bounds(&b, 360.0).is_ok());
        assert!(check_bounds(&b, -0.1).is_err());
        assert!(check_bounds(&b, 360.1).is_err());

        let excl = Bounds {
            min: None,
            max: None,
            exclusive_min: Some(0.0),
            exclusive_max: Some(1.0),
        };
        assert!(check_bounds(&excl, 0.0).is_err());
        assert!(check_bounds(&excl, 1.0).is_err());
        assert!(check_bounds(&excl, 0.5).is_ok());
    }

    #[test]
    fn test_build_schema_for_one_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![
                FieldDef {
                    name: "value".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "ok".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        let _schema = build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();
        // Schema builds without panicking
    }

    #[test]
    fn test_colliding_sanitized_topics_error() {
        // "a/b" and "a-b" both sanitize to "a_b" — should error rather than suffix
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![FieldDef {
                    name: "x".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "a-b".to_string(),
                fields: vec![FieldDef {
                    name: "y".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let err = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap_err();
        assert!(
            err.to_string().contains("duplicate sanitized topic name"),
            "{err}"
        );
    }

    #[test]
    fn test_reserved_topic_name_errors() {
        let topics = vec![TopicDef {
            topic: "Query".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let err = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap_err();
        assert!(err.to_string().contains("reserved"), "{err}");
    }

    #[test]
    fn test_digit_prefixed_topic_is_valid() {
        let topics = vec![TopicDef {
            topic: "123/topic".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("_123Topic"), "{sdl}");
    }

    #[test]
    fn test_empty_topic_is_listed_but_not_queryable() {
        // A topic without scalar fields must not crash schema building;
        // it stays visible via `topics` but has no query type.
        let topics = vec![TopicDef {
            topic: "empty/topic".to_string(),
            fields: vec![],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("emptyTopic"), "{sdl}");
    }

    #[test]
    fn test_field_types_in_schema() {
        let topics = vec![TopicDef {
            topic: "t".to_string(),
            fields: vec![
                FieldDef {
                    name: "f_float".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "f_int".to_string(),
                    graphql_type: "Int".to_string(),
                },
                FieldDef {
                    name: "f_bool".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
                FieldDef {
                    name: "f_str".to_string(),
                    graphql_type: "String".to_string(),
                },
                FieldDef {
                    name: "f_unknown".to_string(),
                    graphql_type: "DateTime".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(sdl.contains("fFloat: Float"), "{sdl}");
        assert!(sdl.contains("fInt: Int"), "{sdl}");
        assert!(sdl.contains("fBool: Boolean"), "{sdl}");
        assert!(sdl.contains("fStr: String"), "{sdl}");
        // Unknown types fall back to String
        assert!(sdl.contains("fUnknown: String"), "{sdl}");
    }

    #[tokio::test]
    async fn test_query_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![
                FieldDef {
                    name: "value".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "ok".to_string(),
                    graphql_type: "Boolean".to_string(),
                },
                FieldDef {
                    name: "label".to_string(),
                    graphql_type: "String".to_string(),
                },
            ],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "test/channel",
            json!({"value": 23.5, "ok": true, "label": "hello"}),
        );
        let schema = build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ testChannel { value ok label } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"]["value"], json!(23.5));
        assert_eq!(data["testChannel"]["ok"], json!(true));
        assert_eq!(data["testChannel"]["label"], json!("hello"));
    }

    fn thrusters_module_view() -> Vec<ModuleView> {
        vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            control_mode: None,
            control_values: None,
            parameters: None,
            controller_state: None,
            sensor_values: vec![ModuleFieldDef {
                gql_field: "thrustersFlowcontrolAft".to_string(),
                type_name: "thrustersFlowcontrolAftType".into(),
                topic: "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft".to_string(),
                leaves: vec![
                    ModuleLeafDef {
                        gql: "positionRel".to_string(),
                        raw: "PositionRel".to_string(),
                        r#type: "Float".to_string(),
                        enum_values: None,
                        enum_type: None,
                        optional: false,
                        actuated_raw: None,
                        default: None,
                    },
                    ModuleLeafDef {
                        gql: "positionAbs".to_string(),
                        raw: "PositionAbs".to_string(),
                        r#type: "Float".to_string(),
                        enum_values: None,
                        enum_type: None,
                        optional: false,
                        actuated_raw: None,
                        default: None,
                    },
                ],
                computed: false,
                input_only: false,
            }],
        }]
    }

    #[tokio::test]
    async fn test_nested_module_view_returns_camelcase_leaves() {
        // Leaf names must be thrs-api's camelCase (positionRel), not the flat
        // schema's lowercased positionrel, and value/timestamp come from the
        // cached PascalCase payload.
        let topic = "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft";
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            topic,
            json!({
                "PositionRel": {"Value": 0.75, "TimeStamp": "2024-01-01T00:00:00Z"},
                "PositionAbs": {"Value": 270.0, "TimeStamp": "2024-01-01T00:00:00Z"}
            }),
        );
        let schema = build_schema(
            cache,
            SchemaInputs {
                module_views: &thrusters_module_view(),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute(
                "{ modules { thrusters { sensorValues { thrustersFlowcontrolAft { \
                 positionRel { value timestamp } positionAbs { value } } } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let field = &data["modules"]["thrusters"]["sensorValues"]["thrustersFlowcontrolAft"];
        assert_eq!(field["positionRel"]["value"], json!(0.75));
        // Timestamps are normalized to thrs-api's `+00:00` shape (a UTC `Z` on
        // the wire becomes `+00:00`), so the two APIs match byte for byte.
        assert_eq!(
            field["positionRel"]["timestamp"],
            json!("2024-01-01T00:00:00+00:00")
        );
        assert_eq!(field["positionAbs"]["value"], json!(270.0));
    }

    #[tokio::test]
    async fn test_nested_module_view_null_when_uncached() {
        // A field with no cached payload resolves to null (not an error).
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                module_views: &thrusters_module_view(),
                ..Default::default()
            },
        )
        .unwrap();
        let response = schema
            .execute(
                "{ modules { thrusters { sensorValues { thrustersFlowcontrolAft { \
                 positionRel { value } } } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(
            data["modules"]["thrusters"]["sensorValues"]["thrustersFlowcontrolAft"],
            json!(null)
        );
    }

    #[tokio::test]
    async fn test_nested_module_view_dedupes_colliding_gql_field() {
        // Two distinct snake_case model fields can collapse to the same
        // camelCase name (pvt_flow_main_string1_2 / pvt_flow_main_string12 ->
        // pvtFlowMainString12). The schema must still build (async-graphql
        // panics on a duplicate field) by keeping the first and skipping the
        // rest, so one ambiguous field never crashes the service.
        let first_topic = "simulation/500000-thrs/pvt/pvt-flow-main-string1-2";
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            first_topic,
            json!({"Flow": {"Value": 1.5, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let leaf = || {
            vec![ModuleLeafDef {
                gql: "flow".to_string(),
                raw: "Flow".to_string(),
                r#type: "Float".to_string(),
                enum_values: None,
                enum_type: None,
                optional: false,
                actuated_raw: None,
                default: None,
            }]
        };
        let views = vec![ModuleView {
            module: "pvt".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "PvtControlModule".into(),
            sensor_values_type_name: "PvtSensorValuesType".into(),
            control_mode: None,
            control_values: None,
            parameters: None,
            controller_state: None,
            sensor_values: vec![
                ModuleFieldDef {
                    gql_field: "pvtFlowMainString12".to_string(),
                    type_name: "pvtFlowMainString12Type".into(),
                    topic: first_topic.to_string(),
                    leaves: leaf(),
                    computed: false,
                    input_only: false,
                },
                ModuleFieldDef {
                    gql_field: "pvtFlowMainString12".to_string(),
                    type_name: "pvtFlowMainString12Type".into(),
                    topic: "simulation/500000-thrs/pvt/pvt-flow-main-string12".to_string(),
                    leaves: leaf(),
                    computed: false,
                    input_only: false,
                },
            ],
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let response = schema
            .execute(
                "{ modules { pvt { sensorValues { pvtFlowMainString12 { flow { value } } } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        // The kept (first) field resolves from its own topic's cached payload.
        assert_eq!(
            data["modules"]["pvt"]["sensorValues"]["pvtFlowMainString12"]["flow"]["value"],
            json!(1.5)
        );
    }

    #[test]
    fn test_normalize_timestamp_matches_thrs_api_shape() {
        // A UTC `Z` becomes `+00:00`; an all-zero fractional is dropped; an
        // explicit offset is left untouched.
        assert_eq!(
            normalize_timestamp("2026-09-12T19:34:51.561515Z"),
            "2026-09-12T19:34:51.561515+00:00"
        );
        assert_eq!(
            normalize_timestamp("2026-09-12T19:34:51Z"),
            "2026-09-12T19:34:51+00:00"
        );
        assert_eq!(
            normalize_timestamp("2026-09-12T19:34:51.000000Z"),
            "2026-09-12T19:34:51+00:00"
        );
        assert_eq!(
            normalize_timestamp("2026-09-11T09:45:40.697018+00:00"),
            "2026-09-11T09:45:40.697018+00:00"
        );
    }

    #[tokio::test]
    async fn test_object_section_parameters_flat_and_empty_controller_state() {
        // parameters is one whole-object topic: flat scalar + list fields are
        // pulled out of the cached object by their PascalCase keys. An empty
        // controllerState (no fields) must still form a valid, null-resolving
        // section (thrs-api's `_empty` placeholder).
        let params_topic = "thrs/controller/thrusters/parameters";
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            params_topic,
            json!({"CoolingFlow": 25.0, "PumpTuning": [0.01, 0.001, 0.0]}),
        );
        let views = vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            control_mode: None,
            parameters: Some(ObjectSectionDef {
                topic: params_topic.to_string(),
                type_name: "ThrustersParametersType".into(),
                fields: vec![
                    ObjectFieldDef {
                        gql_field: "coolingFlow".to_string(),
                        key: "CoolingFlow".to_string(),
                        topic: None,
                        type_name: None,
                        optional: false,
                        r#type: Some("Float".to_string()),
                        leaves: vec![],
                    },
                    ObjectFieldDef {
                        gql_field: "pumpTuning".to_string(),
                        key: "PumpTuning".to_string(),
                        topic: None,
                        type_name: None,
                        optional: false,
                        r#type: Some("[Float!]".to_string()),
                        leaves: vec![],
                    },
                ],
            }),
            controller_state: Some(ObjectSectionDef {
                topic: "thrs/controller/thrusters/controller-state".to_string(),
                type_name: "ThrustersControllerStateType".into(),
                fields: vec![],
            }),
            // Every real module has sensor fields; one keeps the SensorValues
            // object non-empty (an empty GraphQL object is invalid).
            sensor_values: vec![ModuleFieldDef {
                gql_field: "thrustersFlowAft".to_string(),
                type_name: "thrustersFlowAftType".into(),
                topic: "simulation/500000-thrs/thrusters/thrusters-flow-aft".to_string(),
                leaves: vec![ModuleLeafDef {
                    gql: "flow".to_string(),
                    raw: "Flow".to_string(),
                    r#type: "Float".to_string(),
                    enum_values: None,
                    enum_type: None,
                    optional: false,
                    actuated_raw: None,
                    default: None,
                }],
                computed: false,
                input_only: false,
            }],
            ..Default::default()
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let response = schema
            .execute(
                "{ modules { thrusters { \
                 parameters { coolingFlow pumpTuning } \
                 controllerState { Empty } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let params = &data["modules"]["thrusters"]["parameters"];
        assert_eq!(params["coolingFlow"], json!(25.0));
        assert_eq!(params["pumpTuning"], json!([0.01, 0.001, 0.0]));
        // No controller-state object cached -> the whole section resolves null,
        // exactly like thrs-api returning null for an unpublished section.
        assert_eq!(data["modules"]["thrusters"]["controllerState"], json!(null));
    }

    #[tokio::test]
    async fn test_nested_module_view_maps_enum_leaf_to_member_name() {
        // An enum leaf (type String + enumValues) must resolve `value` to the
        // thrs-api member name, not the raw wire value: int 0 -> "LOCAL",
        // str "off" -> "OFF". Unmapped values pass through untouched.
        let mode_topic = "simulation/500000-thrs/thrusters/mode";
        let pcs_topic = "simulation/500000-thrs/thrusters/pcs-mode";
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            mode_topic,
            json!({"Mode": {"Value": 0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        cache.insert(
            pcs_topic,
            json!({"Mode": {"Value": "off", "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let enum_leaf = |enum_type: &str, raw_to_name: &[(&str, &str)]| ModuleLeafDef {
            gql: "mode".to_string(),
            raw: "Mode".to_string(),
            r#type: "String".to_string(),
            enum_values: Some(
                raw_to_name
                    .iter()
                    .map(|(k, v)| (k.to_string(), v.to_string()))
                    .collect(),
            ),
            enum_type: Some(enum_type.to_string()),
            optional: false,
            actuated_raw: None,
            default: None,
        };
        let views = vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            control_mode: None,
            control_values: None,
            parameters: None,
            controller_state: None,
            sensor_values: vec![
                ModuleFieldDef {
                    gql_field: "mode".to_string(),
                    type_name: "modeType".into(),
                    topic: mode_topic.to_string(),
                    leaves: vec![enum_leaf("ControlMode", &[("0", "LOCAL"), ("1", "MANUAL")])],
                    computed: false,
                    input_only: false,
                },
                ModuleFieldDef {
                    gql_field: "thrustersPcs".to_string(),
                    type_name: "thrustersPcsType".into(),
                    topic: pcs_topic.to_string(),
                    leaves: vec![enum_leaf("PcsMode", &[("off", "OFF"), ("on", "ON")])],
                    computed: false,
                    input_only: false,
                },
            ],
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let response = schema
            .execute(
                "{ modules { thrusters { sensorValues { \
                 mode { mode { value timestamp } } \
                 thrustersPcs { mode { value } } } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let sv = &data["modules"]["thrusters"]["sensorValues"];
        assert_eq!(sv["mode"]["mode"]["value"], json!("LOCAL"));
        assert_eq!(
            sv["mode"]["mode"]["timestamp"],
            json!("2024-01-01T00:00:00+00:00")
        );
        assert_eq!(sv["thrustersPcs"]["mode"]["value"], json!("OFF"));
    }

    struct CapturingPublisher {
        sent: Arc<std::sync::Mutex<Vec<(String, String)>>>,
    }

    impl TopicPublisher for CapturingPublisher {
        fn publish(&self, topic: String, payload: String) -> PublishFuture {
            let sent = self.sent.clone();
            Box::pin(async move {
                sent.lock().unwrap().push((topic, payload));
                Ok(())
            })
        }
    }

    fn cooling_flow_mutation() -> Vec<ModuleMutations> {
        vec![ModuleMutations {
            module: "thrusters".to_string(),
            mutations: vec![MutationDef {
                derived: Vec::new(),
                gql_name: "thrustersParameterSetCoolingFlow".to_string(),
                kind: "parameter".to_string(),
                arg_type: "Float".to_string(),
                arg_name: "value".to_string(),
                payload_key: "CoolingFlow".to_string(),
                state_topic: "thrs/controller/thrusters/parameters".to_string(),
                set_topic: "thrs/controller/thrusters/parameters/set".to_string(),
                bounds: None,
                true_value: None,
                false_value: None,
                input_fields: Vec::new(),
                input_type_name: None,
                missing_error: Some("No parameters available to update".to_string()),
            }],
            parameters_object: Default::default(),
            control_values_object: Default::default(),
        }]
    }

    #[tokio::test]
    async fn test_mutation_reads_cache_modifies_and_publishes() {
        // A parameter mutation overwrites one field of the cached object and
        // publishes the whole object to the set topic; other fields untouched.
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "thrs/controller/thrusters/parameters",
            json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0}),
        );
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });

        let schema = build_schema(
            cache,
            SchemaInputs {
                mutations: &cooling_flow_mutation(),
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute("mutation { thrustersParameterSetCoolingFlow(value: 12.34) }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["thrustersParameterSetCoolingFlow"], json!(true));

        let sent = sent.lock().unwrap();
        assert_eq!(sent.len(), 1, "expected exactly one publish");
        assert_eq!(sent[0].0, "thrs/controller/thrusters/parameters/set");
        let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
        assert_eq!(published["CoolingFlow"], json!(12.34), "field set to arg");
        assert_eq!(
            published["WarmupTemperature"],
            json!(60.0),
            "other fields preserved"
        );
    }

    #[tokio::test]
    async fn test_mutation_errors_and_publishes_nothing_when_state_uncached() {
        // With no cached parameters object, the mutation errors (like thrs-api's
        // "No parameters available to update") and publishes nothing.
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                mutations: &cooling_flow_mutation(),
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute("mutation { thrustersParameterSetCoolingFlow(value: 12.34) }")
            .await;
        assert!(!response.errors.is_empty(), "expected an error");
        assert!(
            sent.lock().unwrap().is_empty(),
            "nothing should be published"
        );
    }

    #[tokio::test]
    async fn test_control_mutation_restamps_component_and_publishes() {
        use crate::mutations_view::InputFieldDef;
        let cache = Arc::new(TopicCache::new());
        // Seed a manual-values object with two components; only one is set.
        cache.insert(
            "thrs/controller/thrusters/manual-values",
            json!({
                "thrusters_pump_1": {"Dutypoint": {"Value": 0.5, "TimeStamp": "old"}},
                "thrusters_flowcontrol_aft": {"Setpoint": {"Value": 0.0, "TimeStamp": "old"}}
            }),
        );
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });
        let mut enum_values = std::collections::BTreeMap::new();
        enum_values.insert("1".to_string(), "CONSTANT_SPEED".to_string());
        let mutations = vec![ModuleMutations {
            module: "thrusters".to_string(),
            mutations: vec![MutationDef {
                derived: Vec::new(),
                gql_name: "thrustersControlSetThrustersPump1".to_string(),
                kind: "control".to_string(),
                arg_type: "Float".to_string(),
                arg_name: "value".to_string(),
                payload_key: "thrusters_pump_1".to_string(),
                state_topic: "thrs/controller/thrusters/manual-values".to_string(),
                set_topic: "thrs/controller/thrusters/manual-values/set".to_string(),
                bounds: None,
                true_value: None,
                false_value: None,
                input_type_name: Some("PumpInputType".to_string()),
                missing_error: None,
                input_fields: vec![
                    InputFieldDef {
                        arg_name: "dutypoint".to_string(),
                        wire_key: "Dutypoint".to_string(),
                        r#type: "Float".to_string(),
                        enum_values: None,
                        enum_type: None,
                        required: true,
                    },
                    InputFieldDef {
                        arg_name: "on".to_string(),
                        wire_key: "On".to_string(),
                        r#type: "Boolean".to_string(),
                        enum_values: None,
                        enum_type: None,
                        required: true,
                    },
                    InputFieldDef {
                        arg_name: "controlMode".to_string(),
                        wire_key: "ControlMode".to_string(),
                        r#type: "String".to_string(),
                        enum_values: Some(enum_values),
                        enum_type: Some("PumpControlMode".to_string()),
                        required: true,
                    },
                ],
            }],
            parameters_object: Default::default(),
            control_values_object: Default::default(),
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                mutations: &mutations,
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();

        let resp = schema
            .execute(
                "mutation { thrustersControlSetThrustersPump1(value: \
                 { dutypoint: 0.8, on: true, controlMode: CONSTANT_SPEED }) }",
            )
            .await;
        assert!(resp.errors.is_empty(), "{:?}", resp.errors);

        let sent = sent.lock().unwrap();
        assert_eq!(sent.len(), 1);
        assert_eq!(sent[0].0, "thrs/controller/thrusters/manual-values/set");
        let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
        let comp = &published["thrusters_pump_1"];
        assert_eq!(comp["Dutypoint"]["Value"], json!(0.8));
        assert_eq!(comp["On"]["Value"], json!(true));
        // Enum member mapped back to its wire value (1), stored as a number.
        assert_eq!(comp["ControlMode"]["Value"], json!(1));
        // Each leaf got a fresh (non-"old") timestamp.
        assert_ne!(comp["Dutypoint"]["TimeStamp"], json!("old"));
        // The other component is preserved untouched.
        assert_eq!(
            published["thrusters_flowcontrol_aft"]["Setpoint"]["Value"],
            json!(0.0)
        );
        // The republished object has exactly the seeded components as
        // top-level keys: the cache's flattened field view (which also holds
        // the leaf keys `Dutypoint`/`Setpoint` at the top level) must not
        // leak into what the controller receives.
        let mut keys: Vec<&String> = published.as_object().unwrap().keys().collect();
        keys.sort();
        assert_eq!(
            keys,
            vec!["thrusters_flowcontrol_aft", "thrusters_pump_1"],
            "republished object carries flattened keys: {published}"
        );
    }

    #[tokio::test]
    async fn test_parameter_mutation_returns_modified_object_and_automation_mode() {
        use crate::modules_view::ObjectFieldDef;
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "thrs/controller/thrusters/parameters",
            json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0}),
        );
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });
        let mutations = vec![ModuleMutations {
            module: "thrusters".to_string(),
            mutations: vec![
                MutationDef {
                    derived: Vec::new(),
                    gql_name: "thrustersParameterSetCoolingFlow".to_string(),
                    kind: "parameter".to_string(),
                    arg_type: "Float".to_string(),
                    arg_name: "value".to_string(),
                    payload_key: "CoolingFlow".to_string(),
                    state_topic: "thrs/controller/thrusters/parameters".to_string(),
                    set_topic: "thrs/controller/thrusters/parameters/set".to_string(),
                    bounds: None,
                    true_value: None,
                    false_value: None,
                    input_fields: Vec::new(),
                    input_type_name: None,
                    missing_error: None,
                },
                MutationDef {
                    derived: Vec::new(),
                    gql_name: "thrustersSetAutomationMode".to_string(),
                    kind: "automationMode".to_string(),
                    arg_type: "Boolean".to_string(),
                    arg_name: "automatic".to_string(),
                    payload_key: "Mode".to_string(),
                    state_topic: "thrs/controller/thrusters/automation-mode".to_string(),
                    set_topic: "thrs/controller/thrusters/automation-mode/set".to_string(),
                    bounds: None,
                    true_value: Some("automatic".to_string()),
                    false_value: Some("manual".to_string()),
                    input_fields: Vec::new(),
                    input_type_name: None,
                    missing_error: None,
                },
            ],
            parameters_object: ObjectSectionDef {
                topic: String::new(),
                type_name: "ThrustersParametersType".into(),
                fields: vec![
                    ObjectFieldDef {
                        gql_field: "coolingFlow".to_string(),
                        key: "CoolingFlow".to_string(),
                        topic: None,
                        r#type: Some("Float".to_string()),
                        type_name: None,
                        optional: false,
                        leaves: Vec::new(),
                    },
                    ObjectFieldDef {
                        gql_field: "warmupTemperature".to_string(),
                        key: "WarmupTemperature".to_string(),
                        topic: None,
                        r#type: Some("Float".to_string()),
                        type_name: None,
                        optional: false,
                        leaves: Vec::new(),
                    },
                ],
            },
            control_values_object: Default::default(),
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                mutations: &mutations,
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();

        // Parameter mutation returns the modified parameters object.
        let resp = schema
            .execute(
                "mutation { thrustersParameterSetCoolingFlow(value: 12.34) \
                 { coolingFlow warmupTemperature } }",
            )
            .await;
        assert!(resp.errors.is_empty(), "{:?}", resp.errors);
        let data: serde_json::Value = resp.data.into_json().unwrap();
        let obj = &data["thrustersParameterSetCoolingFlow"];
        assert_eq!(obj["coolingFlow"], json!(12.34), "modified field returned");
        assert_eq!(
            obj["warmupTemperature"],
            json!(60.0),
            "other field returned"
        );

        // Automation-mode returns Boolean and publishes a fresh {"Mode": ...}.
        let resp = schema
            .execute("mutation { thrustersSetAutomationMode(automatic: false) }")
            .await;
        assert!(resp.errors.is_empty(), "{:?}", resp.errors);
        let data: serde_json::Value = resp.data.into_json().unwrap();
        // thrs-api's set_automation_mode returns the `automatic` it was given.
        assert_eq!(data["thrustersSetAutomationMode"], json!(false));
        let sent = sent.lock().unwrap();
        let am = sent
            .iter()
            .find(|(t, _)| t == "thrs/controller/thrusters/automation-mode/set")
            .expect("automation-mode publish");
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(&am.1).unwrap(),
            json!({"Mode": "manual"})
        );
    }

    #[tokio::test]
    async fn test_simulation_mutation_rederives_mirror_fields_from_the_new_component() {
        use crate::mutations_view::{DerivedFieldDef, DerivedLeaf, InputFieldDef};
        // dhw's inputs: `DrivesFlowRecovery` mirrors `DhwDrivesSupply`'s flow
        // and temperature (a pydantic computed_field thrs-api re-serializes).
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "thrs/simulator/simulation-inputs",
            json!({
                "DhwDrivesSupply": {
                    "Flow": {"Value": 1.0, "TimeStamp": "old"},
                    "Temperature": {"Value": 2.0, "TimeStamp": "old"}
                },
                "DrivesFlowRecovery": {
                    "Flow": {"Value": 1.0, "TimeStamp": "old"},
                    "Temperature": {"Value": 2.0, "TimeStamp": "old"}
                },
                "Mode": {"Value": 0, "TimeStamp": "old"}
            }),
        );
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });
        let leaf = |arg: &str, wire: &str| InputFieldDef {
            arg_name: arg.to_string(),
            wire_key: wire.to_string(),
            r#type: "Float".to_string(),
            enum_values: None,
            enum_type: None,
            required: true,
        };
        let mut leaves = BTreeMap::new();
        for (k, v) in [("Flow", "Flow"), ("Temperature", "Temperature")] {
            leaves.insert(
                k.to_string(),
                DerivedLeaf::Source {
                    component: "DhwDrivesSupply".to_string(),
                    leaf: v.to_string(),
                },
            );
        }
        let mutations = vec![ModuleMutations {
            module: "dhw".to_string(),
            mutations: vec![MutationDef {
                gql_name: "dhwSimulationSetDhwDrivesSupply".to_string(),
                kind: "control".to_string(),
                arg_type: String::new(),
                arg_name: "value".to_string(),
                payload_key: "DhwDrivesSupply".to_string(),
                state_topic: "thrs/simulator/simulation-inputs".to_string(),
                set_topic: "thrs/simulator/simulation-inputs/set".to_string(),
                bounds: None,
                true_value: None,
                false_value: None,
                input_type_name: Some("BoundaryInputType".to_string()),
                missing_error: None,
                input_fields: vec![leaf("flow", "Flow"), leaf("temperature", "Temperature")],
                derived: vec![DerivedFieldDef {
                    key: "DrivesFlowRecovery".to_string(),
                    leaves,
                }],
            }],
            parameters_object: Default::default(),
            control_values_object: Default::default(),
        }];
        let schema = build_schema(
            cache,
            SchemaInputs {
                mutations: &mutations,
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();
        let resp = schema
            .execute(
                "mutation { dhwSimulationSetDhwDrivesSupply(value: { flow: 0.5, temperature: 0.25 }) }",
            )
            .await;
        assert!(resp.errors.is_empty(), "{:?}", resp.errors);
        let sent = sent.lock().unwrap();
        let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
        // The mirror carries the new component's leaves verbatim (value and
        // the fresh timestamp), exactly like thrs-api's re-serialized model.
        assert_eq!(
            published["DrivesFlowRecovery"],
            published["DhwDrivesSupply"]
        );
        assert_eq!(published["DrivesFlowRecovery"]["Flow"]["Value"], json!(0.5));
        assert_ne!(
            published["DrivesFlowRecovery"]["Flow"]["TimeStamp"],
            json!("old")
        );
        assert_eq!(published["Mode"]["Value"], json!(0));
    }

    #[test]
    fn test_duplicate_input_type_keeps_first_definition() {
        // Two mutations naming their input `AdsorptionChillerInputType` with
        // different fields (control vs. simulation component): the schema
        // serves the first one, like thrs-api's Strawberry.
        let control = InputObject::new("AdsorptionChillerInputType")
            .field(InputValue::new(
                "enable",
                TypeRef::named_nn(TypeRef::BOOLEAN),
            ))
            .field(InputValue::new(
                "coolingSetpoint",
                TypeRef::named_nn(TypeRef::FLOAT),
            ));
        let simulation = InputObject::new("AdsorptionChillerInputType").field(InputValue::new(
            "freeCooling",
            TypeRef::named_nn(TypeRef::BOOLEAN),
        ));
        let mutation = Object::new("Mutation").field(
            Field::new("set", TypeRef::named_nn(TypeRef::BOOLEAN), |_| {
                FieldFuture::new(async { Ok(Some(FieldValue::value(true))) })
            })
            .argument(InputValue::new(
                "value",
                TypeRef::named_nn("AdsorptionChillerInputType"),
            )),
        );
        let query = Object::new("Query").field(Field::new(
            "ok",
            TypeRef::named_nn(TypeRef::BOOLEAN),
            |_| FieldFuture::new(async { Ok(Some(FieldValue::value(true))) }),
        ));
        let schema = finish_schema(
            query,
            Some(mutation),
            vec![control.into(), simulation.into()],
        )
        .unwrap();
        let sdl = schema.sdl();
        let def = sdl
            .split("input AdsorptionChillerInputType")
            .nth(1)
            .expect("input type in SDL");
        let def = &def[..def.find('}').unwrap()];
        assert!(
            def.contains("enable") && def.contains("coolingSetpoint"),
            "{def}"
        );
        assert!(!def.contains("freeCooling"), "{def}");
    }

    #[test]
    fn test_no_mutation_type_without_publisher() {
        // Mutations declared but no publisher (read-only deploy): no Mutation
        // type in the schema.
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                mutations: &cooling_flow_mutation(),
                ..Default::default()
            },
        )
        .unwrap();
        assert!(!schema.sdl().contains("type Mutation"), "{}", schema.sdl());
    }

    #[test]
    fn test_no_modules_query_without_module_views() {
        // Without any module-view specs the flat schema is unchanged: no
        // `modules` query field, no `Modules` type.
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("type Modules"), "{sdl}");
    }

    #[tokio::test]
    async fn test_query_returns_null_for_missing_topic() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"], json!(null));
    }

    #[tokio::test]
    async fn test_query_returns_null_for_missing_field() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"other": 1.0}));
        let schema = build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ testChannel { value } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["testChannel"]["value"], json!(null));
    }

    #[tokio::test]
    async fn test_query_unknown_field_errors() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ testChannel { nope } }").await;
        assert!(!response.errors.is_empty());
    }

    #[tokio::test]
    async fn test_topics_field_lists_all_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "c/d".to_string(),
                fields: vec![],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ topics }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["topics"], json!(["a/b", "c/d"]));
    }

    #[tokio::test]
    async fn test_query_multiple_topics() {
        let topics = vec![
            TopicDef {
                topic: "a/b".to_string(),
                fields: vec![FieldDef {
                    name: "x".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
            TopicDef {
                topic: "c/d".to_string(),
                fields: vec![FieldDef {
                    name: "y".to_string(),
                    graphql_type: "Float".to_string(),
                }],
                payload_schema: None,
                ttl_secs: 300,
            },
        ];

        let cache = Arc::new(TopicCache::new());
        cache.insert("a/b", json!({"x": 1.5}));
        cache.insert("c/d", json!({"y": 2.5}));
        let schema = build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema.execute("{ aB { x } cD { y } }").await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["aB"]["x"], json!(1.5));
        assert_eq!(data["cD"]["y"], json!(2.5));
    }

    fn power_tag_group() -> Vec<TopicGroupDef> {
        vec![TopicGroupDef {
            group: "power-tags".to_string(),
            pattern: "power-tags/+/+".to_string(),
            params: vec!["panel".to_string(), "slug".to_string()],
            fields: vec![
                FieldDef {
                    name: "active_power_total".to_string(),
                    graphql_type: "Float".to_string(),
                },
                FieldDef {
                    name: "current_a".to_string(),
                    graphql_type: "Float".to_string(),
                },
            ],
            payload_schema: None,
            field_schemas: BTreeMap::new(),
            value_extensions: BTreeMap::from([
                (
                    "active_power_total".to_string(),
                    BTreeMap::from([("unit".to_string(), "W".to_string())]),
                ),
                (
                    "current_a".to_string(),
                    BTreeMap::from([("unit".to_string(), "A".to_string())]),
                ),
            ]),
            ttl_secs: 300,
        }]
    }

    fn power_tag_metadata() -> Vec<MetadataFile> {
        serde_json::from_value(json!([
            {
                "group": "power-tags",
                "topics": [
                    {
                        "topic": "power-tags/10P1/test-consumer",
                        "metadata": {
                            "panel": "10P1",
                            "slug": "test-consumer",
                            "component": "150F01",
                            "consumer": "TEST CONSUMER"
                        }
                    },
                    {
                        "topic": "power-tags/10P2/no-data",
                        "metadata": {"component": "151F01", "slug": "no-data"}
                    }
                ]
            }
        ]))
        .unwrap()
    }

    #[tokio::test]
    async fn test_group_list_returns_metadata_and_values() {
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(
            cache,
            SchemaInputs {
                groups: &power_tag_group(),
                metadata: &power_tag_metadata(),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute(
                "{ powerTags { topic \
                 metadata { panel component consumer values { name unit } } \
                 values { activePowerTotal } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let rows = data["powerTags"].as_array().unwrap();
        assert_eq!(rows.len(), 2);

        assert_eq!(rows[0]["topic"], json!("power-tags/10P1/test-consumer"));
        assert_eq!(rows[0]["metadata"]["panel"], json!("10P1"));
        assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
        assert_eq!(rows[0]["metadata"]["consumer"], json!("TEST CONSUMER"));
        assert_eq!(
            rows[0]["metadata"]["values"],
            json!([
                {"name": "activePowerTotal", "unit": "W"},
                {"name": "currentA", "unit": "A"}
            ])
        );
        assert_eq!(rows[0]["values"]["activePowerTotal"], json!(42.0));

        // Second row has no cached MQTT data: static fields present, live null
        assert_eq!(rows[1]["topic"], json!("power-tags/10P2/no-data"));
        assert_eq!(rows[1]["metadata"]["panel"], json!(null));
        assert_eq!(rows[1]["metadata"]["component"], json!("151F01"));
        assert_eq!(rows[1]["values"]["activePowerTotal"], json!(null));
    }

    #[tokio::test]
    async fn test_group_without_mqtt_data_serves_static() {
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                groups: &power_tag_group(),
                metadata: &power_tag_metadata(),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute("{ powerTags { metadata { component slug } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let rows = data["powerTags"].as_array().unwrap();
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
        assert_eq!(rows[0]["metadata"]["slug"], json!("test-consumer"));
    }

    #[tokio::test]
    async fn test_group_without_metadata_omits_query_field() {
        // Without metadata there is no enumeration source, so no list field
        // (empty object types would be invalid GraphQL).
        let schema = build_schema(
            Arc::new(TopicCache::new()),
            SchemaInputs {
                groups: &power_tag_group(),
                ..Default::default()
            },
        )
        .unwrap();
        let sdl = schema.sdl();
        assert!(!sdl.contains("powerTags"), "{sdl}");
    }

    #[tokio::test]
    async fn test_group_live_values_expire_to_null() {
        let per_topic =
            std::collections::HashMap::from([("power-tags/10P1/test-consumer".to_string(), 0u64)]);
        let cache = Arc::new(TopicCache::with_ttl(60, per_topic));
        cache.insert("power-tags/10P1/test-consumer", json!({"current_a": 1.0}));
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                groups: &power_tag_group(),
                metadata: &power_tag_metadata(),
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute("{ powerTags { values { currentA } } }")
            .await;
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTags"][0]["values"]["currentA"], json!(null));

        // A topic without a zero-TTL override keeps serving its cached value
        cache.insert("power-tags/10P2/no-data", json!({"current_a": 2.5}));
        let response = schema
            .execute("{ powerTags { values { currentA } } }")
            .await;
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTags"][1]["values"]["currentA"], json!(2.5));
    }

    #[tokio::test]
    async fn test_power_tag_bucket_grouping() {
        // `group_by: "panel"` on the group's metadata file enables bucket queries.
        let mut metadata = power_tag_metadata();
        metadata[0].group_by = Some("panel".to_string());
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            "power-tags/10P1/test-consumer",
            json!({"active_power_total": 42.0}),
        );
        let schema = build_schema(
            cache,
            SchemaInputs {
                groups: &power_tag_group(),
                metadata: &metadata,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute(
                "{ powerTagBuckets { id powerTags { topic values { activePowerTotal } } } \
                 powerTagBucket(id: \"10P1\") { id powerTags { topic } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();

        // Entries without the `group_by` attribute land in the "unknown" bucket.
        let buckets = data["powerTagBuckets"].as_array().unwrap();
        assert_eq!(buckets.len(), 2);
        assert_eq!(buckets[0]["id"], json!("10P1"));
        assert_eq!(
            buckets[0]["powerTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );
        assert_eq!(
            buckets[0]["powerTags"][0]["values"]["activePowerTotal"],
            json!(42.0)
        );
        assert_eq!(buckets[1]["id"], json!("unknown"));
        assert_eq!(
            buckets[1]["powerTags"][0]["topic"],
            json!("power-tags/10P2/no-data")
        );

        assert_eq!(
            data["powerTagBucket"]["powerTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );

        // Unknown bucket ids resolve to null.
        let response = schema
            .execute("{ powerTagBucket(id: \"nope\") { id } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["powerTagBucket"], json!(null));
    }

    #[tokio::test]
    async fn test_grouped_by_queries_are_generic() {
        // Any group whose metadata file declares `group_by` gains grouped
        // queries — the names derive from group + attribute, not from a
        // hardcoded domain.
        let mut group = power_tag_group()[0].clone();
        group.group = "fuel-tags".to_string();
        group.pattern = "fuel-tags/+/+".to_string();
        let mut metadata = power_tag_metadata();
        metadata[0].group = "fuel-tags".to_string();
        metadata[0].group_by = Some("tank".to_string());
        metadata[0].topics[0]
            .metadata
            .insert("tank".to_string(), json!("T01"));

        let cache = Arc::new(TopicCache::new());
        let schema = build_schema(
            cache,
            SchemaInputs {
                groups: &[group],
                metadata: &metadata,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute(
                "{ fuelTagBuckets { id fuelTags { topic } } \
                 fuelTagBucket(id: \"T01\") { id } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();

        // Entries without a `tank` attribute land in the "unknown" bucket.
        let buckets = data["fuelTagBuckets"].as_array().unwrap();
        assert_eq!(buckets.len(), 2);
        assert_eq!(buckets[0]["id"], json!("T01"));
        assert_eq!(
            buckets[0]["fuelTags"][0]["topic"],
            json!("power-tags/10P1/test-consumer")
        );
        assert_eq!(buckets[1]["id"], json!("unknown"));
        assert_eq!(data["fuelTagBucket"]["id"], json!("T01"));
    }

    #[tokio::test]
    async fn test_concrete_topic_gains_metadata_field() {
        let topics = vec![TopicDef {
            topic: "sensor/temp".to_string(),
            fields: vec![FieldDef {
                name: "celsius".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];
        let metadata: Vec<MetadataFile> = serde_json::from_value(json!([
            {
                "group": "sensors",
                "topics": [
                    {"topic": "sensor/temp", "metadata": {"room": "galley"}}
                ]
            }
        ]))
        .unwrap();

        let cache = Arc::new(TopicCache::new());
        cache.insert("sensor/temp", json!({"celsius": 21.5}));
        let schema = build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                metadata: &metadata,
                ..Default::default()
            },
        )
        .unwrap();

        let response = schema
            .execute("{ sensorTemp { celsius metadata { room } } }")
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["sensorTemp"]["celsius"], json!(21.5));
        assert_eq!(data["sensorTemp"]["metadata"]["room"], json!("galley"));
    }

    #[tokio::test]
    async fn test_health_endpoint() {
        let app =
            router(build_schema(Arc::new(TopicCache::new()), SchemaInputs::default()).unwrap());

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

    #[tokio::test]
    async fn test_graphql_endpoint_returns_cached_values() {
        let topics = vec![TopicDef {
            topic: "test/channel".to_string(),
            fields: vec![FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }];

        let cache = Arc::new(TopicCache::new());
        cache.insert("test/channel", json!({"value": 42.0}));
        let app = router(
            build_schema(
                cache,
                SchemaInputs {
                    topics: &topics,
                    ..Default::default()
                },
            )
            .unwrap(),
        );

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

    fn leaf(gql: &str, raw: &str, ty: &str) -> ModuleLeafDef {
        ModuleLeafDef {
            gql: gql.to_string(),
            raw: raw.to_string(),
            r#type: ty.to_string(),
            enum_values: None,
            enum_type: None,
            optional: false,
            actuated_raw: None,
            default: None,
        }
    }

    fn sensor_field(gql: &str, topic: &str) -> ModuleFieldDef {
        ModuleFieldDef {
            gql_field: gql.to_string(),
            type_name: format!("{gql}Type"),
            topic: topic.to_string(),
            leaves: vec![leaf("flow", "Flow", "Float")],
            computed: false,
            input_only: false,
        }
    }

    #[tokio::test]
    async fn test_actuated_control_values_assembled_from_device_topics_and_rekeyed() {
        // thrs-api's controlValues is the actuated control values: one device
        // topic per component read through the `CC_*` keys. The section is
        // null until every component is cached with its required keys, then
        // the shared component type reads the plain aliases.
        let pump_topic = "simulation/500000-thrs/thrusters/thrusters-pump1";
        let valve_topic = "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft";
        let cache = Arc::new(TopicCache::new());
        cache.insert(
            pump_topic,
            json!({
                "Speed": {"Value": 3.0, "TimeStamp": "2024-01-01T00:00:00Z"},
                "CC_DutyPoint": {"Value": 0.42, "TimeStamp": "2024-01-01T00:00:00Z"},
                "CC_OnOff": {"Value": true, "TimeStamp": "2024-01-01T00:00:00Z"}
            }),
        );
        let mut dutypoint = leaf("dutypoint", "Dutypoint", "Float");
        dutypoint.actuated_raw = Some("CC_DutyPoint".to_string());
        let mut on = leaf("on", "On", "Boolean");
        on.actuated_raw = Some("CC_OnOff".to_string());
        let mut setpoint = leaf("setpoint", "Setpoint", "Float");
        setpoint.actuated_raw = Some("CC_Setpoint".to_string());
        let views = vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            control_values: Some(ObjectSectionDef {
                topic: String::new(),
                type_name: "ThrustersControlValuesType".to_string(),
                fields: vec![
                    ObjectFieldDef {
                        gql_field: "thrustersPump1".to_string(),
                        key: "thrusters_pump1".to_string(),
                        topic: Some(pump_topic.to_string()),
                        type_name: Some("ControlPumpType".to_string()),
                        optional: false,
                        r#type: None,
                        leaves: vec![dutypoint, on],
                    },
                    ObjectFieldDef {
                        gql_field: "thrustersFlowcontrolAft".to_string(),
                        key: "thrusters_flowcontrol_aft".to_string(),
                        topic: Some(valve_topic.to_string()),
                        type_name: Some("ControlValveType".to_string()),
                        optional: false,
                        r#type: None,
                        leaves: vec![setpoint],
                    },
                ],
            }),
            sensor_values: vec![sensor_field("thrustersFlowAft", "simulation/x/flow-aft")],
            ..Default::default()
        }];
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let query = "{ modules { thrusters { controlValues { \
                     thrustersPump1 { dutypoint { value } on { value } } \
                     thrustersFlowcontrolAft { setpoint { value } } } } } }";
        // Valve topic missing -> the whole section is null, no errors.
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["modules"]["thrusters"]["controlValues"], json!(null));
        // Valve payload with only the request setpoint (no CC_) is incomplete too.
        cache.insert(
            valve_topic,
            json!({"Setpoint": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["modules"]["thrusters"]["controlValues"], json!(null));
        // Actuated key present -> complete; values come from the CC_ keys.
        cache.insert(
            valve_topic,
            json!({
                "Setpoint": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"},
                "CC_Setpoint": {"Value": 0.5, "TimeStamp": "2024-01-01T00:00:00Z"}
            }),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let cv = &data["modules"]["thrusters"]["controlValues"];
        assert_eq!(cv["thrustersPump1"]["dutypoint"]["value"], json!(0.42));
        assert_eq!(cv["thrustersPump1"]["on"]["value"], json!(true));
        assert_eq!(
            cv["thrustersFlowcontrolAft"]["setpoint"]["value"],
            json!(0.5)
        );
    }

    #[tokio::test]
    async fn test_sensor_values_null_until_every_required_leaf_is_cached() {
        // thrs-api serves sensorValues only once its whole model validates.
        let cache = Arc::new(TopicCache::new());
        let a = "simulation/x/flow-aft";
        let b = "simulation/x/flow-fwd";
        cache.insert(
            a,
            json!({"Flow": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let views = vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            sensor_values: vec![
                sensor_field("thrustersFlowAft", a),
                sensor_field("thrustersFlowFwd", b),
            ],
            ..Default::default()
        }];
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let query =
            "{ modules { thrusters { sensorValues { thrustersFlowAft { flow { value } } } } } }";
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
        // Present but null value for a required leaf is still incomplete.
        cache.insert(
            b,
            json!({"Flow": {"Value": null, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
        cache.insert(
            b,
            json!({"Flow": {"Value": 2.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(
            data["modules"]["thrusters"]["sensorValues"]["thrustersFlowAft"]["flow"]["value"],
            json!(1.0)
        );
    }

    #[tokio::test]
    async fn test_enable_optional_sensor_values_serves_cached_fields_and_nulls_the_rest() {
        // ENABLE_OPTIONAL_SENSOR_VALUES: each sensor field answers on its own topic.
        let cache = Arc::new(TopicCache::new());
        let a = "simulation/x/flow-aft";
        let b = "simulation/x/flow-fwd";
        let views = vec![ModuleView {
            module: "thrusters".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "ThrustersControlModule".into(),
            sensor_values_type_name: "ThrustersSensorValuesType".into(),
            sensor_values: vec![
                sensor_field("thrustersFlowAft", a),
                sensor_field("thrustersFlowFwd", b),
            ],
            ..Default::default()
        }];
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                module_views: &views,
                enable_optional_sensor_values: true,
                ..Default::default()
            },
        )
        .unwrap();
        // The sensor fields are nullable in this mode (schema change).
        let sdl = schema.sdl();
        assert!(
            sdl.contains("thrustersFlowAft: thrustersFlowAftType\n"),
            "expected nullable sensor field in:\n{sdl}"
        );
        let query = "{ modules { thrusters { sensorValues { \
                     thrustersFlowAft { flow { value } } \
                     thrustersFlowFwd { flow { value } } } } } }";
        // Nothing cached yet: the container itself is null, like thrs-api.
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
        // One topic cached: that field serves, the other is null, no errors.
        cache.insert(
            a,
            json!({"Flow": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let sv = &data["modules"]["thrusters"]["sensorValues"];
        assert_eq!(sv["thrustersFlowAft"]["flow"]["value"], json!(1.0));
        assert_eq!(sv["thrustersFlowFwd"], json!(null));
        // A cached payload missing a required leaf value nulls only its field.
        cache.insert(
            b,
            json!({"Flow": {"Value": null, "TimeStamp": "2024-01-01T00:00:00Z"}}),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        let sv = &data["modules"]["thrusters"]["sensorValues"];
        assert_eq!(sv["thrustersFlowAft"]["flow"]["value"], json!(1.0));
        assert_eq!(sv["thrustersFlowFwd"], json!(null));
    }

    #[tokio::test]
    async fn test_control_mode_section_and_empty_placeholder() {
        // `controlMode { automatic automaticMode { ... } }`: null when the
        // topic is absent, `automatic` derived from `AutomaticMode` being
        // non-null, nested groups typed by thrs-api's names, and a fieldless
        // model rendered with the `Empty: Void` placeholder.
        let topic = "thrs/controller/pvt/control-mode";
        let cache = Arc::new(TopicCache::new());
        let group = PlainObjectDef {
            type_name: "PvtGroupControlModeType".to_string(),
            fields: vec![PlainFieldDef {
                gql_field: "mode".to_string(),
                key: "Mode".to_string(),
                r#type: Some("String".to_string()),
                object: None,
                optional: false,
            }],
        };
        let views = vec![ModuleView {
            module: "pvt".to_string(),
            modules_type_name: "ControlModules".into(),
            type_name: "PvtControlModule".into(),
            sensor_values_type_name: "PvtSensorValuesType".into(),
            control_mode: Some(ControlModeDef {
                topic: topic.to_string(),
                type_name: "PvtSwitchingControlModeType".into(),
                key: "AutomaticMode".to_string(),
                automatic_mode: PlainObjectDef {
                    type_name: "PvtControlModeType".to_string(),
                    fields: vec![
                        PlainFieldDef {
                            gql_field: "aft".to_string(),
                            key: "Aft".to_string(),
                            r#type: None,
                            object: Some(group.clone()),
                            optional: false,
                        },
                        PlainFieldDef {
                            gql_field: "empty".to_string(),
                            key: "Empty".to_string(),
                            r#type: None,
                            object: Some(PlainObjectDef {
                                type_name: "ConsumersControlModeType".to_string(),
                                fields: vec![],
                            }),
                            optional: true,
                        },
                    ],
                },
            }),
            sensor_values: vec![sensor_field("pvtFlow", "simulation/x/pvt-flow")],
            ..Default::default()
        }];
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                module_views: &views,
                ..Default::default()
            },
        )
        .unwrap();
        let query = "{ modules { pvt { controlMode { automatic \
                     automaticMode { aft { mode } empty { Empty } } } } } }";
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["modules"]["pvt"]["controlMode"], json!(null));
        cache.insert(topic, json!({"AutomaticMode": null}));
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(
            data["modules"]["pvt"]["controlMode"],
            json!({"automatic": false, "automaticMode": null})
        );
        cache.insert(
            topic,
            json!({"AutomaticMode": {"Aft": {"Mode": "idle"}, "Empty": {}}}),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(
            data["modules"]["pvt"]["controlMode"],
            json!({"automatic": true,
                   "automaticMode": {"aft": {"mode": "idle"}, "empty": {"Empty": null}}})
        );
    }

    fn simulation_view() -> SimulationView {
        serde_json::from_value(json!({
            "stateTypeName": "SimulationState",
            "statusTopic": "thrs/simulator/status",
            "statusKeys": {"status": "Status", "time": "SimulationTime"},
            "inputsTopic": "thrs/simulator/simulation-inputs",
            "outputsTopic": "thrs/simulator/simulation-outputs",
            "inputsSetTopic": "thrs/simulator/simulation-inputs/set",
            "inputsUnionType": "SimulationInputsType",
            "outputsUnionType": "SimulationOutputsType",
            "waitTimeoutS": 0.2,
            "directives": [
                {"gqlName": "simulationPlay", "topic": "thrs/simulator/play",
                         "argName": "playbackRate",
                         "payloadKey": "PlaybackRate", "default": 1.0,
                         "bounds": {"min": 0.25, "max": 10},
                         "allowedFrom": ["available", "running"], "expectStatus": "running",
                         "preconditionError": "Can only play an available or running simulation",
                         "missingError": "No simulation status available, cannot play"},
                {"gqlName": "simulationPause", "topic": "thrs/simulator/pause",
                          "allowedFrom": ["running"],
                          "expectStatus": "available",
                          "preconditionError": "Can only pause a running simulation",
                          "missingError": "No simulation status available, cannot pause"},
                {"gqlName": "simulationStep", "topic": "thrs/simulator/step",
                         "argName": "seconds",
                         "payloadKey": "Seconds", "argRequired": true,
                         "allowedFrom": ["available"], "expectStatus": "stepping",
                         "preconditionError": "Can only step an available simulation",
                         "missingError": "No simulation status available, cannot step"}
            ],
            "simulations": [
                {"name": "thrusters",
                 "inputs": {"typeName": "ThrustersSimulationInputsType", "fields": [
                     {"gqlField": "thrustersPcs", "key": "ThrustersPcs",
                      "typeName": "SimulationPcsType", "leaves": [
                         {"gql": "mode", "raw": "Mode", "type": "String", "enumType": "PcsMode",
                          "enumValues": {"0": "OFF", "1": "PROPULSION"}}]}]},
                 "outputs": {"typeName": "ThrustersSimulationOutputsType", "fields": [
                     {"gqlField": "thrustersPcmSupply", "key": "ThrustersPcmSupply",
                      "typeName": "SimulationFlowBoundaryType", "leaves": [
                         {"gql": "flow", "raw": "Flow", "type": "Float"}]}]},
                 "mutations": [{"gqlName": "thrustersSimulationSetThrustersPcs",
                     "kind": "simulation", "argName": "value", "payloadKey": "ThrustersPcs",
                     "inputTypeName": "PcsInputType",
                     "inputFields": [{"argName": "mode", "wireKey": "Mode", "type": "String",
                         "enumType": "PcsMode", "enumValues": {"0": "OFF", "1": "PROPULSION"}}],
                     "stateTopic": "thrs/simulator/simulation-inputs",
                     "setTopic": "thrs/simulator/simulation-inputs/set"}]},
                {"name": "pcm",
                 "inputs": {"typeName": "PcmSimulationInputsType", "fields": [
                     {"gqlField": "pcmPvtSupply", "key": "PcmPvtSupply",
                      "typeName": "SimulationBoundaryType", "leaves": [
                         {"gql": "flow", "raw": "Flow", "type": "Float"}]}]},
                 "outputs": {"typeName": "PcmSimulationOutputsType", "fields": [
                     {"gqlField": "pcmConsumersSupply", "key": "PcmConsumersSupply",
                      "typeName": "SimulationFlowBoundaryType", "leaves": [
                         {"gql": "flow", "raw": "Flow", "type": "Float"}]}]},
                 "mutations": []}
            ]
        }))
        .unwrap()
    }

    #[tokio::test]
    async fn test_simulation_query_status_union_and_directive_preconditions() {
        let cache = Arc::new(TopicCache::new());
        let sim = simulation_view();
        let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
        let publisher: Arc<dyn TopicPublisher> =
            Arc::new(CapturingPublisher { sent: sent.clone() });
        let schema = build_schema(
            cache.clone(),
            SchemaInputs {
                simulation: Some(&sim),
                publisher: Some(publisher),
                ..Default::default()
            },
        )
        .unwrap();
        let query = "{ simulation { status time inputs { __typename \
                     ... on ThrustersSimulationInputsType { thrustersPcs { mode { value } } } \
                     ... on PcmSimulationInputsType { pcmPvtSupply { flow { value } } } } \
                     outputs { __typename } } }";
        // No status retained -> `simulation` is null, like thrs-api.
        let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
        assert_eq!(data["simulation"], json!(null));
        cache.insert(
            "thrs/simulator/status",
            json!({"Mode": "thrusters", "Status": "available", "ControlModules": ["thrusters"],
                   "SimulationTime": "2026-01-02T03:04:05.678901Z"}),
        );
        // Inputs typed by which simulation's keys the object carries.
        cache.insert(
            "thrs/simulator/simulation-inputs",
            json!({"ThrustersPcs": {"Mode": {"Value": 1, "TimeStamp": "2026-01-01T00:00:00Z"}}}),
        );
        let response = schema.execute(query).await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(data["simulation"]["status"], json!("available"));
        assert_eq!(
            data["simulation"]["time"],
            json!("2026-01-02T03:04:05.678901+00:00")
        );
        assert_eq!(
            data["simulation"]["inputs"]["__typename"],
            json!("ThrustersSimulationInputsType")
        );
        assert_eq!(
            data["simulation"]["inputs"]["thrustersPcs"]["mode"]["value"],
            json!("PROPULSION")
        );
        assert_eq!(data["simulation"]["outputs"], json!(null));

        // Pause while available: thrs-api's exact precondition error, nothing published.
        let response = schema.execute("mutation { simulationPause }").await;
        assert_eq!(
            response.errors[0].message,
            "Can only pause a running simulation"
        );
        assert!(sent.lock().unwrap().is_empty());
        // Play out of bounds: rejected before publishing.
        let response = schema
            .execute("mutation { simulationPlay(playbackRate: 100) }")
            .await;
        assert!(!response.errors.is_empty());
        assert!(sent.lock().unwrap().is_empty());
        // Play in range: publishes `{"PlaybackRate": 2}` then times out waiting
        // for `running` (nothing flips the status here).
        let response = schema
            .execute("mutation { simulationPlay(playbackRate: 2) }")
            .await;
        assert_eq!(sent.lock().unwrap().len(), 1);
        let (topic, payload) = sent.lock().unwrap()[0].clone();
        assert_eq!(topic, "thrs/simulator/play");
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(&payload).unwrap(),
            json!({"PlaybackRate": 2.0})
        );
        assert!(response.errors[0]
            .message
            .starts_with("Timeout waiting for simulation status"));

        // Input mutation: restamps the component into the cached inputs object
        // and republishes it; returns the simulation's inputs type.
        let response = schema
            .execute(
                "mutation { thrustersSimulationSetThrustersPcs(value: {mode: OFF}) \
                 { thrustersPcs { mode { value } } } }",
            )
            .await;
        assert!(response.errors.is_empty(), "{:?}", response.errors);
        let data: serde_json::Value = response.data.into_json().unwrap();
        assert_eq!(
            data["thrustersSimulationSetThrustersPcs"]["thrustersPcs"]["mode"]["value"],
            json!("OFF")
        );
        let (topic, payload) = sent.lock().unwrap()[1].clone();
        assert_eq!(topic, "thrs/simulator/simulation-inputs/set");
        let published: serde_json::Value = serde_json::from_str(&payload).unwrap();
        assert_eq!(published["ThrustersPcs"]["Mode"]["Value"], json!(0));
    }
}
