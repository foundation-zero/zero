//! Resolving `$ref`s inside one AsyncAPI document.

use std::collections::BTreeMap;
use std::fmt::Debug;

use log::info;
use roas_asyncapi::common::reference::{RefOr, Reference};

use super::roas::{Channel, Document, Message, Operation, SchemaOrMultiFormat};

/// Follow a component `$ref` to a real entry
pub(super) fn resolve_ref_to_entry<'a, T: Debug>(
    reference: &'a Reference,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
    mut traversed_keys: Vec<&'a str>,
) -> Option<(Option<String>, &'a T)> {
    let pointer = reference.local_pointer()?;
    let key = reference.local_key()?;

    let entries = if reference.reference.starts_with("#/components/") {
        entries_components
    } else {
        entries_main
    };

    let entries = entries?;

    if (traversed_keys).contains(&pointer) {
        info!("Found circular refs, aborting on: {key}");
        return None;
    }

    match entries.get(&key)? {
        RefOr::Reference(nested) => {
            traversed_keys.push(pointer);
            resolve_ref_to_entry(nested, entries_main, entries_components, traversed_keys)
        }
        RefOr::Item(entry) => Some((Some(reference.reference.clone()), entry)),
    }
}

fn resolve_refor<'a, T: Debug>(
    reference: &'a RefOr<T>,
    entries_main: Option<&'a BTreeMap<String, RefOr<T>>>,
    entries_components: Option<&'a BTreeMap<String, RefOr<T>>>,
) -> Option<(Option<String>, &'a T)> {
    match reference {
        RefOr::Item(m) => Some((None, m)),
        RefOr::Reference(reference) => {
            resolve_ref_to_entry(reference, entries_main, entries_components, vec![])
        }
    }
}

/// Resolve an operation's channel, which is always a `$ref`.
pub(super) fn resolve_channel<'a>(
    r: &'a Reference,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Channel)> {
    resolve_ref_to_entry(
        r,
        Some(&doc.channels),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.channels),
        vec![],
    )
}

pub(super) fn resolve_operation<'a>(
    r: &'a RefOr<Operation>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Operation)> {
    resolve_refor(
        r,
        Some(&doc.operations),
        doc.components
            .as_ref()
            .map(|componentens| &componentens.operations),
    )
}

pub(super) fn resolve_message<'a>(
    r: &'a RefOr<Message>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a Message)> {
    resolve_refor(
        r,
        None,
        doc.components
            .as_ref()
            .map(|componentens| &componentens.messages),
    )
}

pub(super) fn resolve_payload_schema<'a>(
    r: &'a RefOr<SchemaOrMultiFormat>,
    doc: &'a Document,
) -> Option<(Option<String>, &'a SchemaOrMultiFormat)> {
    resolve_refor(
        r,
        None,
        doc.components
            .as_ref()
            .map(|componentens| &componentens.schemas),
    )
}
