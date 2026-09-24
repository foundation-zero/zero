use std::time::SystemTime;

use super::*;

/// A `setComponent` input object, named as thrs-api names it (clients hard-code
/// names like `PumpInputType` as variable types).
pub(super) fn control_input_type(def: &MutationDef) -> InputObject {
    let mut input_obj = InputObject::new(def.input_type_name());
    for f in &def.input_fields {
        let base = match &f.enum_type {
            Some(name) => name.clone(),
            None => flat_scalar_name(&f.r#type),
        };
        let input = if f.required {
            InputValue::new(&f.gql, TypeRef::named_nn(base))
        } else {
            InputValue::new(&f.gql, TypeRef::named(base)).default_value(GraphQlValue::Null)
        };
        input_obj = input_obj.field(input);
    }
    input_obj
}

/// A mutation's return object, built by the read side's section builder;
/// `None` (returning Boolean) without a non-empty section.
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

/// One mutation field of any kind; a composite kind pushes its input type onto `types`.
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

/// The `Mutation` object (fields deduped by name) plus its supporting types.
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

/// The object type when available, else `Boolean!` as in thrs-api.
fn mutation_return_type(return_type: Option<&str>) -> TypeRef {
    match return_type {
        Some(name) => TypeRef::named_nn(name),
        None => TypeRef::named_nn(TypeRef::BOOLEAN),
    }
}

/// The raw cached object a mutation modifies (the flattened view would add keys
/// to the republish), or thrs-api's error when none is cached.
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

/// Publish the object, await any confirmation, and return the object or `boolean`.
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

/// What a confirmation waits for: the written value, or (a switch) any value.
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

/// Wait until the confirm topic meets the expectation, or time out.
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

/// JSON equality with `1` == `1.0`, so a republished object matches its echo.
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

/// A `setField` (validate and overwrite one key of the cached object) or
/// `setFlag` (publish a fresh `{key: value}`) mutation.
pub(super) fn mutation_field(
    def: &MutationDef,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
    return_type: Option<String>,
) -> Field {
    let def = def.clone();
    let cache = cache.clone();
    let arg_name = def.arg_name.clone();
    // A list arg is `[Float!]!`, as in thrs-api.
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
                        // GraphQL input coercion: a single value is a one-item list.
                        let items = match value.list() {
                            Ok(list) => list.iter().map(item).collect::<Result<Vec<_>, _>>()?,
                            Err(_) => vec![item(value)?],
                        };
                        JsonValue::Array(items)
                    }
                    _ => JsonValue::from(value.f64()?),
                };
                let mut map = cached_state(&cache, &def)?;
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

/// A `setComponent` mutation: restamp each input leaf with `now()` and republish
/// the cached object with the component replaced.
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
                    match input.get(&f.gql) {
                        Some(v) => {
                            let member = v.enum_name()?;
                            // `enumValues` maps wire value -> member name.
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
            // Validate before reading the cache, as thrs-api does.
            if let Some(model) = &def.model {
                component = model
                    .validate_model(component)
                    .map_err(async_graphql::Error::new)?;
            }

            let mut map = cached_state(&cache, &def)?;
            map.insert(def.key.clone(), JsonValue::Object(component));
            // Re-derive mirror fields from the components, as thrs-api does.
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

/// Now as a microsecond RFC 3339 UTC timestamp, as `Stamped` values carry it.
pub fn now_iso() -> String {
    humantime::format_rfc3339_micros(SystemTime::now()).to_string()
}
