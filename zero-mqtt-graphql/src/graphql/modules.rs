//! The nested per-module read view: `modules { <module> { sensorValues
//! controlValues parameters controllerState controlMode } }`, thrs-api's shape
//! served over the cache from the module-view specs (see
//! [`crate::modules_view`]).

use super::*;

// --- Nested per-module view (`modules { <module> { sensorValues { … } } }`) ---

/// The query field plus every type it needs.
pub(super) struct ModulesSchemaParts {
    pub(super) query_field: Field,
    pub(super) objects: Vec<Object>,
}

/// A sensor field a module serves, with whether it is recomputed from raw
/// inputs (see [`crate::recompute`]) rather than relayed from its own topic.
pub(super) struct ServedSensorField<'a> {
    pub(super) field: &'a ModuleFieldDef,
    pub(super) recompute: bool,
}

/// The sensor fields a module serves, in spec order. Drops the `input_only`
/// collision shadows (a raw sensor thrs-api serves no query field for - it
/// stays in the view only as a recompute input) and, belt-and-suspenders, any
/// later duplicate of a camelCase name (async-graphql panics on a duplicate
/// field, which would take every module down). A computed field is recomputed
/// when `COMPUTED_MODE` is recompute and its formula is ported; otherwise it
/// relays its own topic like any sensor field.
pub(super) fn served_sensor_fields(
    view: &ModuleView,
    computed_mode: ComputedMode,
) -> Vec<ServedSensorField<'_>> {
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    view.sensor_values
        .iter()
        .filter(|f| !f.input_only)
        .filter(|f| {
            let first = seen.insert(f.gql_field.as_str());
            if !first {
                warn!(
                    "module '{}': duplicate sensorValues field '{}' (snake->camel \
                     collision); keeping first, skipping topic '{}'",
                    view.module, f.gql_field, f.topic
                );
            }
            first
        })
        .map(|field| ServedSensorField {
            field,
            recompute: computed_mode == ComputedMode::Recompute
                && field.computed
                && crate::recompute::is_recomputable(&view.module, &field.gql_field),
        })
        .collect()
}

/// Build the `modules { … }` query from the loaded specs, or `None` if there
/// are none (or something already claimed the `modules` field).
///
/// Container levels resolve to a constant non-null object so their children
/// run; each leaf resolver reads its own topic from the cache and projects the
/// `{Value, TimeStamp}` leaves through the `Stamped<Inner>` wrappers. Every
/// type carries thrs-api's own name, so the two schemas match by name.
pub(super) fn register_modules_query(
    module_views: &[ModuleView],
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
    computed_mode: ComputedMode,
) -> Option<ModulesSchemaParts> {
    let modules_type = &module_views.first()?.modules_type_name;
    if !used_query_fields.insert("modules".to_string()) {
        warn!("'modules' query field already claimed — skipping nested module view");
        return None;
    }

    let mut objects: Vec<Object> = Vec::new();
    let mut modules_obj = Object::new(modules_type.as_str());
    // Component/section types named after the pydantic class are shared across
    // modules (`ControlPumpType`); register each once.
    let mut seen_types: BTreeSet<String> = BTreeSet::new();

    for view in module_views {
        modules_obj = modules_obj.field(constant_object_field(&view.module, &view.type_name));
        let served = served_sensor_fields(view, computed_mode);

        // The module object carries every read section the UI queries:
        // `sensorValues` (constant container, one topic per field) plus the
        // whole-object sections when the spec declares them.
        let mut module_obj = Object::new(view.type_name.as_str()).field(
            sensor_values_container_field(&view.sensor_values_type_name, &served, cache),
        );
        for (name, section) in module_object_sections(view) {
            let Some(section) = section else { continue };
            module_obj = module_obj.field(object_section_container_field(name, section, cache));
            objects.extend(object_section_objects(&view.module, section));
        }
        if let Some(cm) = &view.control_mode {
            let (field, cm_objects) = control_mode_section(cm, cache);
            module_obj = module_obj.field(field);
            objects.extend(cm_objects);
        }
        objects.push(module_obj);

        // gqlField -> topic for every sensor field (shadows included), so a
        // recomputed computed field can read its raw inputs by name.
        let field_topics: Arc<BTreeMap<String, String>> = Arc::new(
            view.sensor_values
                .iter()
                .map(|f| (f.gql_field.clone(), f.topic.clone()))
                .collect(),
        );

        let mut sensor_values_obj = Object::new(view.sensor_values_type_name.as_str());
        for ServedSensorField { field, recompute } in served {
            let sensor_field = if recompute {
                module_recompute_field(field, cache, &view.module, field_topics.clone())
            } else {
                module_sensor_field(field, cache)
            };
            sensor_values_obj = sensor_values_obj.field(sensor_field);
            if seen_types.insert(field.type_name.clone()) {
                objects.push(module_field_object(field));
            }
        }
        objects.push(sensor_values_obj);
    }
    objects.push(modules_obj);

    Some(ModulesSchemaParts {
        query_field: constant_object_field("modules", modules_type),
        objects,
    })
}

