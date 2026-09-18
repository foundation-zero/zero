//! The write-path: thrs-api's module mutations (`parameter`, `automationMode`,
//! `control`) served over the cache and a [`TopicPublisher`]. The simulation's
//! input mutations reuse [`control_mutation_field`] (see `super::simulation`).

use super::*;

/// The composite input object for a `control`/`simulation` mutation, named as
/// thrs-api names it (`PumpInputType`, shared across modules; zero-ui hard-codes
/// those names as variable types). Scalar leaves (`dutypoint`/`setpoint`/`on`)
/// are required; an enum leaf (`controlMode`, which the model makes optional) is
/// nullable and typed as the shared thrs-api enum (see `shared_types`).
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
            InputValue::new(&f.arg_name, TypeRef::named_nn(base))
        } else {
            InputValue::new(&f.arg_name, TypeRef::named(base)).default_value(GraphQlValue::Null)
        };
        input_obj = input_obj.field(input);
    }
    input_obj
}

/// The object type a `parameter`/`control` mutation returns, registered into
/// `types`: the read section's own type (thrs-api returns the whole `Parameters`
/// / `ControlValues` model, `ThrustersParametersType`), built by the same
/// section builder so read and write share one definition. `None` when no
/// mutation of that kind exists or the object has no fields (the mutation then
/// returns Boolean).
fn mutation_result_type(
    module: &str,
    section: &ObjectSectionDef,
    wanted: bool,
    types: &mut Vec<Type>,
) -> Option<String> {
    if !wanted || section.fields.is_empty() {
        return None;
    }
    types.extend(
        object_section_objects(module, section)
            .into_iter()
            .map(Type::from),
    );
    Some(section.type_name.clone())
}

/// Build the `Mutation` object (one field per declared mutation, deduped by
/// GraphQL name) plus every supporting type: parameter/control return objects
/// and the control mutations' composite input types. thrs-api can't expose two
/// mutations with the same name either.
pub(super) fn register_mutations(
    mutations: &[ModuleMutations],
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
) -> (Object, Vec<Type>) {
    let mut obj = Object::new("Mutation");
    let mut seen: BTreeSet<String> = BTreeSet::new();
    let mut types: Vec<Type> = Vec::new();
    for module in mutations {
        let has_kind = |kind: &str| module.mutations.iter().any(|m| m.kind == kind);
        let param_result = mutation_result_type(
            &module.module,
            &module.parameters_object,
            has_kind("parameter"),
            &mut types,
        );
        let control_result = mutation_result_type(
            &module.module,
            &module.control_values_object,
            has_kind("control"),
            &mut types,
        );

        for def in &module.mutations {
            if !seen.insert(def.gql_name.clone()) {
                warn!("duplicate mutation '{}' — skipping", def.gql_name);
                continue;
            }
            let field = match def.kind.as_str() {
                "control" => {
                    types.push(control_input_type(def).into());
                    control_mutation_field(def, cache, publisher.clone(), control_result.clone())
                }
                "parameter" => mutation_field(def, cache, publisher.clone(), param_result.clone()),
                _ => mutation_field(def, cache, publisher.clone(), None),
            };
            obj = obj.field(field);
        }
    }
    (obj, types)
}

/// Reject a numeric mutation value that violates the parameter's single-field
/// bounds, matching thrs-api's `validate_assignment` (see [`Bounds`]). Only the
/// per-field bounds; cross-field invariants are enforced by the control loop.
pub(super) fn check_bounds(bounds: &Bounds, v: f64) -> Result<(), String> {
    if let Some(min) = bounds.min {
        if v < min {
            return Err(format!("value {v} is below the minimum {min}"));
        }
    }
    if let Some(max) = bounds.max {
        if v > max {
            return Err(format!("value {v} is above the maximum {max}"));
        }
    }
    if let Some(x) = bounds.exclusive_min {
        if v <= x {
            return Err(format!("value {v} must be greater than {x}"));
        }
    }
    if let Some(x) = bounds.exclusive_max {
        if v >= x {
            return Err(format!("value {v} must be less than {x}"));
        }
    }
    Ok(())
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

/// Publish the (modified) object to the mutation's set topic and produce the
/// field's result: the object itself when the field returns an object type
/// (its fields are projected off it by the section objects), else the given
/// Boolean (thrs-api returns `true` for a parameter/control mutation without
/// an object type, and the `automatic` argument itself for automation mode).
async fn publish_result(
    publisher: &dyn TopicPublisher,
    def: &MutationDef,
    payload: JsonValue,
    returns_object: bool,
    boolean_result: bool,
) -> async_graphql::Result<Option<FieldValue<'static>>> {
    let serialized =
        serde_json::to_string(&payload).map_err(|e| async_graphql::Error::new(e.to_string()))?;
    publisher
        .publish(def.set_topic.clone(), serialized)
        .await
        .map_err(|e| async_graphql::Error::new(e.to_string()))?;
    Ok(Some(if returns_object {
        FieldValue::value(json_to_graphql_value(&payload))
    } else {
        FieldValue::value(boolean_result)
    }))
}

