import { gql } from "@urql/vue";
import { mutationResponse } from ".";
import { LightGroupFragment } from "./light-groups";

export const RoomFragment = gql`
  fragment RoomItem on DomesticRooms {
    id
    name
    group
    roomControls(orderBy: { id: ASC }) {
      id
      type
      value
      time
      name
    }
    roomSensors(orderBy: { id: ASC }) {
      id
      type
      value
      time
      name
    }
  }
`;

export const getAll = gql`
  query GetAllRooms {
    rooms: domesticRooms {
      id
      name
      group
      roomControls(orderBy: { id: ASC }) {
        id
        type
        value
        time
        name
      }
      roomSensors(orderBy: { id: ASC }) {
        id
        type
        value
        time
        name
      }
    }
  }

  ${LightGroupFragment}
`;

export const subscribeToRoom = gql`
  subscription SubscribeToRoom($roomId: String!) {
    domesticRooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const subscribeToRooms = gql`
  subscription SubscribeToRoom {
    rooms: domesticRooms {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const getRoomById = gql`
  query GetRoomById($roomId: String!) {
    rooms: domesticRooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const setTemperatureSetpointMutation = gql`
  mutation SetTemperatureSetpointForRoom($id: ID!, $temperature: Float!) {
    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(
      ids: [$id]
      temperature: $temperature
    ) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setTemperatureSetpointForRoomMutation = gql`
  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {
    setRoomTemperatureSetpoints: domesticSetRoomTemperatureSetpoints(
      ids: $ids
      temperature: $temperature
    ) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setAmplifierMutation = gql`
  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {
    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setAmplifierForRoomMutation = gql`
  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {
    setAmplifiers: domesticSetAmplifiers(ids: $ids, on: $on) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setHumiditySetpointMutation = gql`
  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {
    setRoomHumiditySetpoints: domesticSetRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setCO2SetpointMutation = gql`
  mutation SetRoomCo2Setpoint($ids: [ID!]!, $co2: Float!) {
    setRoomCo2Setpoint: domesticSetRoomCo2Setpoint(ids: $ids, co2: $co2) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;