/// A field that resolves to a constant empty (but non-null) object, so its
/// children run and read the cache from their own topics. Used for the
/// `modules` / `<module>` container levels.
pub(super) fn constant_object_field(name: &str, type_name: &str) -> Field {
    Field::new(name.to_string(), TypeRef::named_nn(type_name), |_ctx| {
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(Some(FieldValue::value(GraphQlValue::Object(
                Default::default(),
            ))))
        })
    })
}

/// The `sensorValues` container: thrs-api builds the whole SensorValues model
/// from its per-field topics and serves null until every (required) field has
/// arrived, never a partial object. Mirror that: resolve the (empty, constant)
/// container only when every relayed field's topic is cached; a recomputed
/// computed field needs no topic of its own. Its children are non-null.
pub(super) fn sensor_values_container_field(
    type_name: &str,
    served: &[ServedSensorField<'_>],
    cache: &Arc<TopicCache>,
) -> Field {
    let required: Arc<Vec<RequiredTopic>> = Arc::new(
        served
            .iter()
            .filter(|s| !s.recompute)
            .map(|s| RequiredTopic::new(&s.field.topic, &s.field.leaves))
            .collect(),
    );
    let cache = cache.clone();
    Field::new("sensorValues", TypeRef::named(type_name), move |_ctx| {
        let required = required.clone();
        let cache = cache.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(section_complete(&cache, &required)
                .then(|| FieldValue::value(GraphQlValue::Object(Default::default()))))
        })
    })
}

/// The `<field>` resolver under the sensorValues object: returns the whole
/// cached payload of the field's topic. Non-null like thrs-api; the container
/// only resolves when every field is cached (see
/// `sensor_values_container_field`).
pub(super) fn module_sensor_field(field: &ModuleFieldDef, cache: &Arc<TopicCache>) -> Field {
    let topic = field.topic.clone();
    let cache = cache.clone();
    Field::new(
        field.gql_field.clone(),
        TypeRef::named_nn(&field.type_name),
        move |_ctx| {
            let topic = topic.clone();
            let cache = cache.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                Ok(cache
                    .get(&topic)
                    .map(|json| FieldValue::value(json_to_graphql_value(&json))))
            })
        },
    )
}

/// The recompute variant of [`module_sensor_field`]: instead of relaying the
/// computed field's own topic, it derives the payload from the module's raw
/// sensor topics with thrs-api's formula (see [`crate::recompute`]). Returns
/// null when the formula isn't ported or its inputs aren't cached, so children
/// resolve null just like a relayed empty topic.
pub(super) fn module_recompute_field(
    field: &ModuleFieldDef,
    cache: &Arc<TopicCache>,
    module: &str,
    field_topics: Arc<BTreeMap<String, String>>,
) -> Field {
    let module = module.to_string();
    let gql_field = field.gql_field.clone();
    let cache = cache.clone();
    Field::new(
        field.gql_field.clone(),
        TypeRef::named_nn(&field.type_name),
        move |_ctx| {
            let module = module.clone();
            let gql_field = gql_field.clone();
            let cache = cache.clone();
            let field_topics = field_topics.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let reader = crate::recompute::InputReader::new(&cache, &field_topics);
                Ok(
                    crate::recompute::recompute_field(&module, &gql_field, &reader)
                        .map(|json| FieldValue::value(json_to_graphql_value(&json))),
                )
            })
        },
    )
}

