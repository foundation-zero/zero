use std::collections::BTreeMap;

use anyhow::bail;

use crate::api_model::{GraphqlPath, TopicDef};

/// One level of a Query tree: the nodes under one branch, by field name.
pub type QueryTree = BTreeMap<String, PathNode>;

/// A node in the Query tree of one Spec
#[derive(Debug, Clone)]
pub enum PathNode {
    Branch(QueryTree),
    Topic(TopicDef),
}

impl PathNode {
    /// The first Topic at or below this node, for error messages.
    #[must_use]
    pub fn first_topic(&self) -> &str {
        match self {
            PathNode::Topic(topic) => topic.topic.as_str(),
            PathNode::Branch(children) => children
                .values()
                .next()
                .map(PathNode::first_topic)
                .unwrap_or_default(),
        }
    }
}

/// Place every queryable Topic of one Spec at its GraphQL path. Errors on a
/// topic without a GraphQL path or on a Path conflict.
pub(super) fn query_tree(topics: Vec<TopicDef>) -> anyhow::Result<QueryTree> {
    let mut root = QueryTree::new();
    for topic in topics.into_iter().filter(TopicDef::is_queryable) {
        let path = GraphqlPath::from_address(&topic.topic)?;
        insert_topic(&mut root, path.segments(), topic)?;
    }
    Ok(root)
}

/// Insert a Topic at the `remaining` part of its GraphQL path.
fn insert_topic(node: &mut QueryTree, remaining: &[String], topic: TopicDef) -> anyhow::Result<()> {
    let Some((segment, rest)) = remaining.split_first() else {
        return Ok(());
    };

    if rest.is_empty() {
        if let Some(branch) = node.get(segment) {
            return tree_conflict(&topic.topic, branch.first_topic());
        }
        node.insert(segment.clone(), PathNode::Topic(topic));
        return Ok(());
    }

    let child = node
        .entry(segment.clone())
        .or_insert_with(|| PathNode::Branch(QueryTree::new()));

    match child {
        PathNode::Branch(children) => insert_topic(children, rest, topic),
        existing @ PathNode::Topic(_) => tree_conflict(existing.first_topic(), &topic.topic),
    }
}

fn tree_conflict<T>(topic: &str, existing: &str) -> anyhow::Result<T> {
    bail!("GraphQL path conflict: topic '{topic}' conflicts with topic '{existing}'")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::api_model::{Direction, FieldType, TopicKind};

    /// Helper for a Send Topic with one Float field.
    fn mock_topic(topic: &str, field: &str) -> TopicDef {
        TopicDef {
            topic: topic.to_string(),
            fields: BTreeMap::from_iter(vec![(field.to_string(), FieldType::Float)]),
            payload_schema_ref: Some(format!("#/components/schemas/{field}payload")),
            operation: Direction::Send,
            ttl_secs: None,
            kind: TopicKind::Single,
        }
    }

    #[test_log::test]
    fn test_topics_on_the_same_graphql_path_conflict() {
        // `b-c` and `b_c` both sanitize to `bC`.
        let topics = vec![mock_topic("a/b-c", "x"), mock_topic("a/b_c", "y")];

        let err = query_tree(topics).unwrap_err();
        assert_eq!(
            err.to_string(),
            "GraphQL path conflict: topic 'a/b_c' conflicts with topic 'a/b-c'"
        );
    }

    #[test_log::test]
    fn test_topic_that_is_also_a_parent_conflicts_in_either_order() {
        for topics in [
            vec![mock_topic("a/b", "x"), mock_topic("a/b/c", "y")],
            vec![mock_topic("a/b/c", "y"), mock_topic("a/b", "x")],
        ] {
            let err = query_tree(topics).unwrap_err();
            assert_eq!(
                err.to_string(),
                "GraphQL path conflict: topic 'a/b' conflicts with topic 'a/b/c'"
            );
        }
    }

    #[test_log::test]
    fn test_address_empty_errors() {
        for address in ["//", ""] {
            let err = query_tree(vec![mock_topic(address, "v")]).unwrap_err();
            assert_eq!(
                err.to_string(),
                format!("topic '{address}' would result in an empty GraphQL name")
            );
        }
    }
}
