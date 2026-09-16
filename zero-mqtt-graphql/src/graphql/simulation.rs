//! thrs-api's simulation surface: the `simulation { status time inputs
//! outputs }` query, the play/pause/step directives and the per-simulation
//! input mutations, served from the simulation spec (see
//! [`crate::simulation_view`]).

use super::*;

// --- Simulation (`simulation { status time inputs outputs }`, directives, input mutations) ---

/// Schema contributions of the simulation spec.
pub(super) struct SimulationSchemaParts {
    pub(super) query_field: Field,
    pub(super) types: Vec<Type>,
    pub(super) mutation_fields: Vec<Field>,
}

/// Build thrs-api's simulation surface over the cache: the `simulation` query
/// (the retained status object; null until a simulator has published one, like
/// thrs-api), the inputs/outputs unions typed by whichever simulation's fields
/// match the cached object, and - with a publisher - the play/pause/step
/// directives plus every `{sim}SimulationSet{Component}` input mutation (same
/// restamp-and-republish semantics as a `control` mutation, returning the
/// simulation's inputs type).
pub(super) fn register_simulation(
    sim: &SimulationView,
    cache: &Arc<TopicCache>,
    publisher: Option<Arc<dyn TopicPublisher>>,
) -> SimulationSchemaParts {
    let mut types: Vec<Type> = Vec::new();
    let mut inputs_union = Union::new(&sim.inputs_union_type);
    let mut outputs_union = Union::new(&sim.outputs_union_type);
    // (type name, by-alias keys) per simulation, to resolve the union member.
    let mut inputs_index: Vec<(String, BTreeSet<String>)> = Vec::new();
    let mut outputs_index: Vec<(String, BTreeSet<String>)> = Vec::new();
    let mut seen_types: BTreeSet<String> = BTreeSet::new();
    for s in &sim.simulations {
        for (io, union, index) in [
            (&s.inputs, &mut inputs_union, &mut inputs_index),
            (&s.outputs, &mut outputs_union, &mut outputs_index),
        ] {
            if seen_types.insert(io.type_name.clone()) {
                types.extend(
                    object_section_objects(&s.name, io)
                        .into_iter()
                        .map(Type::from),
                );
                *union =
                    std::mem::replace(union, Union::new("_")).possible_type(io.type_name.clone());
            }
            index.push((
                io.type_name.clone(),
                io.fields.iter().map(|f| f.key.clone()).collect(),
            ));
        }
    }
    types.push(inputs_union.into());
    types.push(outputs_union.into());

    // `SimulationState { status: String!, time: DateTime!, inputs, outputs }`,
    // resolved off the cached status object (thrs-api's `SimulationState`).
    let status_key = Name::new(&sim.status_keys.status);
    let time_key = Name::new(&sim.status_keys.time);
    let status_field = plain_field(&PlainFieldDef {
        gql_field: "status".into(),
        key: sim.status_keys.status.clone(),
        r#type: Some("String".into()),
        object: None,
        optional: false,
    });
    let time_field = Field::new("time", TypeRef::named_nn(DATETIME_SCALAR), {
        let time_key = time_key.clone();
        move |ctx| {
            let time_key = time_key.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let parent = ctx.parent_value.try_to_value()?;
                let value = match parent {
                    GraphQlValue::Object(map) => match map.get(&time_key) {
                        Some(GraphQlValue::String(t)) => {
                            GraphQlValue::String(normalize_timestamp(t))
                        }
                        Some(other) => other.clone(),
                        None => GraphQlValue::Null,
                    },
                    _ => GraphQlValue::Null,
                };
                Ok(Some(FieldValue::value(value)))
            })
        }
    });
    let state_obj = Object::new(&sim.state_type_name)
        .field(status_field)
        .field(time_field)
        .field(union_member_field(
            "inputs",
            &sim.inputs_union_type,
            &sim.inputs_topic,
            inputs_index,
            cache,
        ))
        .field(union_member_field(
            "outputs",
            &sim.outputs_union_type,
            &sim.outputs_topic,
            outputs_index,
            cache,
        ));
    types.push(state_obj.into());

    // `simulation`: the cached status object, or null when none is retained or
    // it carries no simulation time (thrs-api's `resolve simulation` guard).
    let status_topic = sim.status_topic.clone();
    let cache_q = cache.clone();
    let query_field = Field::new(
        "simulation",
        TypeRef::named(&sim.state_type_name),
        move |_ctx| {
            let status_topic = status_topic.clone();
            let cache = cache_q.clone();
            let status_key = status_key.clone();
            let time_key = time_key.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let value = cache_q_status(&cache, &status_topic, &status_key, &time_key);
                Ok(value.map(FieldValue::value))
            })
        },
    );

    let mut mutation_fields = Vec::new();
    if let Some(publisher) = publisher {
        let wait = std::time::Duration::from_secs_f64(sim.wait_timeout_s);
        for def in &sim.directives {
            mutation_fields.push(directive_field(
                def,
                &sim.status_topic,
                &sim.status_keys.status,
                wait,
                cache,
                publisher.clone(),
            ));
        }
        let mut seen: BTreeSet<String> = BTreeSet::new();
        for (s, def) in sim.mutations() {
            if !seen.insert(def.gql_name.clone()) {
                warn!(
                    "duplicate simulation mutation '{}' — skipping",
                    def.gql_name
                );
                continue;
            }
            types.push(control_input_type(def).into());
            mutation_fields.push(control_mutation_field(
                def,
                cache,
                publisher.clone(),
                Some(s.inputs.type_name.clone()),
            ));
        }
    }

    SimulationSchemaParts {
        query_field,
        types,
        mutation_fields,
    }
}

