use crate::naming::sanitize_to_graphql_name;

/// A GraphQL path: the chain of field names from the root of the Query or
/// Mutation tree to a branch or Topic, written as `marpower.freshWater.cold`.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct GraphqlPath(Vec<String>);

impl GraphqlPath {
    /// The GraphQL path of a Topic or Group: its MQTT address split on `/`, each
    /// level sanitized to a GraphQL name. Skips segments that have no usable
    /// name, such as the empty levels in `/a` or `a//b` and wildcards.
    /// Errors when path is empty.
    pub fn from_address(address: &str) -> anyhow::Result<Self> {
        let segments: Vec<String> = address
            .split('/')
            .take_while(|&s| s != "#" && s != "+")
            .map(sanitize_to_graphql_name)
            .filter(|s| !s.is_empty())
            .collect();
        if segments.is_empty() {
            anyhow::bail!("topic '{address}' would result in an empty GraphQL name");
        }
        Ok(Self(segments))
    }

    #[must_use]
    pub fn segments(&self) -> &[String] {
        &self.0
    }

    /// This path extended by one field.
    #[must_use]
    pub fn child(&self, segment: &str) -> Self {
        let mut segments = self.0.clone();
        segments.push(segment.to_string());
        Self(segments)
    }
}

impl std::fmt::Display for GraphqlPath {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0.join("."))
    }
}
