use std::collections::BTreeMap;

use anyhow::bail;

use crate::{
    api_model::{Api, TopicDef},
    graphql::{GraphqlPath, queryable_topic},
};

/// A node in the Query tree of Topics
#[derive(Debug, Clone)]
pub enum PathNode<'a> {
    Branch(BTreeMap<String, PathNode<'a>>),
    Topic { spec: &'a str, topic: &'a TopicDef },
}

impl PathNode<'_> {
    /// The first Topic at or below this node, for error messages.
    #[must_use]
    pub fn first_topic(&self) -> &str {
        match self {
            PathNode::Topic { topic, .. } => topic.topic.as_str(),
            PathNode::Branch(children) => children
                .values()
                .next()
                .map(PathNode::first_topic)
                .unwrap_or_default(),
        }
    }
}

/// Merge the GraphQL paths of every queryable Topic, across all Specs, into
/// one tree. Errors on a Path conflict.
pub fn graphql_tree(api: &Api) -> anyhow::Result<BTreeMap<String, PathNode<'_>>> {
    let mut root = BTreeMap::new();
    for model in &api.models {
        for topic in model.topics.iter().filter(|&t| queryable_topic(t)) {
            let path = GraphqlPath::from_address(&topic.topic)?;
            insert_topic(&mut root, path.segments(), &model.name, topic)?;
        }
    }
    Ok(root)
}

/// Insert a Topic at the `remaining` part of its GraphQL path.
fn insert_topic<'a>(
    node: &mut BTreeMap<String, PathNode<'a>>,
    remaining: &[String],
    spec: &'a str,
    topic: &'a TopicDef,
) -> anyhow::Result<()> {
    let Some((segment, rest)) = remaining.split_first() else {
        return Ok(());
    };

    if rest.is_empty() {
        if let Some(branch) = node.get(segment) {
            return tree_conflict(&topic.topic, branch.first_topic());
        }
        node.insert(segment.clone(), PathNode::Topic { spec, topic });
        return Ok(());
    }

    let child = node
        .entry(segment.clone())
        .or_insert_with(|| PathNode::Branch(BTreeMap::new()));

    match child {
        PathNode::Branch(children) => insert_topic(children, rest, spec, topic),
        existing @ PathNode::Topic { .. } => tree_conflict(existing.first_topic(), &topic.topic),
    }
}

fn tree_conflict<T>(topic: &str, existing: &str) -> anyhow::Result<T> {
    bail!("GraphQL path conflict: topic '{topic}' conflicts with topic '{existing}'")
}
