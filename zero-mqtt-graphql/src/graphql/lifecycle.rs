//! Lifecycles: a status query, whole-object relays typed by a union, the
//! directives that transition the status and the member mutations, served
//! from a declared lifecycle (see [`crate::lifecycle_view`]).

use super::*;

use crate::lifecycle_view::StatusFieldDef;

/// graphql-core's message for an error that has none.
const UNKNOWN_ERROR: &str = "An unknown error occurred.";

// --- Lifecycle (`<queryField> { <status fields> <objects> }`, directives, member mutations) ---

/// Schema contributions of one lifecycle.
pub(super) struct LifecycleSchemaParts {
    pub(super) gql: Field,
    pub(super) types: Vec<Type>,
    pub(super) mutation_fields: Vec<Field>,
}

/// Build one lifecycle over the cache: the status query (the retained status
/// object; null until one has been published), the relayed objects typed by
/// whichever member object matches the cached payload, and - with a publisher
/// - the directives plus every member mutation.
pub(super) fn register_lifecycle(
    def: &LifecycleDef,
    cache: &Arc<TopicCache>,
    publisher: Option<Arc<dyn TopicPublisher>>,
) -> LifecycleSchemaParts {
    let mut types: Vec<Type> = Vec::new();
    let mut registered: BTreeSet<String> = BTreeSet::new();
    let mut state_obj = Object::new(&def.state_type_name);

    for field in &def.status.fields {
        state_obj = state_obj.field(status_field(field));
    }

    for object in &def.objects {
        let mut union = Union::new(&object.union_type);
        // (type name, by-alias keys) per member, to resolve the union member.
        let mut index: Vec<(String, BTreeSet<String>)> = Vec::new();
        for member in &def.members {
            let Some(io) = member.section(&object.member_section) else {
                continue;
            };
            if registered.insert(io.type_name.clone()) {
                types.extend(
                    object_section_objects(&member.name, io)
                        .into_iter()
                        .map(Type::from),
                );
            }
            if !index.iter().any(|(t, _)| *t == io.type_name) {
                union = union.possible_type(io.type_name.clone());
            }
            index.push((
                io.type_name.clone(),
                io.fields.iter().map(|f| f.key.clone()).collect(),
            ));
        }
        types.push(union.into());
        state_obj = state_obj.field(union_member_field(
            &object.gql,
            &object.union_type,
            &object.topic,
            index,
            cache,
        ));
    }
    types.push(state_obj.into());

    // The query field: the cached status object, or null when none is
    // retained or it lacks one of the status fields.
    let status_topic = def.status.topic.clone();
    let status_keys: Arc<Vec<Name>> = Arc::new(
        def.status
            .fields
            .iter()
            .map(|f| Name::new(&f.key))
            .collect(),
    );
    let cache_q = cache.clone();
    let gql = Field::new(
        def.gql.clone(),
        TypeRef::named(&def.state_type_name),
        move |_ctx| {
            let status_topic = status_topic.clone();
            let cache = cache_q.clone();
            let status_keys = status_keys.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let value = cache_q_status(&cache, &status_topic, &status_keys);
                Ok(value.map(FieldValue::value))
            })
        },
    );

    let mut mutation_fields = Vec::new();
    if let Some(publisher) = publisher {
        let wait = std::time::Duration::from_secs_f64(def.wait_timeout_s);
        for directive in &def.directives {
            mutation_fields.push(directive_field(
                directive,
                &def.status.topic,
                &def.status.key,
                wait,
                cache,
                publisher.clone(),
            ));
        }
        let mut seen: BTreeSet<String> = BTreeSet::new();
        for (member, mutation) in def.mutations() {
            if !seen.insert(mutation.gql.clone()) {
                warn!("duplicate lifecycle mutation '{}' — skipping", mutation.gql);
                continue;
            }
            let return_type = mutation_result_type(
                &member.name,
                mutation.returns.as_deref().and_then(|r| member.section(r)),
                &mut registered,
                &mut types,
            );
            mutation_fields.push(mutation_field_of(
                mutation,
                cache,
                publisher.clone(),
                return_type,
                &mut types,
            ));
        }
    }

    LifecycleSchemaParts {
        gql,
        types,
        mutation_fields,
    }
}

/// One field of the status object: a `DateTime` field serves the cached
/// timestamp as-is (RFC 3339); any other scalar reads its key straight off
/// the object.
fn status_field(def: &StatusFieldDef) -> Field {
    if def.r#type != "DateTime" {
        return plain_field(&PlainFieldDef {
            gql: def.gql.clone(),
            key: def.key.clone(),
            r#type: Some(def.r#type.clone()),
            object: None,
            optional: false,
        });
    }
    let time_key = Name::new(&def.key);
    Field::new(
        def.gql.clone(),
        TypeRef::named_nn(DATETIME_SCALAR),
        move |ctx| {
            let time_key = time_key.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let parent = ctx.parent_value.try_to_value()?;
                let value = match parent {
                    GraphQlValue::Object(map) => {
                        map.get(&time_key).cloned().unwrap_or(GraphQlValue::Null)
                    }
                    _ => GraphQlValue::Null,
                };
                Ok(Some(FieldValue::value(value)))
            })
        },
    )
}

/// The cached status object when it is usable (carries every status field),
/// converted for the resolvers.
pub(super) fn cache_q_status(
    cache: &TopicCache,
    topic: &str,
    keys: &[Name],
) -> Option<GraphQlValue> {
    let value = json_to_graphql_value(&cache.get(topic)?);
    let GraphQlValue::Object(map) = &value else {
        return None;
    };
    let has = |k: &Name| !matches!(map.get(k), None | Some(GraphQlValue::Null));
    keys.iter().all(has).then_some(value)
}

