# MQTT GraphQL bridge

Exposes the data that services publish over MQTT as a GraphQL API, derived from the services' AsyncAPI specs.

## Language

**Spec**:
One AsyncAPI document describing a single publishing service, written from that service's point of view.
_Avoid_: Schema (reserved for GraphQL and JSON Schema), API definition

**Send operation**:
An operation in a Spec through which the service publishes data; the source of everything readable through Query.
_Avoid_: Publish, subscribe operation

**Receive operation**:
An operation in a Spec through which the service accepts input from others; the future source of Mutation.
_Avoid_: Command topic, set topic

**Query tree**:
The nested, read-only part of the GraphQL API built from Send operations.
_Avoid_: Flat schema, topic fields

**Topic**:
An operation on a single, fixed MQTT topic: as a Send operation readable as one current value, as a Receive operation writable as one input.
In code, Topics and Groups are both a `TopicDef`, told apart by its `TopicKind`.
_Avoid_: Channel, field, leaf

**Group**:
An operation whose address is parametrized, standing for a large number of MQTT topics that share one payload format and are handled together as a collection rather than one by one.
_Avoid_: Topic group, parametrized topic, wildcard topic

**Member**:
One concrete MQTT topic belonging to a Group, carrying its own static metadata and its own current value.
_Avoid_: Row, item, group topic

**Bucket**:
A partition of a Group's Members by the value of one of their static metadata attributes.
_Avoid_: Panel, category, grouping

**GraphQL path**:
The chain of fields from the root of the Query or Mutation tree to a Topic or Group, derived from its MQTT address; a `{param}` segment marks a Group level. Payload fields inside a Topic or Group are not part of it.
_Avoid_: Operation path, field path, topic name

**Leaf**:
The end of a GraphQL path, where a Topic or Group sits and its tree stops branching. Each tree builds its fields leaf by leaf: at a Query leaf to read the Topic or Group, at a Mutation leaf to set the Topic. A Leaf is a place in a tree, not the Topic in it.
_Avoid_: Node, endpoint

**Mount**:
A replacement of a leading part of every GraphQL path in one Spec by another path, placing that Spec in the combined tree; replacing nothing by a base path only prepends, and no Mount leaves the paths unchanged.
_Avoid_: Prefix, namespace

**Path conflict**:
Two operations claiming the same GraphQL path, or one path being both a value and a parent of other paths.
_Avoid_: Collision, duplicate

**State topic**:
The Send Topic whose MQTT topic is a Receive Topic's minus the Spec's set suffix (`/set`), or, for a Receive Topic without the suffix, the Send Topic on the same MQTT topic. Through it the service reports the state that Receive Topic sets. Every Receive Topic is expected to have one, but may have none.
_Avoid_: Echo topic, feedback topic, status topic

**Setter**:
The Receive Topic through which a client sets a Topic: for a State topic, the Receive Topic paired with it; for a Receive Topic without a State topic, that Topic itself. Every Leaf of the Mutation tree has one, but the tree as a whole is not "the setters".
In code, `TopicDef.setter`.
_Avoid_: Set topic, command topic

**Mutation tree**:
The nested, write part of the GraphQL API built from Receive operations, laid out by the same rules as the Query tree.
_Avoid_: Commands, setters