/// One mutation field of two kinds:
/// * `parameter` — `{name}(value: <scalar>): <Parameters>`: reads the whole
///   parameters object from `state_topic`, overwrites `payload_key` with the
///   (bounds-checked) value, and republishes the modified object to `set_topic`
///   (thrs-api's read-modify-republish, minus the controller round-trip wait;
///   see `ControlApiChannels.send_parameters`).
/// * `automationMode` — `{name}(automatic: Boolean): Boolean`: publishes a fresh
///   `{payload_key: true_value|false_value}` object to `set_topic` (thrs-api's
///   `ControlMessaging.set_automation_mode`).
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
    Field::new(def.gql_name.clone(), field_type, move |ctx| {
        let cache = cache.clone();
        let publisher = publisher.clone();
        let def = def.clone();
        FieldFuture::new(async move {
            // thrs-api's Boolean result: `set_automation_mode` returns the
            // `automatic` it was given; a parameter mutation without an object
            // type returns true.
            let mut boolean_result = true;
            let payload = if def.kind == "automationMode" {
                let on = ctx.args.try_get(&def.arg_name)?.boolean()?;
                boolean_result = on;
                let mode = if on {
                    def.true_value.clone().unwrap_or_else(|| "automatic".into())
                } else {
                    def.false_value.clone().unwrap_or_else(|| "manual".into())
                };
                let mut map = serde_json::Map::new();
                map.insert(def.payload_key.clone(), JsonValue::from(mode));
                JsonValue::Object(map)
            } else {
                let value = ctx.args.try_get(&def.arg_name)?;
                let new_value: JsonValue = match def.arg_type.as_str() {
                    "Int" => JsonValue::from(value.i64()?),
                    "Boolean" => JsonValue::from(value.boolean()?),
                    t if t.starts_with('[') => {
                        let inner = t.trim_start_matches('[').trim_end_matches(['!', ']']);
                        let items = value
                            .list()?
                            .iter()
                            .map(|v| match inner {
                                "Int" => v.i64().map(JsonValue::from),
                                "Boolean" => v.boolean().map(JsonValue::from),
                                _ => v.f64().map(JsonValue::from),
                            })
                            .collect::<Result<Vec<_>, _>>()?;
                        JsonValue::Array(items)
                    }
                    _ => {
                        let v = value.f64()?;
                        if let Some(bounds) = &def.bounds {
                            check_bounds(bounds, v).map_err(async_graphql::Error::new)?;
                        }
                        JsonValue::from(v)
                    }
                };
                let mut map = cached_state(&cache, &def)?;
                map.insert(def.payload_key.clone(), new_value);
                JsonValue::Object(map)
            };
            publish_result(
                publisher.as_ref(),
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

/// One `control` (manual-values) or `simulation` (inputs) mutation:
/// `{name}(value: <ComponentInput>): <ControlValues>`. Restamps each input leaf
/// with `now()` into `{WireKey: {Value, TimeStamp}}`, sets the whole component
/// into the cached state object, and republishes it to `set_topic` (thrs-api's
/// `ControlMessaging.set_manual_control` / `set_simulation_input`). Returns the
/// modified object (or Boolean when no return type is available).
pub(super) fn control_mutation_field(
    def: &MutationDef,
    cache: &Arc<TopicCache>,
    publisher: Arc<dyn TopicPublisher>,
    return_type: Option<String>,
) -> Field {
    let input_type = def.input_type_name().to_string();
    let def = def.clone();
    let cache = cache.clone();
    let returns_object = return_type.is_some();
    let field_type = mutation_return_type(return_type.as_deref());
    Field::new(def.gql_name.clone(), field_type, move |ctx| {
        let cache = cache.clone();
        let publisher = publisher.clone();
        let def = def.clone();
        FieldFuture::new(async move {
            let input = ctx.args.try_get("value")?.object()?;
            let now = crate::recompute::now_iso();
            let mut component = serde_json::Map::new();
            for f in &def.input_fields {
                let wire: Option<JsonValue> = if let Some(values) = &f.enum_values {
                    // Optional enum leaf: absent -> null (the model's default).
                    match input.get(&f.arg_name) {
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
                                        f.arg_name
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
                    let v = input.try_get(&f.arg_name)?;
                    Some(match f.r#type.as_str() {
                        "Int" => JsonValue::from(v.i64()?),
                        "Boolean" => JsonValue::from(v.boolean()?),
                        _ => JsonValue::from(v.f64()?),
                    })
                };
                component.insert(
                    f.wire_key.clone(),
                    serde_json::json!({ "Value": wire, "TimeStamp": now }),
                );
            }

            let mut map = cached_state(&cache, &def)?;
            map.insert(def.payload_key.clone(), JsonValue::Object(component));
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
                &def,
                JsonValue::Object(map),
                returns_object,
                true,
            )
            .await
        })
    })
    .argument(InputValue::new("value", TypeRef::named_nn(input_type)))
}