/// One per-field payload object: a `Stamped<Inner>` leaf per declared leaf,
/// each projecting its raw PascalCase wire key off the cached payload.
pub(super) fn module_field_object(field: &ModuleFieldDef) -> Object {
    field
        .leaves
        .iter()
        .map(module_leaf_field)
        .fold(Object::new(field.type_name.as_str()), Object::field)
}

// --- Whole-object read sections (controlValues / parameters / controllerState) ---

/// The `controlMode` section (thrs-api `SwitchingControlModeType`): resolves the
/// whole cached control-mode object (null when unpublished, like thrs-api), with
/// `automatic: Boolean!` derived from `AutomaticMode` being non-null and
/// `automaticMode` the module's plain mode object (or null in manual mode).
pub(super) fn control_mode_section(
    def: &ControlModeDef,
    cache: &Arc<TopicCache>,
) -> (Field, Vec<Object>) {
    let key = Name::new(&def.key);
    let automatic = Field::new("automatic", TypeRef::named_nn(TypeRef::BOOLEAN), {
        let key = key.clone();
        move |ctx| {
            let key = key.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let parent = ctx.parent_value.try_to_value()?;
                let on = match parent {
                    GraphQlValue::Object(map) => {
                        !matches!(map.get(&key), None | Some(GraphQlValue::Null))
                    }
                    _ => false,
                };
                Ok(Some(FieldValue::value(on)))
            })
        }
    });
    let mode_type = def.automatic_mode.type_name.clone();
    let automatic_mode = Field::new("automaticMode", TypeRef::named(&mode_type), move |ctx| {
        let key = key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => match map.get(&key) {
                    None | Some(GraphQlValue::Null) => None,
                    Some(v) => Some(v.clone()),
                },
                _ => None,
            };
            Ok(value.map(FieldValue::value))
        })
    });
    let mut objects = vec![Object::new(def.type_name.as_str())
        .field(automatic)
        .field(automatic_mode)];
    objects.extend(plain_object_types(&def.automatic_mode));
    let section = ObjectSectionDef {
        topic: def.topic.clone(),
        type_name: def.type_name.clone(),
        fields: Vec::new(),
    };
    (
        object_section_container_field("controlMode", &section, cache),
        objects,
    )
}

/// A plain (non-Stamped) object type and its nested object types, named as
/// thrs-api names them (`<Class>Type`). Each field reads its by-alias key off
/// the parent JSON; scalars are non-null unless the spec marks them optional. A
/// fieldless model gets the `Empty: Void` placeholder like thrs-api.
pub(super) fn plain_object_types(def: &PlainObjectDef) -> Vec<Object> {
    let mut objects = Vec::new();
    let mut obj = Object::new(def.type_name.as_str());
    for field in &def.fields {
        obj = obj.field(plain_field(field));
        if let Some(nested) = &field.object {
            objects.extend(plain_object_types(nested));
        }
    }
    if def.fields.is_empty() {
        obj = obj.field(empty_placeholder_field());
    }
    objects.push(obj);
    objects
}

pub(super) fn plain_field(field: &PlainFieldDef) -> Field {
    let key = Name::new(&field.key);
    let base = match (&field.object, field.r#type.as_deref()) {
        (Some(nested), _) => TypeRef::named(&nested.type_name),
        (None, Some(t)) => flat_type_ref(t),
        (None, None) => TypeRef::named(TypeRef::STRING),
    };
    let type_ref = if field.optional {
        base
    } else {
        match base {
            TypeRef::Named(n) => TypeRef::NonNull(Box::new(TypeRef::Named(n))),
            other => other,
        }
    };
    Field::new(field.gql_field.clone(), type_ref, move |ctx| {
        let key = key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map.get(&key).cloned(),
                _ => None,
            };
            Ok(value.map(FieldValue::value))
        })
    })
}

