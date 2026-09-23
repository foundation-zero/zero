//! The write-path: the declared mutations (`setField`, `setFlag`,
//! `setComponent`, see [`crate::mutations_view`]) served over the cache and a
//! [`TopicPublisher`]. Lifecycle member mutations reuse the same resolvers
//! (see `super::lifecycle`).

use std::time::SystemTime;

use super::*;

/// The composite input object for a `setComponent` mutation, named as the
/// producer's API names it (`PumpInputType`, shared across groups; clients may
/// hard-code those names as variable types). Required leaves are non-null; an
/// optional enum leaf is nullable and typed as the shared enum (see
/// `shared_types`).
pub(super) fn control_input_type(def: &MutationDef) -> InputObject {
    let mut input_obj = InputObject::new(def.input_type_name());
    for f in &def.input_fields {
        let base = match &f.enum_type {
            Some(name) => name.clone(),
            None => flat_scalar_name(&f.r#type),
        };
        // A nullable input field defaults to null like thrs-api's (the model
        // field's default, unstamped).
        let input = if f.required {
            InputValue::new(&f.gql, TypeRef::named_nn(base))
        } else {
            InputValue::new(&f.gql, TypeRef::named(base)).default_value(GraphQlValue::Null)
        };
        input_obj = input_obj.field(input);
    }
    input_obj
}

/// The object type a mutation returns, registered into `types` once per
/// type name: the member section's own type (the producer's whole
/// `Parameters` / `ControlValues` model), built by the same section builder
/// the read side uses so read and write share one definition. `None` when the
/// mutation names no section or the section has no fields (it then returns
/// Boolean).
pub(super) fn mutation_result_type(
    scope: &str,
    section: Option<&ObjectSectionDef>,
    registered: &mut BTreeSet<String>,
    types: &mut Vec<Type>,
) -> Option<String> {
    let section = section?;
    if section.fields.is_empty() {
        return None;
    }
    if registered.insert(section.type_name.clone()) {
        types.extend(
            object_section_objects(scope, section)
                .into_iter()
                .map(Type::from),
        );
    }
    Some(section.type_name.clone())
}

/// One mutation field of any kind, plus (for a composite kind) its input
/// type pushed onto `types`.
pub(super) fn mutation_field_of(
    def: &MutationDef,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
    return_type: Option<String>,
    types: &mut Vec<Type>,
) -> Field {
    match def.kind {
        MutationKind::SetComponent => {
            types.push(control_input_type(def).into());
            control_mutation_field(def, cache, publisher, return_type)
        }
        MutationKind::SetField | MutationKind::SetFlag => {
            mutation_field(def, cache, publisher, return_type)
        }
    }
}

/// Build the `Mutation` object (one field per mutation of every view member,
/// deduped by GraphQL name) plus every supporting type: return objects and
/// the composite input types. A GraphQL schema can't expose two mutations
/// with the same name.
pub(super) fn register_mutations(
    views: &[ViewDef],
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
) -> (Object, Vec<Type>) {
    let mut obj = Object::new("Mutation");
    let mut seen: BTreeSet<String> = BTreeSet::new();
    let mut types: Vec<Type> = Vec::new();
    let mut registered: BTreeSet<String> = BTreeSet::new();
    for view in views {
        for (member, def) in view.mutations() {
            if !seen.insert(def.gql.clone()) {
                warn!("duplicate mutation '{}' — skipping", def.gql);
                continue;
            }
            let return_type = mutation_result_type(
                &member.gql,
                def.returns
                    .as_deref()
                    .and_then(|r| member.object_section(r)),
                &mut registered,
                &mut types,
            );
            obj = obj.field(mutation_field_of(
                def,
                cache,
                publisher.clone(),
                return_type,
                &mut types,
            ));
        }
    }
    (obj, types)
}

/// The GraphQL type a mutation field returns: the object type when one is
/// available, else `Boolean!` like thrs-api's automation-mode mutation.
fn mutation_return_type(return_type: Option<&str>) -> TypeRef {
    match return_type {
        Some(name) => TypeRef::named_nn(name),
        None => TypeRef::named_nn(TypeRef::BOOLEAN),
    }
}

/// The cached object a mutation modifies (exactly as the controller published
/// it - the flattened field view would add spurious top-level keys to the
/// republish), or thrs-api's error when nothing is cached at its state topic.
fn cached_state(
    cache: &TopicCache,
    def: &MutationDef,
) -> async_graphql::Result<serde_json::Map<String, JsonValue>> {
    match cache.get_raw(&def.state_topic) {
        Some(JsonValue::Object(map)) => Ok(map),
        Some(_) => Err(async_graphql::Error::new(format!(
            "cached state at '{}' is not a JSON object",
            def.state_topic
        ))),
        None => Err(async_graphql::Error::new(format!(
            "{} (nothing cached at '{}')",
            def.missing_error.clone().unwrap_or_default(),
            def.state_topic
        ))),
    }
}

/// Publish the (modified) object to the mutation's set topic, await its
/// confirmation when the mutation declares one, and produce the field's
/// result: the object itself when the field returns an object type (its
/// fields are projected off it by the section objects), else the given
/// Boolean (`true` for a field mutation, the flag itself for a flag mutation).
async fn publish_result(
    publisher: &dyn TopicPublisher,
    cache: &TopicCache,
    def: &MutationDef,
    payload: JsonValue,
    returns_object: bool,
    boolean_result: bool,
) -> async_graphql::Result<Option<FieldValue<'static>>> {
    let expectation = def.confirm.as_ref().map(|confirm| {
        let key = confirm.key.as_deref().unwrap_or(&def.key);
        if confirm.presence {
            Expectation::Presence(boolean_result)
        } else {
            Expectation::Value(payload.get(key).cloned().unwrap_or(JsonValue::Null))
        }
    });
    let serialized =
        serde_json::to_string(&payload).map_err(|e| async_graphql::Error::new(e.to_string()))?;
    publisher
        .publish(def.set_topic.clone(), serialized)
        .await
        .map_err(|e| async_graphql::Error::new(e.to_string()))?;
    if let (Some(confirm), Some(expectation)) = (&def.confirm, expectation) {
        let key = confirm.key.as_deref().unwrap_or(&def.key);
        await_confirmation(cache, confirm, key, &expectation).await?;
    }
    Ok(Some(if returns_object {
        FieldValue::value(json_to_graphql_value(&payload))
    } else {
        FieldValue::value(boolean_result)
    }))
}