/// The cached simulation status object when it is usable (has a status and a
/// simulation time), converted for the resolvers.
pub(super) fn cache_q_status(
    cache: &TopicCache,
    topic: &str,
    status_key: &Name,
    time_key: &Name,
) -> Option<GraphQlValue> {
    let value = json_to_graphql_value(&cache.get(topic)?);
    let GraphQlValue::Object(map) = &value else {
        return None;
    };
    let has = |k: &Name| !matches!(map.get(k), None | Some(GraphQlValue::Null));
    (has(status_key) && has(time_key)).then_some(value)
}

/// The current simulation status string from the cache, if any.
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
/// simulation whose by-alias field keys equal the object's keys (pydantic's
/// union validation picks the model the payload fits), else the one whose keys
/// are the largest subset of the object's, else null.
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
            let Some(JsonValue::Object(map)) = cache.get(&topic) else {
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

/// One simulation directive (`simulationPlay(playbackRate: Float): Void` etc.):
/// checks the cached status against the directive's preconditions (thrs-api's
/// exact error strings), publishes the message, then waits up to the timeout
/// for the status to become the expected one (`DirectiveMessaging`).
pub(super) fn directive_field(
    def: &DirectiveDef,
    status_topic: &str,
    status_key: &str,
    wait: std::time::Duration,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
) -> Field {
    let name = def.gql_name.clone();
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
            let mut payload = serde_json::Map::new();
            if let (Some(arg_name), Some(payload_key)) = (&def.arg_name, &def.payload_key) {
                let given = ctx.args.get(arg_name).map(|v| v.f64()).transpose()?;
                let value = given.or(def.default);
                if let Some(v) = value {
                    if let Some(bounds) = &def.bounds {
                        check_bounds(bounds, v).map_err(async_graphql::Error::new)?;
                    }
                    payload.insert(payload_key.clone(), JsonValue::from(v));
                }
            }
            let status = cached_status(&cache, &status_topic, &status_key)
                .ok_or_else(|| async_graphql::Error::new(def.missing_error.clone()))?;
            if !def.allowed_from.iter().any(|s| *s == status) {
                return Err(async_graphql::Error::new(def.precondition_error.clone()));
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
                    return Err(async_graphql::Error::new(format!(
                        "Timeout waiting for simulation status '{}'",
                        def.expect_status
                    )));
                }
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
            }
            Ok(Some(FieldValue::NULL))
        })
    });
    if let Some(arg_name) = arg {
        // thrs-api: a required arg, or one with a default (`playbackRate: Float!
        // = 1`) is non-null; only an argument with neither is nullable.
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
