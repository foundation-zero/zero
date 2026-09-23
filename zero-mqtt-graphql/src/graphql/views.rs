use super::*;

/// The query field plus every type it needs.
pub(super) struct ViewSchemaParts {
    pub(super) gql: Field,
    pub(super) objects: Vec<Object>,
}

/// A stamped section's fields in spec order, minus later duplicates of a name
/// (async-graphql panics on a duplicate field).
pub(super) fn served_sensor_fields<'a>(
    member: &str,
    section: &'a StampedFieldsSection,
) -> Vec<&'a StampedFieldDef> {
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    section
        .fields
        .iter()
        .filter(|f| {
            let first = seen.insert(f.gql.as_str());
            if !first {
                warn!(
                    "member '{member}': duplicate {} field '{}' (snake->camel \
                     collision); keeping first, skipping topic '{}'",
                    section.gql, f.gql, f.topic
                );
            }
            first
        })
        .collect()
}

/// Build every declared view; one whose query field is already claimed is skipped.
pub(super) fn register_views(
    views: &[ViewDef],
    cache: &Arc<TopicCache>,
    used_query_fields: &mut BTreeSet<String>,
    enable_optional_sensor_values: bool,
) -> Vec<ViewSchemaParts> {
    let mut parts = Vec::new();
    for view in views {
        if !used_query_fields.insert(view.gql.clone()) {
            warn!("'{}' query field already claimed — skipping view", view.gql);
            continue;
        }
        let mut objects: Vec<Object> = Vec::new();
        let mut view_obj = Object::new(view.type_name.as_str());
        // Types like `ControlPumpType` are shared across members; register once.
        let mut seen_types: BTreeSet<String> = BTreeSet::new();

        for member in &view.members {
            view_obj = view_obj.field(constant_object_field(&member.gql, &member.type_name));
            let mut member_obj = Object::new(member.type_name.as_str());
            for section in &member.sections {
                match section {
                    SectionDef::StampedFields(stamped) => {
                        let served = served_sensor_fields(&member.gql, stamped);
                        member_obj = member_obj.field(sensor_values_container_field(
                            &stamped.gql,
                            &stamped.type_name,
                            &served,
                            cache,
                            enable_optional_sensor_values,
                        ));
                        let mut section_obj = Object::new(stamped.type_name.as_str());
                        for field in served {
                            section_obj = section_obj.field(module_sensor_field(
                                field,
                                cache,
                                enable_optional_sensor_values,
                            ));
                            if seen_types.insert(field.type_name.clone()) {
                                objects.push(module_field_object(field));
                            }
                        }
                        objects.push(section_obj);
                    }
                    SectionDef::Object(object) => {
                        member_obj = member_obj.field(object_section_container_field(
                            &object.gql,
                            &object.section,
                            cache,
                        ));
                        objects.extend(object_section_objects(&member.gql, &object.section));
                    }
                    SectionDef::Switch(switch) => {
                        let (field, switch_objects) =
                            control_mode_section(&switch.gql, &switch.section, cache);
                        member_obj = member_obj.field(field);
                        objects.extend(switch_objects);
                    }
                }
            }
            objects.push(member_obj);
        }
        objects.push(view_obj);
        parts.push(ViewSchemaParts {
            gql: constant_object_field(&view.gql, &view.type_name),
            objects,
        });
    }
    parts
}

/// A constant non-null container so its children resolve from their own topics.
pub(super) fn constant_object_field(name: &str, type_name: &str) -> Field {
    Field::new(name.to_string(), TypeRef::named_nn(type_name), |_ctx| {
        FieldFuture::new(async move {
            Ok(Some(FieldValue::value(GraphQlValue::Object(
                Default::default(),
            ))))
        })
    })
}

/// The `sensorValues` container: null until every field is cached, as in thrs-api.
/// With `partial` it resolves once any field is complete.
pub(super) fn sensor_values_container_field(
    field_name: &str,
    type_name: &str,
    served: &[&StampedFieldDef],
    cache: &Arc<TopicCache>,
    partial: bool,
) -> Field {
    let required: Arc<Vec<RequiredTopic>> = Arc::new(
        served
            .iter()
            .map(|f| RequiredTopic::new(&f.topic, &f.leaves))
            .collect(),
    );
    let cache = cache.clone();
    Field::new(
        field_name.to_string(),
        TypeRef::named(type_name),
        move |_ctx| {
            let required = required.clone();
            let cache = cache.clone();
            FieldFuture::new(async move {
                let complete = if partial {
                    section_any_complete(&cache, &required)
                } else {
                    section_complete(&cache, &required)
                };
                Ok(complete.then(|| FieldValue::value(GraphQlValue::Object(Default::default()))))
            })
        },
    )
}

