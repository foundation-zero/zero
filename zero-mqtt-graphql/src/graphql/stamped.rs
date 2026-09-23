use super::*;

/// Wrapper type name for a Stamped scalar, e.g. `Float` -> `StampedFloat`.
pub(super) fn stamped_wrapper_type_name(inner: &str) -> String {
    format!("Stamped{inner}")
}

/// The `Stamped<T>` type `{ value, timestamp }`, projected from `Value`/`TimeStamp`.
pub(super) fn stamped_wrapper_object(inner: &str) -> Object {
    let type_name = stamped_wrapper_type_name(inner);
    // `timestamp`, not `timeStamp`: thrs-api's field name; `TimeStamp` is only the wire key.
    Object::new(type_name.as_str())
        .field(stamped_wrapper_field(
            "value",
            "Value",
            stamped_value_type_ref(inner),
        ))
        .field(stamped_timestamp_field(false))
}

/// The `timestamp` field: the raw RFC 3339 `TimeStamp` wire value, served as-is.
pub(super) fn stamped_timestamp_field(non_null: bool) -> Field {
    let type_ref = if non_null {
        TypeRef::named_nn(DATETIME_SCALAR)
    } else {
        TypeRef::named(DATETIME_SCALAR)
    };
    Field::new("timestamp", type_ref, move |ctx| {
        async_graphql::dynamic::FieldFuture::new(async move {
            let parent = ctx.parent_value.try_to_value()?;
            let value = match parent {
                GraphQlValue::Object(map) => map
                    .get(&Name::new("TimeStamp"))
                    .cloned()
                    .unwrap_or(GraphQlValue::Null),
                _ => GraphQlValue::Null,
            };
            Ok(Some(FieldValue::value(value)))
        })
    })
}

/// A `Stamped<T>` field `name` reading wire key `raw_key` off the parent.
pub(super) fn stamped_wrapper_field(name: &str, raw_key: &str, type_ref: TypeRef) -> Field {
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

/// Every distinct Stamped wrapper type used by topics, groups, views and lifecycles.
pub(super) fn register_stamped_wrapper_objects(
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    views: &[ViewDef],
    lifecycles: &[LifecycleDef],
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
    let view_leaves = views
        .iter()
        .flat_map(|v| v.leaves())
        .chain(lifecycles.iter().flat_map(|l| l.leaves()));
    // View leaves use thrs-api's wrapper names (`FloatStampedType` etc.).
    let mut view_wrappers: BTreeMap<String, Object> = BTreeMap::new();
    for leaf in view_leaves {
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