/// What a confirmation waits for under the confirm key: the written value
/// itself, or (a switch) whether the key holds a value at all.
enum Expectation {
    Value(JsonValue),
    Presence(bool),
}

impl Expectation {
    fn met_by(&self, cached: Option<&JsonValue>) -> bool {
        match self {
            Expectation::Value(expected) => cached.is_some_and(|v| json_equivalent(v, expected)),
            Expectation::Presence(present) => cached.is_some_and(|v| !v.is_null()) == *present,
        }
    }
}

/// Wait until the object cached at the confirm topic meets the expectation
/// under `key`, or fail with the confirm's timeout error.
async fn await_confirmation(
    cache: &TopicCache,
    confirm: &ConfirmDef,
    key: &str,
    expectation: &Expectation,
) -> async_graphql::Result<()> {
    let deadline =
        tokio::time::Instant::now() + std::time::Duration::from_secs_f64(confirm.timeout_s);
    loop {
        let cached = cache.get_raw(&confirm.topic);
        if expectation.met_by(cached.as_ref().and_then(|v| v.get(key))) {
            return Ok(());
        }
        if tokio::time::Instant::now() >= deadline {
            return Err(async_graphql::Error::new(confirm.timeout_error.clone()));
        }
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
    }
}

/// JSON equality with numbers compared by value (`1` and `1.0` are the same
/// on the wire) so a republished object matches its echo.
fn json_equivalent(a: &JsonValue, b: &JsonValue) -> bool {
    match (a, b) {
        (JsonValue::Number(x), JsonValue::Number(y)) => x.as_f64() == y.as_f64(),
        (JsonValue::Array(x), JsonValue::Array(y)) => {
            x.len() == y.len() && x.iter().zip(y).all(|(p, q)| json_equivalent(p, q))
        }
        (JsonValue::Object(x), JsonValue::Object(y)) => {
            x.len() == y.len()
                && x.iter()
                    .all(|(k, v)| y.get(k).is_some_and(|w| json_equivalent(v, w)))
        }
        _ => a == b,
    }
}