/// A `sensorValues` field serving its topic's payload; nullable with `partial`
/// so one missing sensor doesn't null its siblings.
pub(super) fn module_sensor_field(
    field: &StampedFieldDef,
    cache: &Arc<TopicCache>,
    partial: bool,
) -> Field {
    let topic = field.topic.clone();
    let required = partial.then(|| Arc::new(RequiredTopic::new(&field.topic, &field.leaves)));
    let cache = cache.clone();
    let type_ref = if partial {
        TypeRef::named(&field.type_name)
    } else {
        TypeRef::named_nn(&field.type_name)
    };
    Field::new(field.gql.clone(), type_ref, move |_ctx| {
        let topic = topic.clone();
        let required = required.clone();
        let cache = cache.clone();
        FieldFuture::new(async move {
            Ok(cache
                .get(&topic)
                .filter(|json| required.as_ref().is_none_or(|r| r.satisfied_by(json)))
                .map(|json| FieldValue::value(json_to_graphql_value(&json))))
        })
    })
}

/// A per-field payload object with one Stamped leaf per declared leaf.
pub(super) fn module_field_object(field: &StampedFieldDef) -> Object {
    field
        .leaves
        .iter()
        .map(module_leaf_field)
        .fold(Object::new(field.type_name.as_str()), Object::field)
}

/// The `controlMode` section; `automatic` is derived from `AutomaticMode` being non-null.
pub(super) fn control_mode_section(
    name: &str,
    def: &SwitchSectionDef,
    cache: &Arc<TopicCache>,
) -> (Field, Vec<Object>) {
    let key = Name::new(&def.key);
    let automatic = Field::new(
        def.flag_field.clone(),
        TypeRef::named_nn(TypeRef::BOOLEAN),
        move |ctx| {
            let key = key.clone();
            FieldFuture::new(async move {
                let on = parent_key(&ctx, &key)?.is_some();
                Ok(Some(FieldValue::value(on)))
            })
        },
    );
    let automatic_mode = key_field(
        def.object_field.clone(),
        TypeRef::named(&def.object.type_name),
        &def.key,
    );
    let mut objects = vec![Object::new(def.type_name.as_str())
        .field(automatic)
        .field(automatic_mode)];
    objects.extend(plain_object_types(&def.object));
    let section = ObjectSectionDef {
        operation: None,
        topic: def.topic.clone(),
        type_name: def.type_name.clone(),
        fields: Vec::new(),
    };
    (
        object_section_container_field(name, &section, cache),
        objects,
    )
}

/// A plain (non-Stamped) object type and its nested types, named `<Class>Type`.
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
    key_field(field.gql.clone(), type_ref, &field.key)
}

