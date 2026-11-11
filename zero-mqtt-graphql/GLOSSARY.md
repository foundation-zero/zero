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
A Send operation on a single, fixed MQTT topic, readable as one current value.
In code, Topics and Groups are both a `TopicDef`, told apart by its `TopicKind`.
_Avoid_: Channel, field, leaf

**Group**:
A Send operation whose address is parametrized, standing for a large number of MQTT topics that share one payload format and are read together as a collection rather than one by one.
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

**Mount**:
A replacement of a leading part of every GraphQL path in one Spec by another path, placing that Spec in the combined tree; replacing nothing by a base path only prepends, and no Mount leaves the paths unchanged.
_Avoid_: Prefix, namespace

**Path conflict**:
Two operations claiming the same GraphQL path, or one path being both a value and a parent of other paths.
_Avoid_: Collision, duplicate

**Mutation tree**:
The nested, write part of the GraphQL API built from Receive operations, laid out by the same rules as the Query tree.
_Avoid_: Commands, setters