/// One mutation field of two kinds:
/// * `setField` — `{name}(value: <scalar>): <Object>`: reads the whole object
///   from `state_topic`, overwrites `key` with the
///   value validated as the producer validates it (the field, then the
///   object's rules), and republishes it to `set_topic`.
/// * `setFlag` — `{name}(<arg>: Boolean): Boolean`: publishes a fresh
///   `{key: true_value|false_value}` object to `set_topic`.
pub(super) fn mutation_field(
    def: &MutationDef,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
    return_type: Option<String>,
) -> Field {
    let def = def.clone();
    let cache = cache.clone();
    let arg_name = def.arg_name.clone();
    // A list arg (`[Float!]`, a PID tuning tuple) is a non-null list of
    // non-null scalars like thrs-api's `[Float!]!`.
    let arg_type_ref = match def.arg_type.strip_prefix('[') {
        Some(inner) => TypeRef::NonNull(Box::new(TypeRef::named_nn_list(flat_scalar_name(
            inner.trim_end_matches(['!', ']']),
        )))),
        None => TypeRef::named_nn(flat_scalar_name(&def.arg_type)),
    };
    let returns_object = return_type.is_some();
    let field_type = mutation_return_type(return_type.as_deref());
    Field::new(def.gql.clone(), field_type, move |ctx| {
        let cache = cache.clone();
        let publisher = publisher.clone();
        let def = def.clone();
        FieldFuture::new(async move {
            // The Boolean result: a flag mutation returns the flag it was
            // given; a field mutation without an object type returns true.
            let mut boolean_result = true;
            let payload = if def.kind == MutationKind::SetFlag {
                let on = ctx.args.try_get(&def.arg_name)?.boolean()?;
                boolean_result = on;
                let mode = if on {
                    def.true_value.clone().unwrap_or_default()
                } else {
                    def.false_value.clone().unwrap_or_default()
                };
                let mut map = serde_json::Map::new();
                map.insert(def.key.clone(), JsonValue::from(mode));
                JsonValue::Object(map)
            } else {
                let value = ctx.args.try_get(&def.arg_name)?;
                let new_value: JsonValue = match def.arg_type.as_str() {
                    "Int" => JsonValue::from(value.i64()?),
                    "Boolean" => JsonValue::from(value.boolean()?),
                    t if t.starts_with('[') => {
                        let inner = t.trim_start_matches('[').trim_end_matches(['!', ']']);
                        let item = |v: async_graphql::dynamic::ValueAccessor<'_>| match inner {
                            "Int" => v.i64().map(JsonValue::from),
                            "Boolean" => v.boolean().map(JsonValue::from),
                            _ => v.f64().map(JsonValue::from),
                        };
                        // A single value where a list is expected is a one-item
                        // list (GraphQL input coercion).
                        let items = match value.list() {
                            Ok(list) => list.iter().map(item).collect::<Result<Vec<_>, _>>()?,
                            Err(_) => vec![item(value)?],
                        };
                        JsonValue::Array(items)
                    }
                    _ => JsonValue::from(value.f64()?),
                };
                let mut map = cached_state(&cache, &def)?;
                // The producer validates the assignment (the field, then the
                // object's rules) before publishing anything.
                let new_value = match &def.model {
                    Some(model) => model
                        .validate_assignment(&map, &def.key, new_value)
                        .map_err(async_graphql::Error::new)?,
                    None => new_value,
                };
                map.insert(def.key.clone(), new_value);
                JsonValue::Object(map)
            };
            publish_result(
                publisher.as_ref(),
                &cache,
                &def,
                payload,
                returns_object,
                boolean_result,
            )
            .await
        })
    })
    .argument(InputValue::new(arg_name, arg_type_ref))
}

