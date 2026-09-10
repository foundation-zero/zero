use std::collections::BTreeMap;
use std::path::Path;

use anyhow::Context;
use serde::Deserialize;
use serde_json::Value;

/// Suffix identifying topic-metadata files inside a spec directory.
pub const METADATA_SUFFIX: &str = "-metadata.json";

/// Static attributes for one concrete topic.
#[derive(Debug, Clone, Deserialize)]
pub struct TopicMetadataEntry {
    pub topic: String,
    #[serde(default)]
    pub metadata: BTreeMap<String, Value>,
}

/// A metadata file: static attributes for the topics of one domain group.
///
/// The `group` matches a parametrized channel's static prefix (e.g.
/// `power-tags`) so its entries can be merged into that group's list query.
#[derive(Debug, Clone, Deserialize)]
pub struct MetadataFile {
    pub group: String,
    #[serde(default)]
    pub group_by: Option<String>,
    #[serde(default)]
    pub topics: Vec<TopicMetadataEntry>,
}

/// Whether this path is a topic-metadata file (not an AsyncAPI document).
pub fn is_metadata_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.ends_with(METADATA_SUFFIX))
}

/// Load every `*-metadata.json` file from a spec directory.
pub fn load_metadata(spec_dir: &str) -> anyhow::Result<Vec<MetadataFile>> {
    let dir = Path::new(spec_dir);
    if !dir.is_dir() {
        anyhow::bail!(
            "spec_dir does not exist or is not a directory: {}",
            spec_dir
        );
    }

    let mut paths: Vec<_> = std::fs::read_dir(dir)?
        .filter_map(|entry| entry.ok().map(|e| e.path()))
        .filter(|path| is_metadata_file(path))
        .collect();
    paths.sort();

    paths
        .into_iter()
        .map(|path| {
            let display = path.display().to_string();
            let content = std::fs::read_to_string(&path)
                .with_context(|| format!("failed to read {display}"))?;
            serde_json::from_str(&content).with_context(|| format!("failed to parse {display}"))
        })
        .collect()
}

/// Static attributes per concrete topic: `topic → (group, attributes)`.
pub type MetadataByTopic = BTreeMap<String, (String, BTreeMap<String, Value>)>;

/// Flat lookup of every annotated topic across all files:
/// `topic → (group, metadata)`.
pub fn metadata_by_topic(files: &[MetadataFile]) -> MetadataByTopic {
    files
        .iter()
        .flat_map(|file| {
            file.topics.iter().map(move |entry| {
                (
                    entry.topic.clone(),
                    (file.group.clone(), entry.metadata.clone()),
                )
            })
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::io::Write;

    fn write_file(dir: &Path, name: &str, content: &str) {
        let mut file = std::fs::File::create(dir.join(name)).unwrap();
        file.write_all(content.as_bytes()).unwrap();
    }

    #[test]
    fn test_is_metadata_file() {
        assert!(is_metadata_file(Path::new(
            "/specs/power-tags-metadata.json"
        )));
        assert!(!is_metadata_file(Path::new("/specs/power-tags.json")));
        assert!(!is_metadata_file(Path::new("/specs/data.json")));
    }

    #[test]
    fn test_load_metadata_multiple_files() {
        let dir = std::env::temp_dir().join("mqtt-graphql-metadata-test-ok");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();

        write_file(
            &dir,
            "power-tags-metadata.json",
            r#"{
              "group": "power-tags",
              "topics": [
                {"topic": "power-tags/10P1/x", "metadata": {"panel": "10P1", "component": "150F01"}}
              ]
            }"#,
        );
        write_file(
            &dir,
            "hull-temperature-metadata.json",
            r#"{
              "group": "hull-temperature",
              "topics": [
                {"topic": "hull-temperature/temperatures", "metadata": {"zone": "fwd"}}
              ]
            }"#,
        );
        // Non-metadata json must be ignored
        write_file(&dir, "other.json", r#"{"asyncapi": "3.0.0"}"#);

        let files = load_metadata(dir.to_str().unwrap()).unwrap();
        assert_eq!(files.len(), 2);
        assert!(files.iter().any(|f| f.group == "power-tags"));
        assert!(files.iter().any(|f| f.group == "hull-temperature"));

        let by_topic = metadata_by_topic(&files);
        let (group, meta) = by_topic.get("power-tags/10P1/x").unwrap();
        assert_eq!(group, "power-tags");
        assert_eq!(meta.get("component"), Some(&json!("150F01")));

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_load_metadata_missing_dir_errors() {
        assert!(load_metadata("/nonexistent-specs").is_err());
    }

    #[test]
    fn test_load_metadata_malformed_errors() {
        let dir = std::env::temp_dir().join("mqtt-graphql-metadata-test-bad");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        write_file(&dir, "broken-metadata.json", "{ not json");

        assert!(load_metadata(dir.to_str().unwrap()).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }
}