/// The three optional whole-object sections of a module view, paired with the
/// GraphQL field name the UI queries them under.
pub(super) fn module_object_sections(
    view: &ModuleView,
) -> [(&'static str, &Option<ObjectSectionDef>); 3] {
    [
        ("controlValues", &view.control_values),
        ("parameters", &view.parameters),
        ("controllerState", &view.controller_state),
    ]
}

/// The `<section>` field under the module object: resolves to the whole cached
/// object on the section topic, or null when nothing is cached — matching
/// thrs-api returning null for a section the controller hasn't published.
pub(super) fn object_section_container_field(
    name: &str,
    section: &ObjectSectionDef,
    cache: &Arc<TopicCache>,
) -> Field {
    let type_name = section.type_name.as_str();
    if section.topic.is_empty() && section.fields.iter().any(|f| f.topic.is_some()) {
        // Per-topic section (actuated controlValues): assemble the section
        // object from one cached payload per component, keyed like the
        // whole-object form (`{ByAliasKey: payload}`), and only once every
        // component's payload is cached with all its required leaves (thrs-api's
        // PartialModelBuilder). The component fields then read `parent[key]`
        // exactly as for a whole-object section, so the section type can be
        // shared with the mutation return object (same name, one definition).
        let parts: Arc<Vec<(String, RequiredTopic)>> = Arc::new(
            section
                .fields
                .iter()
                .filter_map(|f| {
                    f.topic
                        .as_ref()
                        .map(|t| (f.key.clone(), RequiredTopic::new(t, &f.leaves)))
                })
                .collect(),
        );
        let cache = cache.clone();
        return Field::new(name.to_string(), TypeRef::named(type_name), move |_ctx| {
            let parts = parts.clone();
            let cache = cache.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let mut object = serde_json::Map::new();
                for (key, required) in parts.iter() {
                    let Some(payload) = cache.get(&required.topic) else {
                        return Ok(None);
                    };
                    if !required.satisfied_by(&payload) {
                        return Ok(None);
                    }
                    object.insert(key.clone(), required.rekeyed(payload));
                }
                Ok(Some(FieldValue::value(json_to_graphql_value(
                    &JsonValue::Object(object),
                ))))
            })
        });
    }
    let topic = section.topic.clone();
    let cache = cache.clone();
    Field::new(name.to_string(), TypeRef::named(type_name), move |_ctx| {
        let topic = topic.clone();
        let cache = cache.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(cache
                .get(&topic)
                .map(|json| FieldValue::value(json_to_graphql_value(&json))))
        })
    })
}

/// One topic a section needs cached, with the wire keys that must be present
/// (non-null) in its payload for thrs-api's model to validate: the required
/// leaves of the component read off it.
pub(super) struct RequiredTopic {
    pub(super) topic: String,
    pub(super) keys: Vec<String>,
    /// (device key, model key) pairs to re-key when assembling a per-topic
    /// section (`CC_DutyPoint` -> `Dutypoint`); empty when the keys agree.
    pub(super) rekey: Vec<(String, String)>,
}

impl RequiredTopic {
    fn new(topic: &str, leaves: &[ModuleLeafDef]) -> Self {
        Self {
            topic: topic.to_string(),
            keys: leaves
                .iter()
                .filter(|l| !l.optional)
                .map(|l| l.actuated_raw.clone().unwrap_or_else(|| l.raw.clone()))
                .collect(),
            rekey: leaves
                .iter()
                .filter_map(|l| l.actuated_raw.as_ref().map(|a| (a.clone(), l.raw.clone())))
                .collect(),
        }
    }