/// A `<section>` field: the cached section object, or null when unpublished.
pub(super) fn object_section_container_field(
    name: &str,
    section: &ObjectSectionDef,
    cache: &Arc<TopicCache>,
) -> Field {
    let type_name = section.type_name.as_str();
    if section.is_per_topic() {
        // Per-topic section: assemble `{ByAliasKey: payload}` once every component
        // is complete, so the type is shared with the whole-object form.
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
            FieldFuture::new(async move {
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
        FieldFuture::new(async move {
            Ok(cache
                .get(&topic)
                .map(|json| FieldValue::value(json_to_graphql_value(&json))))
        })
    })
}

/// A topic a section needs cached, with the leaf keys that must be non-null.
pub(super) struct RequiredTopic {
    pub(super) topic: String,
    pub(super) keys: Vec<String>,
    /// (device key, model key) renames, e.g. `CC_DutyPoint` -> `Dutypoint`.
    pub(super) rekey: Vec<(String, String)>,
}

impl RequiredTopic {
    fn new(topic: &str, leaves: &[LeafDef]) -> Self {
        Self {
            topic: topic.to_string(),
            keys: leaves
                .iter()
                .filter(|l| !l.optional)
                .map(|l| l.actuated_key.clone().unwrap_or_else(|| l.key.clone()))
                .collect(),
            rekey: leaves
                .iter()
                .filter_map(|l| l.actuated_key.as_ref().map(|a| (a.clone(), l.key.clone())))
                .collect(),
        }
    }

    /// Rename actuated keys; the `CC_` key (actual value) wins over the plain
    /// (requested) key, as in thrs-api.
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

    /// Whether every required leaf key is present and non-null (`{"Value": null}` fails too).
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

/// Whether every required topic is cached and complete, as thrs-api requires.
pub(super) fn section_complete(cache: &TopicCache, required: &[RequiredTopic]) -> bool {
    required
        .iter()
        .all(|r| cache.get(&r.topic).is_some_and(|p| r.satisfied_by(&p)))
}

/// Whether any required topic is complete, or there is none.
pub(super) fn section_any_complete(cache: &TopicCache, required: &[RequiredTopic]) -> bool {
    required.is_empty()
        || required
            .iter()
            .any(|r| cache.get(&r.topic).is_some_and(|p| r.satisfied_by(&p)))
}

/// The section object type plus its component object types.
pub(super) fn object_section_objects(module: &str, section: &ObjectSectionDef) -> Vec<Object> {
    let mut objects = Vec::new();
    let mut section_obj = Object::new(section.type_name.as_str());
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    let mut added = 0usize;
    for field in &section.fields {
        if !seen.insert(field.gql.as_str()) {
            warn!(
                "member '{module}': duplicate {} field '{}' (snake->camel \
                 collision); keeping first",
                section.type_name, field.gql
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
        // An empty GraphQL object is invalid; zero-ui selects `controllerState { Empty }`.
        section_obj = section_obj.field(empty_placeholder_field());
    }
    objects.push(section_obj);
    objects
}

/// The always-null `Empty: Void` placeholder on a fieldless object.
pub(super) fn empty_placeholder_field() -> Field {
    Field::new(EMPTY_FIELD, TypeRef::named(VOID_SCALAR), |_ctx| {
        FieldFuture::new(async move { Ok(Some(FieldValue::value(GraphQlValue::Null))) })
    })
}

/// A flat (parameter) field reading its `key` off the parent section.
pub(super) fn object_flat_field(field: &ObjectFieldDef) -> Field {
    let base = flat_type_ref(field.r#type.as_deref().unwrap_or("Float"));
    let type_ref = if field.optional {
        base
    } else {
        TypeRef::NonNull(Box::new(base))
    };
    key_field(field.gql.clone(), type_ref, &field.key)
}

/// A component field resolving its `key` to a sub-object of Stamped leaves.
pub(super) fn object_component_field(field: &ObjectFieldDef) -> Field {
    key_field(
        field.gql.clone(),
        TypeRef::named_nn(field.component_type_name()),
        &field.key,
    )
}

pub(super) fn object_component_object(field: &ObjectFieldDef) -> Object {
    field
        .leaves
        .iter()
        .map(module_leaf_field)
        .fold(Object::new(field.component_type_name()), Object::field)
}

/// TypeRef for a flat field: a scalar or a list like `[Float!]`.
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

/// One `{value, timestamp}` leaf reading wire key `leaf.key` off the parent.
pub(super) fn module_leaf_field(leaf: &LeafDef) -> Field {
    let raw_key = Name::new(&leaf.key);
    let enum_values = leaf.enum_values.clone();
    let default = leaf.default.as_ref().map(json_to_graphql_value);
    // Non-null: an incomplete section is null as a whole.
    let type_ref = TypeRef::named_nn(view_stamped_type_name(leaf));
    Field::new(leaf.gql.clone(), type_ref, move |ctx| {
        let raw_key = raw_key.clone();
        let enum_values = enum_values.clone();
        let default = default.clone();
        FieldFuture::new(async move {
            // An absent leaf serves thrs-api's default `{value: null, timestamp: epoch}`.
            let mut value = parent_key(&ctx, &raw_key)?
                .or(default)
                .unwrap_or(GraphQlValue::Null);
            if let Some(map) = &enum_values {
                value = map_enum_leaf_value(value, map);
            }
            Ok(nullable(value))
        })
    })
}

/// A leaf's wrapper key: its enum name, `<Scalar>List` for a tuple, else the scalar.
pub(super) fn stamped_inner_key(leaf: &LeafDef) -> String {
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

/// thrs-api's `<Inner>[Optional]StampedType` name (e.g. `BoolStampedType`); unlike
/// flat-topic wrappers, `value` is non-null unless the leaf is optional.
pub(super) fn view_stamped_type_name(leaf: &LeafDef) -> String {
    let inner = match stamped_inner_key(leaf).as_str() {
        "Boolean" => "Bool".to_string(),
        "BooleanList" => "BoolList".to_string(),
        other => other.to_string(),
    };
    let optional = if leaf.optional { "Optional" } else { "" };
    format!("{inner}{optional}StampedType")
}

/// The wrapper object for a view leaf (see [`view_stamped_type_name`]).
pub(super) fn view_stamped_object(leaf: &LeafDef) -> Object {
    let inner = stamped_inner_key(leaf);
    let value_ref = match stamped_value_type_ref(&inner) {
        r if leaf.optional => r,
        TypeRef::Named(n) => TypeRef::NonNull(Box::new(TypeRef::Named(n))),
        list => TypeRef::NonNull(Box::new(list)),
    };
    Object::new(view_stamped_type_name(leaf))
        .field(key_field("value", value_ref, "Value"))
        .field(stamped_timestamp_field(true))
}

/// The type of a wrapper's `value`: a scalar, a list of it, or a named enum.
pub(super) fn stamped_value_type_ref(inner_key: &str) -> TypeRef {
    match inner_key {
        "Float" | "Int" | "Boolean" | "String" => TypeRef::named(flat_scalar_name(inner_key)),
        key => match key.strip_suffix("List") {
            Some(scalar) => TypeRef::named_nn_list(flat_scalar_name(scalar)),
            None => TypeRef::named(key),
        },
    }
}

/// Rewrite an enum leaf's wire `Value` to its member name (`0` -> `LOCAL`);
/// unmapped values pass through so they still surface.
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

/// The enum map lookup key for a scalar wire value.
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
