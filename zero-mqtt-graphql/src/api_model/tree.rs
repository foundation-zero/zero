use std::collections::BTreeMap;

use anyhow::bail;
use jsonschema::Validator;
use log::warn;

use crate::api_model::{GraphqlPath, Setter, TopicDef};
use crate::topic_map::TopicMap;

/// One level of a Spec's tree: the nodes under one branch, by field name.
pub type Tree = BTreeMap<String, PathNode>;

/// A node in the tree of one Spec
#[derive(Debug, Clone)]
pub enum PathNode {
    Branch(Tree),
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

/// Place every queryable and settable Topic of one Spec at its GraphQL path.
///
/// Receive topic `<state><set_suffix>` becomes the [`Setter`] of the Send
/// topic `<state>`, matched exactly by MQTT topic. A Receive topic without
/// the suffix sets the Send topic on its own MQTT topic. A Receive topic
/// without a Send topic stays a leaf of its own, at the path of its topic
/// minus the suffix. A Receive topic without a validator is left out.
/// Errors on a topic without a GraphQL path, on a Path conflict, or on two
/// Receive topics setting the same Send topic.
pub(super) fn tree(
    topics: Vec<TopicDef>,
    validators: &TopicMap<Validator>,
    set_suffix: &str,
) -> anyhow::Result<Tree> {
    let (receives, sends): (Vec<_>, Vec<_>) = topics.into_iter().partition(TopicDef::is_settable);
    let mut root = Tree::new();
    for send in sends.into_iter().filter(TopicDef::is_queryable) {
        let path = GraphqlPath::from_address(&send.topic)?;
        insert_topic(&mut root, path.segments(), send)?;
    }

    // Send topics are all in place, so a Receive topic finds its State topic
    // at its own GraphQL path.
    for receive in receives {
        let (Some(validator), Some(payload)) = (
            validators.get_exact(&receive.topic),
            receive.payload.clone(),
        ) else {
            warn!(
                "Receive Topic '{}' has no JSON Schema validator, leaving it out of Mutation",
                receive.topic
            );
            continue;
        };
        let setter = Box::new(Setter {
            topic: receive.topic.clone(),
            payload,
            validator: validator.clone(),
        });
        let address = receive
            .topic
            .strip_suffix(set_suffix)
            .unwrap_or(&receive.topic);
        let path = GraphqlPath::from_address(address)?;
        match topic_at_mut(&mut root, path.segments()) {
            // The path alone is not enough: `a/b_c` and `a/b-c` share one.
            Some(state) if state.topic == address && state.is_state() => {
                // Two Receive operations on one channel, for example.
                if let Some(other) = &state.setter {
                    bail!(
                        "Receive topics '{}' and '{}' both set '{address}'",
                        other.topic,
                        setter.topic
                    );
                }
                state.setter = Some(setter);
            }
            _ => {
                let leaf = TopicDef {
                    setter: Some(setter),
                    ..receive
                };
                insert_topic(&mut root, path.segments(), leaf)?;
            }
        }
    }
    Ok(root)
}

/// The Topic at `path`, if there is one.
fn topic_at_mut<'t>(tree: &'t mut Tree, path: &[impl AsRef<str>]) -> Option<&'t mut TopicDef> {
    let (last, branches) = path.split_last()?;
    let mut level = tree;
    for segment in branches {
        match level.get_mut(segment.as_ref())? {
            PathNode::Branch(children) => level = children,
            PathNode::Topic(_) => return None,
        }
    }
    match level.get_mut(last.as_ref())? {
        PathNode::Topic(topic) => Some(topic),
        PathNode::Branch(_) => None,
    }
}