    /// The payload as the component type reads it: actuated keys renamed to
    /// the model's aliases (and the model alias dropped when both are present,
    /// as thrs-api's actuated validator does - the plain key is the request,
    /// the `CC_` key the actual value).
    fn rekeyed(&self, payload: JsonValue) -> JsonValue {
        let JsonValue::Object(mut map) = payload else {
            return payload;
        };
        for (device_key, model_key) in &self.rekey {
            match map.remove(device_key) {
                Some(v) => {
                    map.insert(model_key.clone(), v);
                }
                None => {
                    map.remove(model_key);
                }
            }
        }
        JsonValue::Object(map)
    }

    /// Whether a cached payload carries every required leaf key with a
    /// non-null value (a `{"Value": null}` leaf fails a non-optional
    /// `Stamped[X]` in thrs-api's model just like a missing key).
    fn satisfied_by(&self, payload: &JsonValue) -> bool {
        let JsonValue::Object(map) = payload else {
            return self.keys.is_empty();
        };
        self.keys.iter().all(|k| match map.get(k) {
            None | Some(JsonValue::Null) => false,
            Some(JsonValue::Object(leaf)) => !matches!(leaf.get("Value"), Some(JsonValue::Null)),
            Some(_) => true,
        })
    }
}

/// thrs-api builds a section model from its per-field topics and serves it
/// only once the whole model validates. Mirror that: every required topic is
/// cached and carries each required leaf key with a non-null value.
pub(super) fn section_complete(cache: &TopicCache, required: &[RequiredTopic]) -> bool {
    required
        .iter()
        .all(|r| cache.get(&r.topic).is_some_and(|p| r.satisfied_by(&p)))
}

/// The section object type plus any per-field component object types. A flat
/// field (a parameter scalar/list) reads its key straight off the section
/// object; a component field (a controlValues/controllerState sub-object) nests
/// a `Stamped<Inner>`-leaf object, same shape as a sensor field.
pub(super) fn object_section_objects(module: &str, section: &ObjectSectionDef) -> Vec<Object> {
    let mut objects = Vec::new();
    let mut section_obj = Object::new(section.type_name.as_str());
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    let mut added = 0usize;
    for field in &section.fields {
        if !seen.insert(field.gql_field.as_str()) {
            warn!(
                "module '{module}': duplicate {} field '{}' (snake->camel \
                 collision); keeping first",
                section.type_name, field.gql_field
            );
            continue;
        }
        if field.leaves.is_empty() {
            section_obj = section_obj.field(object_flat_field(field));
        } else {
            section_obj = section_obj.field(object_component_field(field));
            objects.push(object_component_object(field));
        }
        added += 1;
    }
    if added == 0 {
        // An empty section (e.g. a module with no controller-state fields) would
        // be an invalid empty GraphQL object. thrs-api handles this the same way
        // (`empty_pydantic_type_to_strawberry_type` adds an `_empty` placeholder,
        // exposed as `Empty: Void`), and zero-ui selects `controllerState { Empty }`
        // verbatim, so the placeholder must carry that exact name.
        section_obj = section_obj.field(empty_placeholder_field());
    }
    objects.push(section_obj);
    objects
}

/// thrs-api's `Empty: Void` placeholder on a fieldless object. Always null.
pub(super) fn empty_placeholder_field() -> Field {
    Field::new(EMPTY_FIELD, TypeRef::named(VOID_SCALAR), |_ctx| {
        async_graphql::dynamic::FieldFuture::new(async move {
            Ok(Some(FieldValue::value(GraphQlValue::Null)))
        })
    })
}

