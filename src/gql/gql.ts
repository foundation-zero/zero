/* eslint-disable */
import * as types from './graphql';
import type { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';

/**
 * Map of all GraphQL operations in the project.
 *
 * This map has several performance disadvantages:
 * 1. It is not tree-shakeable, so it will include all operations in the project.
 * 2. It is not minifiable, so the string of a GraphQL query will be multiple times inside the bundle.
 * 3. It does not support dead code elimination, so it will add unused operations.
 *
 * Therefore it is highly recommended to use the babel or swc plugin for production.
 * Learn more about it here: https://the-guild.dev/graphql/codegen/plugins/presets/preset-client#reducing-bundle-size
 */
const documents = {
    "\n  fragment BlindsItem on blinds {\n    id\n    name\n    level\n    room_id\n    opacity\n    group\n  }\n": types.BlindsItemFragmentDoc,
    "\n  query GetBlindsByRoom($roomId: String!) {\n    blinds(where: { room_id: { _eq: $roomId } }) {\n      ...BlindsItem\n    }\n  }\n\n  \n": types.GetBlindsByRoomDocument,
    "\n  fragment LightGroupItem on lighting_groups {\n    id\n    name\n    level\n    room_id\n  }\n": types.LightGroupItemFragmentDoc,
    "\n  query GetLightGroupsByRoom($roomId: String!) {\n    lighting_groups(where: { room_id: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n": types.GetLightGroupsByRoomDocument,
    "\n  fragment RoomItem on rooms {\n    id\n    amplifier_on\n    actual_temperature\n    actual_humidity\n    temperature_setpoint\n    thermal_comfort_index\n    name\n    group\n    last_movement\n    blinds {\n      ...BlindsItem\n    }\n    lighting_groups {\n      ...LightGroupItem\n    }\n\n    \n    \n  }\n": types.RoomItemFragmentDoc,
    "\n  query GetAllRooms {\n    rooms {\n      ...RoomItem\n    }\n  }\n\n  \n": types.GetAllRoomsDocument,
};

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 *
 *
 * @example
 * ```ts
 * const query = graphql(`query GetUser($id: ID!) { user(id: $id) { name } }`);
 * ```
 *
 * The query argument is unknown!
 * Please regenerate the types.
 */
export function graphql(source: string): unknown;

/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment BlindsItem on blinds {\n    id\n    name\n    level\n    room_id\n    opacity\n    group\n  }\n"): (typeof documents)["\n  fragment BlindsItem on blinds {\n    id\n    name\n    level\n    room_id\n    opacity\n    group\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetBlindsByRoom($roomId: String!) {\n    blinds(where: { room_id: { _eq: $roomId } }) {\n      ...BlindsItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  query GetBlindsByRoom($roomId: String!) {\n    blinds(where: { room_id: { _eq: $roomId } }) {\n      ...BlindsItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment LightGroupItem on lighting_groups {\n    id\n    name\n    level\n    room_id\n  }\n"): (typeof documents)["\n  fragment LightGroupItem on lighting_groups {\n    id\n    name\n    level\n    room_id\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetLightGroupsByRoom($roomId: String!) {\n    lighting_groups(where: { room_id: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  query GetLightGroupsByRoom($roomId: String!) {\n    lighting_groups(where: { room_id: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment RoomItem on rooms {\n    id\n    amplifier_on\n    actual_temperature\n    actual_humidity\n    temperature_setpoint\n    thermal_comfort_index\n    name\n    group\n    last_movement\n    blinds {\n      ...BlindsItem\n    }\n    lighting_groups {\n      ...LightGroupItem\n    }\n\n    \n    \n  }\n"): (typeof documents)["\n  fragment RoomItem on rooms {\n    id\n    amplifier_on\n    actual_temperature\n    actual_humidity\n    temperature_setpoint\n    thermal_comfort_index\n    name\n    group\n    last_movement\n    blinds {\n      ...BlindsItem\n    }\n    lighting_groups {\n      ...LightGroupItem\n    }\n\n    \n    \n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetAllRooms {\n    rooms {\n      ...RoomItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  query GetAllRooms {\n    rooms {\n      ...RoomItem\n    }\n  }\n\n  \n"];

export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> = TDocumentNode extends DocumentNode<  infer TType,  any>  ? TType  : never;