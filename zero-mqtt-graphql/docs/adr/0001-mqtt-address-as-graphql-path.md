# MQTT addresses define the GraphQL tree, with room for explicit paths later

The GraphQL API is nested to mirror the structure of the published data. Each operation's position in that tree (its GraphQL path) is derived from its channel's MQTT address: split on `/`, segments sanitized to GraphQL names, `{param}` segments marking Group levels, and the Spec's set suffix (`/set`) dropped for Receive operations because it is MQTT plumbing, not API shape. This works with today's Specs without generator changes.

## Considered Options

- **Address (chosen to start)**: no Spec changes needed; names are whatever the topics are (`_250000FreshWater`), and renaming a topic changes the API.
- **Address with a per-operation `x-graphql-path` override**: services opt into clean, topic-independent paths one at a time.
- **Operation name with a dot convention**: full control, but every generator must change first and the operation id gains a second, GraphQL-specific meaning.
- **Required `x-graphql-path` on every operation**: same control without overloading the operation id, same up-front generator cost.
- **Rewrite rules in bridge config**: no Spec changes, but the bridge must know every service's topic layout and silently drifts when topics change.

## Consequences

To keep the override option open, the GraphQL path is resolved once per operation into a list of segments, and everything after that (Mounts, merging, Path conflicts, type naming, Group detection) works only on that list, never on the address. An override for a Group will have to contain the same `{param}` names as its address, because parameters are matched by name. Addresses containing MQTT wildcards (`+`, `#`) cannot form a path and are left out of the tree.
