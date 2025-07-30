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
    "\n  fragment BlindsItem on Blinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n": types.BlindsItemFragmentDoc,
    "\n  mutation SetBlindsLevel($id: ID!, $level: Float!) {\n    setBlind(id: $id, level: $level)\n  }\n": types.SetBlindsLevelDocument,
    "\n  fragment LightGroupItem on LightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n": types.LightGroupItemFragmentDoc,
    "\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n": types.GetLightGroupsByRoomDocument,
    "\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup(id: $id, level: $level)\n  }\n": types.SetLightLevelDocument,
    "\n  fragment RoomItem on Rooms {\n    id\n    amplifierOn\n    actualTemperature\n    actualHumidity\n    temperatureSetpoint\n    thermalComfortIndex\n    name\n    group\n    lastMovement\n  }\n": types.RoomItemFragmentDoc,
    "\n  query GetAllRooms {\n    rooms {\n      id\n      name\n      group\n    }\n  }\n": types.GetAllRoomsDocument,
    "\n  subscription SubscribeToRoom($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n": types.SubscribeToRoomDocument,
    "\n  query GetRoomById($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n": types.GetRoomByIdDocument,
    "\n  mutation SetTemperatureSetpoint($id: ID!, $temperature: Int!) {\n    setRoomTemperatureSetpoint(id: $id, temperature: $temperature)\n  }\n": types.SetTemperatureSetpointDocument,
    "\n  mutation SetAmplifier($id: ID!, $on: Boolean!) {\n    setAmplifier(id: $id, on: $on)\n  }\n": types.SetAmplifierDocument,
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
export function graphql(source: "\n  fragment BlindsItem on Blinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n"): (typeof documents)["\n  fragment BlindsItem on Blinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetBlindsLevel($id: ID!, $level: Float!) {\n    setBlind(id: $id, level: $level)\n  }\n"): (typeof documents)["\n  mutation SetBlindsLevel($id: ID!, $level: Float!) {\n    setBlind(id: $id, level: $level)\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment LightGroupItem on LightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n"): (typeof documents)["\n  fragment LightGroupItem on LightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup(id: $id, level: $level)\n  }\n"): (typeof documents)["\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup(id: $id, level: $level)\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment RoomItem on Rooms {\n    id\n    amplifierOn\n    actualTemperature\n    actualHumidity\n    temperatureSetpoint\n    thermalComfortIndex\n    name\n    group\n    lastMovement\n  }\n"): (typeof documents)["\n  fragment RoomItem on Rooms {\n    id\n    amplifierOn\n    actualTemperature\n    actualHumidity\n    temperatureSetpoint\n    thermalComfortIndex\n    name\n    group\n    lastMovement\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetAllRooms {\n    rooms {\n      id\n      name\n      group\n    }\n  }\n"): (typeof documents)["\n  query GetAllRooms {\n    rooms {\n      id\n      name\n      group\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  subscription SubscribeToRoom($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n"): (typeof documents)["\n  subscription SubscribeToRoom($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetRoomById($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n"): (typeof documents)["\n  query GetRoomById($roomId: String!) {\n    rooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n      blinds {\n        ...BlindsItem\n      }\n      lightingGroups {\n        ...LightGroupItem\n      }\n    }\n  }\n\n  \n  \n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetTemperatureSetpoint($id: ID!, $temperature: Int!) {\n    setRoomTemperatureSetpoint(id: $id, temperature: $temperature)\n  }\n"): (typeof documents)["\n  mutation SetTemperatureSetpoint($id: ID!, $temperature: Int!) {\n    setRoomTemperatureSetpoint(id: $id, temperature: $temperature)\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetAmplifier($id: ID!, $on: Boolean!) {\n    setAmplifier(id: $id, on: $on)\n  }\n"): (typeof documents)["\n  mutation SetAmplifier($id: ID!, $on: Boolean!) {\n    setAmplifier(id: $id, on: $on)\n  }\n"];

export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> = TDocumentNode extends DocumentNode<  infer TType,  any>  ? TType  : never;