/// The current status string from the cache, if any.
pub(super) fn cached_status(cache: &TopicCache, topic: &str, status_key: &str) -> Option<String> {
    match cache.get(topic)? {
        JsonValue::Object(map) => map
            .get(status_key)
            .and_then(|v| v.as_str())
            .map(str::to_string),
        _ => None,
    }
}

/// A field resolving a whole cached object to one member of a union: the
/// member whose by-alias field keys equal the object's keys (a pydantic
/// union picks the model the payload fits), else the one whose keys are the
/// largest subset of the object's, else null.
pub(super) fn union_member_field(
    name: &str,
    union_type: &str,
    topic: &str,
    index: Vec<(String, BTreeSet<String>)>,
    cache: &Arc<TopicCache>,
) -> Field {
    let topic = topic.to_string();
    let cache = cache.clone();
    let index = Arc::new(index);
    Field::new(name, TypeRef::named(union_type), move |_ctx| {
        let topic = topic.clone();
        let cache = cache.clone();
        let index = index.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            // The object as published: the flattened field view would carry
            // the components' leaf keys too and never match a member exactly.
            let Some(JsonValue::Object(map)) = cache.get_raw(&topic) else {
                return Ok(None);
            };
            let keys: BTreeSet<String> = map.keys().cloned().collect();
            let type_name = index
                .iter()
                .find(|(_, k)| *k == keys)
                .or_else(|| {
                    index
                        .iter()
                        .filter(|(_, k)| k.is_subset(&keys))
                        .max_by_key(|(_, k)| k.len())
                })
                .map(|(t, _)| t.clone());
            Ok(type_name.map(|t| {
                FieldValue::value(json_to_graphql_value(&JsonValue::Object(map))).with_type(t)
            }))
        })
    })
}

/// One directive (`simulationPlay(playbackRate: Float): Void` etc.): checks
/// the cached status against the directive's preconditions (the producer's
/// exact error strings), publishes the message, then waits up to the timeout
/// for the status to become the expected one.
pub(super) fn directive_field(
    def: &DirectiveDef,
    status_topic: &str,
    status_key: &str,
    wait: std::time::Duration,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
) -> Field {
    let name = def.gql.clone();
    let def = def.clone();
    let status_topic = status_topic.to_string();
    let status_key = status_key.to_string();
    let cache = cache.clone();
    let arg = def.arg_name.clone();
    let required = def.arg_required;
    let default = def.default;
    let mut field = Field::new(name, TypeRef::named(VOID_SCALAR), move |ctx| {
        let def = def.clone();
        let status_topic = status_topic.clone();
        let status_key = status_key.clone();
        let cache = cache.clone();
        let publisher = publisher.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            // An argument that is absent (or null: a variable the client did
            // not send) takes its default, as graphql-core passes it.
            let given = match def.arg_name.as_ref().and_then(|name| ctx.args.get(name)) {
                Some(v) if !v.is_null() => Some(v.f64()?),
                _ => None,
            };
            let status = cached_status(&cache, &status_topic, &status_key)
                .ok_or_else(|| async_graphql::Error::new(def.missing_error.clone()))?;
            if !def.allowed_from.contains(&status) {
                return Err(async_graphql::Error::new(def.precondition_error.clone()));
            }
            // The producer builds (and so validates) the message only when it
            // sends it, after the status checks.
            let mut payload = serde_json::Map::new();
            if let (Some(key), Some(v)) = (&def.key, given.or(def.default)) {
                payload.insert(key.clone(), JsonValue::from(v));
            }
            if let Some(model) = &def.model {
                payload = model
                    .validate_model(payload)
                    .map_err(async_graphql::Error::new)?;
            }
            let serialized = serde_json::to_string(&JsonValue::Object(payload))
                .map_err(|e| async_graphql::Error::new(e.to_string()))?;
            publisher
                .publish(def.topic.clone(), serialized)
                .await
                .map_err(|e| async_graphql::Error::new(e.to_string()))?;
            let deadline = tokio::time::Instant::now() + wait;
            loop {
                if cached_status(&cache, &status_topic, &status_key).as_deref()
                    == Some(def.expect_status.as_str())
                {
                    break;
                }
                if tokio::time::Instant::now() >= deadline {
                    // The producer's wait raises a bare `TimeoutError`, which
                    // its GraphQL layer reports with its message-less default.
                    return Err(async_graphql::Error::new(UNKNOWN_ERROR));
                }
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
            }
            Ok(Some(FieldValue::NULL))
        })
    });
    if let Some(arg_name) = arg {
        // A required arg, or one with a default (`playbackRate: Float! = 1`)
        // is non-null; only an argument with neither is nullable.
        let mut input = if required || default.is_some() {
            InputValue::new(arg_name, TypeRef::named_nn(TypeRef::FLOAT))
        } else {
            InputValue::new(arg_name, TypeRef::named(TypeRef::FLOAT))
        };
        if let Some(d) = default {
            // Strawberry prints an integral float default as `1`, not `1.0`.
            let default = if d.fract() == 0.0 && d.abs() < 1e15 {
                GraphQlValue::from(d as i64)
            } else {
                GraphQlValue::from(d)
            };
            input = input.default_value(default);
        }
        field = field.argument(input);
    }
    field
}