/// One `setComponent` mutation: `{name}(<arg>: <ComponentInput>): <Object>`.
/// Restamps each input leaf with `now()` into `{WireKey: {Value, TimeStamp}}`,
/// sets the whole component into the cached state object, and republishes it
/// to `set_topic`. Returns the modified object (or Boolean when no return type
/// is available).
pub(super) fn control_mutation_field(
    def: &MutationDef,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
    return_type: Option<String>,
) -> Field {
    let input_type = def.input_type_name().to_string();
    let arg_name = def.arg_name.clone();
    let def = def.clone();
    let cache = cache.clone();
    let returns_object = return_type.is_some();
    let field_type = mutation_return_type(return_type.as_deref());
    Field::new(def.gql.clone(), field_type, move |ctx| {
        let cache = cache.clone();
        let publisher = publisher.clone();
        let def = def.clone();
        FieldFuture::new(async move {
            let input = ctx.args.try_get(&def.arg_name)?.object()?;
            let now = now_iso();
            let mut component = serde_json::Map::new();
            for f in &def.input_fields {
                let wire: Option<JsonValue> = if let Some(values) = &f.enum_values {
                    // Optional enum leaf: absent -> null (the model's default).
                    match input.get(&f.gql) {
                        Some(v) => {
                            let member = v.enum_name()?;
                            // Map the member name back to its wire value; the
                            // enumValues map is wire-value(str) -> member-name.
                            let wire_val = values
                                .iter()
                                .find(|(_, name)| name.as_str() == member)
                                .map(|(k, _)| k.clone())
                                .ok_or_else(|| {
                                    async_graphql::Error::new(format!(
                                        "unknown enum member '{member}' for '{}'",
                                        f.gql
                                    ))
                                })?;
                            // Wire stores the value; a numeric enum value goes as
                            // a number, anything else as a string.
                            Some(match wire_val.parse::<i64>() {
                                Ok(n) => JsonValue::from(n),
                                Err(_) => JsonValue::from(wire_val),
                            })
                        }
                        None => Some(JsonValue::Null),
                    }
                } else {
                    let v = input.try_get(&f.gql)?;
                    Some(match f.r#type.as_str() {
                        "Int" => JsonValue::from(v.i64()?),
                        "Boolean" => JsonValue::from(v.boolean()?),
                        _ => JsonValue::from(v.f64()?),
                    })
                };
                component.insert(
                    f.key.clone(),
                    serde_json::json!({ "Value": wire, "TimeStamp": now }),
                );
            }
            // The producer builds (and so validates) the component before it
            // looks at the cached object.
            if let Some(model) = &def.model {
                component = model
                    .validate_model(component)
                    .map_err(async_graphql::Error::new)?;
            }

            let mut map = cached_state(&cache, &def)?;
            map.insert(def.key.clone(), JsonValue::Object(component));
            // Re-derive the object's mirror fields from the (possibly just
            // replaced) components, as thrs-api's model does on serialization.
            for derived in &def.derived {
                let mut mirrored = serde_json::Map::new();
                for (leaf, origin) in &derived.leaves {
                    let value = match origin {
                        DerivedLeaf::Source { component, leaf } => map
                            .get(component)
                            .and_then(|c| c.get(leaf))
                            .cloned()
                            .unwrap_or(JsonValue::Null),
                        DerivedLeaf::Constant { constant } => constant.clone(),
                    };
                    mirrored.insert(leaf.clone(), value);
                }
                map.insert(derived.key.clone(), JsonValue::Object(mirrored));
            }
            publish_result(
                publisher.as_ref(),
                &cache,
                &def,
                JsonValue::Object(map),
                returns_object,
                true,
            )
            .await
        })
    })
    .argument(InputValue::new(arg_name, TypeRef::named_nn(input_type)))
}

/// The current instant as an RFC 3339 UTC timestamp with microseconds
/// (`2026-01-02T03:04:05.678901Z`), the form a `Stamped` value carries on
/// the wire.
pub fn now_iso() -> String {
    humantime::format_rfc3339_micros(SystemTime::now()).to_string()
}
