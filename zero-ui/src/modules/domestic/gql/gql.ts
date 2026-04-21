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
type Documents = {
    "\n  query GetVersion {\n    version: domesticVersion\n  }\n": typeof types.GetVersionDocument,
    "\n  fragment BlindsItem on DomesticBlinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n": typeof types.BlindsItemFragmentDoc,
    "\n  mutation SetBlindsLevel($ids: [ID!]!, $level: Float!) {\n    setBlinds: domesticSetBlinds(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetBlindsLevelDocument,
    "\n  query GetRoomAirConditioningLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      airConditioningLog(period: $period) {\n        timestamp\n        actualTemperature\n        temperatureSetpoint\n        actualHumidity\n        humiditySetpoint\n      }\n    }\n  }\n": typeof types.GetRoomAirConditioningLogDocument,
    "\n  query GetRoomVentilationLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      ventilationLog(period: $period) {\n        timestamp\n        actualCo2\n        co2Setpoint\n      }\n    }\n  }\n": typeof types.GetRoomVentilationLogDocument,
    "\n  fragment MutationResponse on MutationResponse {\n    code\n    success\n    message\n  }\n": typeof types.MutationResponseFragmentDoc,
    "\n  fragment LightGroupItem on DomesticLightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n": typeof types.LightGroupItemFragmentDoc,
    "\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups: domesticLightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n": typeof types.GetLightGroupsByRoomDocument,
    "\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup: domesticSetLightingGroups(ids: [$id], level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetLightLevelDocument,
    "\n  mutation SetGroupLightLevel($ids: [ID!]!, $level: Float!) {\n    setLightingGroups: domesticSetLightingGroups(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetGroupLightLevelDocument,
    "\n  fragment RoomItem on DomesticRooms {\n    id\n    name\n    group\n    lightingGroups(orderBy: { id: ASC }) {\n      id\n      name\n      level\n    }\n    blinds(orderBy: { id: ASC }) {\n      id\n      name\n      level\n      opacity\n      group\n    }\n    airConditioning {\n      temperatureSetpoint\n      humiditySetpoint\n      actualTemperature\n      actualHumidity\n    }\n    ventilation {\n      co2Setpoint\n      actualCo2\n    }\n    amplifier {\n      on\n    }\n  }\n": typeof types.RoomItemFragmentDoc,
    "\n  query GetAllRooms {\n    rooms: domesticRooms {\n      id\n      name\n      group\n    }\n  }\n": typeof types.GetAllRoomsDocument,
    "\n  subscription SubscribeToRoom($roomId: String!) {\n    domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n": typeof types.SubscribeToRoomDocument,
    "\n  subscription SubscribeToRooms {\n    rooms: domesticRooms {\n      ...RoomItem\n    }\n  }\n\n  \n": typeof types.SubscribeToRoomsDocument,
    "\n  query GetRoomById($roomId: String!) {\n    rooms: domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n": typeof types.GetRoomByIdDocument,
    "\n  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {\n    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(\n      ids: $ids\n      temperature: $temperature\n    ) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetTemperatureSetpointForRoomDocument,
    "\n  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {\n    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetAmplifierDocument,
    "\n  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {\n    setRoomHumiditySetpoints: domesticSetRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetRoomHumiditySetpointsDocument,
    "\n  mutation SetRoomCo2Setpoints($ids: [ID!]!, $co2: Float!) {\n    setRoomCo2Setpoints: domesticSetRoomCo2Setpoints(ids: $ids, co2: $co2) {\n      ...MutationResponse\n    }\n  }\n\n  \n": typeof types.SetRoomCo2SetpointsDocument,
};
const documents: Documents = {
    "\n  query GetVersion {\n    version: domesticVersion\n  }\n": types.GetVersionDocument,
    "\n  fragment BlindsItem on DomesticBlinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n": types.BlindsItemFragmentDoc,
    "\n  mutation SetBlindsLevel($ids: [ID!]!, $level: Float!) {\n    setBlinds: domesticSetBlinds(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetBlindsLevelDocument,
    "\n  query GetRoomAirConditioningLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      airConditioningLog(period: $period) {\n        timestamp\n        actualTemperature\n        temperatureSetpoint\n        actualHumidity\n        humiditySetpoint\n      }\n    }\n  }\n": types.GetRoomAirConditioningLogDocument,
    "\n  query GetRoomVentilationLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      ventilationLog(period: $period) {\n        timestamp\n        actualCo2\n        co2Setpoint\n      }\n    }\n  }\n": types.GetRoomVentilationLogDocument,
    "\n  fragment MutationResponse on MutationResponse {\n    code\n    success\n    message\n  }\n": types.MutationResponseFragmentDoc,
    "\n  fragment LightGroupItem on DomesticLightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n": types.LightGroupItemFragmentDoc,
    "\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups: domesticLightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n": types.GetLightGroupsByRoomDocument,
    "\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup: domesticSetLightingGroups(ids: [$id], level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetLightLevelDocument,
    "\n  mutation SetGroupLightLevel($ids: [ID!]!, $level: Float!) {\n    setLightingGroups: domesticSetLightingGroups(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetGroupLightLevelDocument,
    "\n  fragment RoomItem on DomesticRooms {\n    id\n    name\n    group\n    lightingGroups(orderBy: { id: ASC }) {\n      id\n      name\n      level\n    }\n    blinds(orderBy: { id: ASC }) {\n      id\n      name\n      level\n      opacity\n      group\n    }\n    airConditioning {\n      temperatureSetpoint\n      humiditySetpoint\n      actualTemperature\n      actualHumidity\n    }\n    ventilation {\n      co2Setpoint\n      actualCo2\n    }\n    amplifier {\n      on\n    }\n  }\n": types.RoomItemFragmentDoc,
    "\n  query GetAllRooms {\n    rooms: domesticRooms {\n      id\n      name\n      group\n    }\n  }\n": types.GetAllRoomsDocument,
    "\n  subscription SubscribeToRoom($roomId: String!) {\n    domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n": types.SubscribeToRoomDocument,
    "\n  subscription SubscribeToRooms {\n    rooms: domesticRooms {\n      ...RoomItem\n    }\n  }\n\n  \n": types.SubscribeToRoomsDocument,
    "\n  query GetRoomById($roomId: String!) {\n    rooms: domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n": types.GetRoomByIdDocument,
    "\n  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {\n    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(\n      ids: $ids\n      temperature: $temperature\n    ) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetTemperatureSetpointForRoomDocument,
    "\n  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {\n    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetAmplifierDocument,
    "\n  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {\n    setRoomHumiditySetpoints: domesticSetRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetRoomHumiditySetpointsDocument,
    "\n  mutation SetRoomCo2Setpoints($ids: [ID!]!, $co2: Float!) {\n    setRoomCo2Setpoints: domesticSetRoomCo2Setpoints(ids: $ids, co2: $co2) {\n      ...MutationResponse\n    }\n  }\n\n  \n": types.SetRoomCo2SetpointsDocument,
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
export function graphql(source: "\n  query GetVersion {\n    version: domesticVersion\n  }\n"): (typeof documents)["\n  query GetVersion {\n    version: domesticVersion\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment BlindsItem on DomesticBlinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n"): (typeof documents)["\n  fragment BlindsItem on DomesticBlinds {\n    id\n    name\n    level\n    roomId\n    opacity\n    group\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetBlindsLevel($ids: [ID!]!, $level: Float!) {\n    setBlinds: domesticSetBlinds(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetBlindsLevel($ids: [ID!]!, $level: Float!) {\n    setBlinds: domesticSetBlinds(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetRoomAirConditioningLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      airConditioningLog(period: $period) {\n        timestamp\n        actualTemperature\n        temperatureSetpoint\n        actualHumidity\n        humiditySetpoint\n      }\n    }\n  }\n"): (typeof documents)["\n  query GetRoomAirConditioningLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      airConditioningLog(period: $period) {\n        timestamp\n        actualTemperature\n        temperatureSetpoint\n        actualHumidity\n        humiditySetpoint\n      }\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetRoomVentilationLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      ventilationLog(period: $period) {\n        timestamp\n        actualCo2\n        co2Setpoint\n      }\n    }\n  }\n"): (typeof documents)["\n  query GetRoomVentilationLog($period: TimePeriod!) {\n    rooms: domesticRooms {\n      id\n      name\n      ventilationLog(period: $period) {\n        timestamp\n        actualCo2\n        co2Setpoint\n      }\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment MutationResponse on MutationResponse {\n    code\n    success\n    message\n  }\n"): (typeof documents)["\n  fragment MutationResponse on MutationResponse {\n    code\n    success\n    message\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment LightGroupItem on DomesticLightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n"): (typeof documents)["\n  fragment LightGroupItem on DomesticLightingGroups {\n    id\n    name\n    level\n    roomId\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups: domesticLightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  subscription GetLightGroupsByRoom($roomId: String!) {\n    lightingGroups: domesticLightingGroups(where: { roomId: { _eq: $roomId } }) {\n      ...LightGroupItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup: domesticSetLightingGroups(ids: [$id], level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetLightLevel($id: ID!, $level: Float!) {\n    setLightingGroup: domesticSetLightingGroups(ids: [$id], level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetGroupLightLevel($ids: [ID!]!, $level: Float!) {\n    setLightingGroups: domesticSetLightingGroups(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetGroupLightLevel($ids: [ID!]!, $level: Float!) {\n    setLightingGroups: domesticSetLightingGroups(ids: $ids, level: $level) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  fragment RoomItem on DomesticRooms {\n    id\n    name\n    group\n    lightingGroups(orderBy: { id: ASC }) {\n      id\n      name\n      level\n    }\n    blinds(orderBy: { id: ASC }) {\n      id\n      name\n      level\n      opacity\n      group\n    }\n    airConditioning {\n      temperatureSetpoint\n      humiditySetpoint\n      actualTemperature\n      actualHumidity\n    }\n    ventilation {\n      co2Setpoint\n      actualCo2\n    }\n    amplifier {\n      on\n    }\n  }\n"): (typeof documents)["\n  fragment RoomItem on DomesticRooms {\n    id\n    name\n    group\n    lightingGroups(orderBy: { id: ASC }) {\n      id\n      name\n      level\n    }\n    blinds(orderBy: { id: ASC }) {\n      id\n      name\n      level\n      opacity\n      group\n    }\n    airConditioning {\n      temperatureSetpoint\n      humiditySetpoint\n      actualTemperature\n      actualHumidity\n    }\n    ventilation {\n      co2Setpoint\n      actualCo2\n    }\n    amplifier {\n      on\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetAllRooms {\n    rooms: domesticRooms {\n      id\n      name\n      group\n    }\n  }\n"): (typeof documents)["\n  query GetAllRooms {\n    rooms: domesticRooms {\n      id\n      name\n      group\n    }\n  }\n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  subscription SubscribeToRoom($roomId: String!) {\n    domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  subscription SubscribeToRoom($roomId: String!) {\n    domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  subscription SubscribeToRooms {\n    rooms: domesticRooms {\n      ...RoomItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  subscription SubscribeToRooms {\n    rooms: domesticRooms {\n      ...RoomItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  query GetRoomById($roomId: String!) {\n    rooms: domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n"): (typeof documents)["\n  query GetRoomById($roomId: String!) {\n    rooms: domesticRooms(where: { id: { _eq: $roomId } }) {\n      ...RoomItem\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {\n    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(\n      ids: $ids\n      temperature: $temperature\n    ) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {\n    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(\n      ids: $ids\n      temperature: $temperature\n    ) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {\n    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {\n    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {\n    setRoomHumiditySetpoints: domesticSetRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {\n    setRoomHumiditySetpoints: domesticSetRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];
/**
 * The graphql function is used to parse GraphQL queries into a document that can be used by GraphQL clients.
 */
export function graphql(source: "\n  mutation SetRoomCo2Setpoints($ids: [ID!]!, $co2: Float!) {\n    setRoomCo2Setpoints: domesticSetRoomCo2Setpoints(ids: $ids, co2: $co2) {\n      ...MutationResponse\n    }\n  }\n\n  \n"): (typeof documents)["\n  mutation SetRoomCo2Setpoints($ids: [ID!]!, $co2: Float!) {\n    setRoomCo2Setpoints: domesticSetRoomCo2Setpoints(ids: $ids, co2: $co2) {\n      ...MutationResponse\n    }\n  }\n\n  \n"];

export function graphql(source: string) {
  return (documents as any)[source] ?? {};
}

export type DocumentType<TDocumentNode extends DocumentNode<any, any>> = TDocumentNode extends DocumentNode<  infer TType,  any>  ? TType  : never;