/// Insert a Topic at the `remaining` part of its GraphQL path.
fn insert_topic(
    node: &mut Tree,
    remaining: &[impl AsRef<str>],
    topic: TopicDef,
) -> anyhow::Result<()> {
    let Some((segment, rest)) = remaining.split_first() else {
        return Ok(());
    };
    let segment = segment.as_ref();

    if rest.is_empty() {
        if let Some(branch) = node.get(segment) {
            return tree_conflict(&topic.topic, branch.first_topic());
        }
        node.insert(segment.to_string(), PathNode::Topic(topic));
        return Ok(());
    }

    let child = node
        .entry(segment.to_string())
        .or_insert_with(|| PathNode::Branch(Tree::new()));

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
    use crate::api_model::{Direction, FieldType, Payload, TopicKind};

    /// Helper for a Send Topic with one Float field.
    fn mock_topic(topic: &str, field: &str) -> TopicDef {
        TopicDef {
            topic: topic.to_string(),
            payload: Some(Payload {
                name: format!("{field}payload"),
                fields: BTreeMap::from_iter(vec![(field.to_string(), FieldType::Float)]),
            }),
            operation: Direction::Send,
            ttl_secs: None,
            setter: None,
            kind: TopicKind::Single,
        }
    }

    /// Helper for a Receive Topic with one Float field.
    fn mock_receive(topic: &str) -> TopicDef {
        TopicDef {
            operation: Direction::Receive,
            ..mock_topic(topic, "x")
        }
    }

    /// An accept-anything validator for each of `topics`.
    fn validators(topics: &[&str]) -> TopicMap<Validator> {
        topics
            .iter()
            .map(|&topic| {
                let validator = jsonschema::validator_for(&serde_json::json!({})).unwrap();
                (topic.to_string(), validator)
            })
            .collect()
    }

    /// The tree of `topics`, with `/set` as suffix and a validator for every
    /// topic.
    fn tree_of(topics: Vec<TopicDef>) -> anyhow::Result<Tree> {
        let names: Vec<String> = topics.iter().map(|t| t.topic.clone()).collect();
        let names: Vec<&str> = names.iter().map(String::as_str).collect();
        tree(topics, &validators(&names), "/set")
    }

    /// The MQTT topic a client sets the Topic at `path` through.
    fn setter_at<'t>(tree: &'t mut Tree, path: &[&str]) -> Option<&'t str> {
        let topic = topic_at_mut(tree, path).unwrap();
        topic.setter.as_ref().map(|setter| setter.topic.as_str())
    }

    #[test_log::test]
    fn test_topics_on_the_same_graphql_path_conflict() {
        // `b-c` and `b_c` both sanitize to `bC`.
        let topics = vec![mock_topic("a/b-c", "x"), mock_topic("a/b_c", "y")];

        let err = tree_of(topics).unwrap_err();
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
            let err = tree_of(topics).unwrap_err();
            assert_eq!(
                err.to_string(),
                "GraphQL path conflict: topic 'a/b' conflicts with topic 'a/b/c'"
            );
        }
    }

    #[test_log::test]
    fn test_receive_topic_sets_the_send_topic_without_its_suffix() {
        let topics = vec![
            mock_topic("a/b", "x"),
            mock_receive("a/b/set"),
            mock_receive("a/c/set"),
            mock_receive("a/d"),
        ];
        let mut tree = tree_of(topics).unwrap();

        let paired = topic_at_mut(&mut tree, &["a", "b"]).unwrap();
        assert_eq!(paired.topic, "a/b");
        assert_eq!(paired.operation, Direction::Send);
        assert_eq!(setter_at(&mut tree, &["a", "b"]), Some("a/b/set"));

        // Without a Send topic, a Receive topic is a leaf of its own.
        let unpaired = topic_at_mut(&mut tree, &["a", "c"]).unwrap();
        assert_eq!(unpaired.operation, Direction::Receive);
        assert_eq!(setter_at(&mut tree, &["a", "c"]), Some("a/c/set"));
        assert_eq!(setter_at(&mut tree, &["a", "d"]), Some("a/d"));
    }

    #[test_log::test]
    fn test_receive_topic_without_suffix_sets_the_send_topic_on_its_own_topic() {
        let topics = vec![mock_topic("a/b", "x"), mock_receive("a/b")];
        let mut tree = tree_of(topics).unwrap();

        let paired = topic_at_mut(&mut tree, &["a", "b"]).unwrap();
        assert_eq!(paired.operation, Direction::Send);
        assert_eq!(setter_at(&mut tree, &["a", "b"]), Some("a/b"));
    }

    #[test_log::test]
    fn test_two_receive_topics_setting_one_send_topic_error() {
        // Two Receive operations on one channel, and two channels that both
        // set `a/b`.
        for (first, second) in [("a/b/set", "a/b/set"), ("a/b/set", "a/b")] {
            let topics = vec![
                mock_topic("a/b", "x"),
                mock_receive(first),
                mock_receive(second),
            ];

            let err = tree_of(topics).unwrap_err();
            assert_eq!(
                err.to_string(),
                format!("Receive topics '{first}' and '{second}' both set 'a/b'")
            );
        }
    }

    #[test_log::test]
    fn test_pairing_matches_topics_not_graphql_paths() {
        // `a/b_c` and `a/b-c` share the GraphQL path `a.bC` but are different
        // topics: no pairing, so the two leaves conflict.
        let topics = vec![mock_topic("a/b_c", "x"), mock_receive("a/b-c/set")];

        let err = tree_of(topics).unwrap_err();
        assert_eq!(
            err.to_string(),
            "GraphQL path conflict: topic 'a/b-c/set' conflicts with topic 'a/b_c'"
        );
    }

    #[test_log::test]
    fn test_unpaired_receive_topic_on_a_send_branch_conflicts() {
        let topics = vec![mock_topic("a/b/c", "x"), mock_receive("a/b/set")];

        let err = tree_of(topics).unwrap_err();
        assert_eq!(
            err.to_string(),
            "GraphQL path conflict: topic 'a/b/set' conflicts with topic 'a/b/c'"
        );
    }

    #[test_log::test]
    fn test_pairing_follows_the_given_suffix() {
        let topics = vec![mock_topic("a/b", "x"), mock_receive("a/b/cmd")];
        let mut tree = tree(topics, &validators(&["a/b/cmd"]), "/cmd").unwrap();

        assert_eq!(setter_at(&mut tree, &["a", "b"]), Some("a/b/cmd"));
    }

    #[test_log::test]
    fn test_receive_topic_without_payload_fields_is_settable() {
        let mut pause = mock_receive("a/pause");
        pause.payload = Some(Payload {
            name: "PauseMessage".to_string(),
            fields: BTreeMap::new(),
        });
        let mut tree = tree_of(vec![mock_topic("a/b", "x"), pause]).unwrap();

        assert_eq!(setter_at(&mut tree, &["a", "pause"]), Some("a/pause"));
    }

    #[test_log::test]
    fn test_receive_topic_without_validator_is_left_out() {
        let topics = vec![mock_topic("a/b", "x"), mock_receive("a/b/set")];
        let mut tree = tree(topics, &TopicMap::new(), "/set").unwrap();

        assert_eq!(setter_at(&mut tree, &["a", "b"]), None);
    }

    #[test_log::test]
    fn test_receive_topic_does_not_borrow_a_wildcard_validator() {
        let topics = vec![mock_topic("a/b", "x"), mock_receive("a/b/set")];
        // A Send topic's `a/#` validator matches `a/b/set`, but is not its own.
        let mut tree = tree(topics, &validators(&["a/#"]), "/set").unwrap();

        assert_eq!(setter_at(&mut tree, &["a", "b"]), None);
    }

    #[test_log::test]
    fn test_address_empty_errors() {
        for address in ["//", ""] {
            let err = tree_of(vec![mock_topic(address, "v")]).unwrap_err();
            assert_eq!(
                err.to_string(),
                format!("topic '{address}' would result in an empty GraphQL name")
            );
        }
    }
}