/// A flat section field (parameter): reads its `key` off the parent section
/// object and returns the raw scalar/list value (null when absent).
pub(super) fn object_flat_field(field: &ObjectFieldDef) -> Field {
    let key = field.key.clone();
    let base = flat_type_ref(field.r#type.as_deref().unwrap_or("Float"));
    // Non-null like thrs-api (`coolingFlow: Float!`, `pumpTuning: [Float!]!`)
    // unless the model field is `X | None`.
    let type_ref = if field.optional {
        base
    } else {
        TypeRef::NonNull(Box::new(base))
    };
    Field::new(field.gql_field.clone(), type_ref, move |ctx| {
        let key = key.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map
                    .get(&Name::new(&key))
                    .cloned()
                    .unwrap_or(GraphQlValue::Null),
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// A component section field (a controlValues valve / controllerState
/// controller): resolves its `key` off the parent object to a sub-object whose
/// `Stamped<Inner>` leaves are then projected.
pub(super) fn object_component_field(field: &ObjectFieldDef) -> Field {
    let key = field.key.clone();
    Field::new(
        field.gql_field.clone(),
        TypeRef::named_nn(field.component_type_name()),
        move |ctx| {
            let key = key.clone();
            async_graphql::dynamic::FieldFuture::new(async move {
                let parent = ctx.parent_value.try_to_value()?;
                let value = match parent {
                    GraphQlValue::Object(map) => map.get(&Name::new(&key)).cloned(),
                    _ => None,
                };
                Ok(value.map(FieldValue::value))
            })
        },
    )
}

pub(super) fn object_component_object(field: &ObjectFieldDef) -> Object {
    field
        .leaves
        .iter()
        .map(module_leaf_field)
        .fold(Object::new(field.component_type_name()), Object::field)
}

/// TypeRef for a flat section field type: a scalar (`Float`/`Int`/`Boolean`/
/// `String`) or a non-null list like `[Float!]`.
pub(super) fn flat_type_ref(typ: &str) -> TypeRef {
    if let Some(inner) = typ.strip_prefix('[').and_then(|s| s.strip_suffix(']')) {
        let inner = inner.trim_end_matches('!');
        return TypeRef::named_nn_list(flat_scalar_name(inner));
    }
    TypeRef::named(flat_scalar_name(typ))
}

pub(super) fn flat_scalar_name(typ: &str) -> String {
    match typ {
        "Float" => TypeRef::FLOAT,
        "Int" => TypeRef::INT,
        "Boolean" => TypeRef::BOOLEAN,
        _ => TypeRef::STRING,
    }
    .to_string()
}

/// One `{value, timestamp}` leaf: field `leaf.gql` reads wire key `leaf.raw`
/// off the parent payload, typed as the shared `Stamped<Inner>` wrapper.
pub(super) fn module_leaf_field(leaf: &ModuleLeafDef) -> Field {
    let raw_key = Name::new(&leaf.raw);
    let enum_values = leaf.enum_values.clone();
    let default = leaf.default.as_ref().map(json_to_graphql_value);
    // Non-null like thrs-api: a section is null as a whole when incomplete
    // (see `sensor_values_container_field`), never partially populated.
    let type_ref = TypeRef::named_nn(view_stamped_type_name(leaf));
    Field::new(leaf.gql.clone(), type_ref, move |ctx| {
        let raw_key = raw_key.clone();
        let enum_values = enum_values.clone();
        let default = default.clone();
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let mut value = match parent {
                GraphQlValue::Object(map) => {
                    map.get(&raw_key).cloned().unwrap_or(GraphQlValue::Null)
                }
                _ => GraphQlValue::Null,
            };
            // A leaf absent from the payload takes the model's default, as
            // thrs-api serves it (`{"value": null, "timestamp": epoch}`).
            if matches!(value, GraphQlValue::Null) {
                if let Some(d) = default {
                    value = d;
                }
            }
            // Enum leaf: translate the cached wire value to the thrs-api member
            // name so `value` reads e.g. "LOCAL" (not 0) / "OFF" (not "off").
            if let Some(map) = &enum_values {
                value = map_enum_leaf_value(value, map);
            }
            Ok(nullable(value))
        })
    })
}

/// The `Stamped<Inner>` wrapper key for a leaf: the enum type name for an enum
/// leaf (`ControlMode`), `<Scalar>List` for a tuple leaf (`[Float!]` ->
/// `FloatList`), else the scalar itself.
pub(super) fn stamped_inner_key(leaf: &ModuleLeafDef) -> String {
    if let Some(name) = &leaf.enum_type {
        return name.clone();
    }
    match leaf.r#type.strip_prefix('[') {
        Some(inner) => format!(
            "{}List",
            flat_scalar_name(inner.trim_end_matches(['!', ']']))
        ),
        None => leaf.r#type.clone(),
    }
}

/// thrs-api's name for a view leaf's Stamped wrapper type:
/// `<Inner>[Optional]StampedType` with Strawberry's spellings (`Bool`, not
/// `Boolean`; `FloatList` for a tuple; the enum class name), e.g.
/// `FloatStampedType`, `FloatOptionalStampedType`, `BoolStampedType`,
/// `PumpControlModeOptionalStampedType`. Distinct from the flat-topic wrappers
/// (`Stamped<Inner>`) because these carry thrs-api's nullability: `value` is
/// non-null unless the leaf is optional, `timestamp` always.
pub(super) fn view_stamped_type_name(leaf: &ModuleLeafDef) -> String {
    let inner = match stamped_inner_key(leaf).as_str() {
        "Boolean" => "Bool".to_string(),
        "BooleanList" => "BoolList".to_string(),
        other => other.to_string(),
    };
    let optional = if leaf.optional { "Optional" } else { "" };
    format!("{inner}{optional}StampedType")
}

/// The wrapper object for a view leaf (see [`view_stamped_type_name`]).
pub(super) fn view_stamped_object(leaf: &ModuleLeafDef) -> Object {
    let inner = stamped_inner_key(leaf);
    let value_ref = match stamped_value_type_ref(&inner) {
        r if leaf.optional => r,
        TypeRef::Named(n) => TypeRef::NonNull(Box::new(TypeRef::Named(n))),
        list => TypeRef::NonNull(Box::new(list)),
    };
    Object::new(view_stamped_type_name(leaf))
        .field(stamped_wrapper_field("value", "Value", value_ref))
        .field(stamped_timestamp_field(true))
}

/// The GraphQL type of a `Stamped<Inner>` wrapper's `value`, from its key (see
/// `stamped_inner_key`): a scalar, a non-null list of it, or a named enum.
pub(super) fn stamped_value_type_ref(inner_key: &str) -> TypeRef {
    match inner_key {
        "Float" | "Int" | "Boolean" | "String" => TypeRef::named(flat_scalar_name(inner_key)),
        key => match key.strip_suffix("List") {
            Some(scalar) => TypeRef::named_nn_list(flat_scalar_name(scalar)),
            None => TypeRef::named(key),
        },
    }
}

/// Rewrite the `Value` of a `Stamped` enum leaf from its raw wire value to the
/// thrs-api enum member (`0` -> `LOCAL`, `"off"` -> `OFF`). `TimeStamp` and
/// any value missing from the map are left untouched, so an unexpected wire
/// value still surfaces rather than vanishing.
pub(super) fn map_enum_leaf_value(
    value: GraphQlValue,
    enum_values: &BTreeMap<String, String>,
) -> GraphQlValue {
    let GraphQlValue::Object(mut map) = value else {
        return value;
    };
    let value_key = Name::new("Value");
    if let Some(name) = map
        .get(&value_key)
        .and_then(graphql_scalar_to_key)
        .and_then(|key| enum_values.get(&key))
    {
        map.insert(value_key, GraphQlValue::Enum(Name::new(name)));
    }
    GraphQlValue::Object(map)
}

/// The map lookup key for a scalar wire value: integers as `"0"`, strings and
/// bools as themselves. Floats fall back to their display form (enums don't use
/// float values, but this keeps the mapping total).
pub(super) fn graphql_scalar_to_key(value: &GraphQlValue) -> Option<String> {
    match value {
        GraphQlValue::Number(n) => n
            .as_i64()
            .map(|i| i.to_string())
            .or_else(|| n.as_u64().map(|u| u.to_string()))
            .or_else(|| n.as_f64().map(|f| f.to_string())),
        GraphQlValue::String(s) => Some(s.clone()),
        GraphQlValue::Boolean(b) => Some(b.to_string()),
        _ => None,
    }
}
