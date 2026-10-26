use std::collections::BTreeMap;
use std::path::Path;

use serde_json::Value;

/// Suffix identifying topic-metadata files inside a spec directory.
pub const METADATA_SUFFIX: &str = "-metadata.json";

/// Whether this path is a topic-metadata file (not an AsyncAPI document).
#[must_use]
pub(crate) fn is_metadata_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.ends_with(METADATA_SUFFIX))
}

/// Static attributes per concrete topic: `topic → (group, attributes)`.
pub type MetadataByTopic = BTreeMap<String, BTreeMap<String, Value>>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test_log::test]
    fn test_is_metadata_file() {
        assert!(is_metadata_file(Path::new(
            "/specs/power-tags-metadata.json"
        )));
        assert!(!is_metadata_file(Path::new("/specs/power-tags.json")));
        assert!(!is_metadata_file(Path::new("/specs/data.json")));
    }
}
