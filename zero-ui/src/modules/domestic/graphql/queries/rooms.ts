import { gql } from "@urql/vue";
import { mutationResponse } from ".";
import { LightGroupFragment } from "./light-groups";

export const RoomFragment = gql`
  fragment RoomItem on Rooms {
    id
    name
    group
    roomsControls {
      id
      type
      value
      time
      name
    }
    roomsSensors {
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
    rooms {
      id
      name
      group
      roomsControls {
        id
        type
        value
        time
        name
      }
      roomsSensors {
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
    rooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const subscribeToRooms = gql`
  subscription SubscribeToRoom {
    rooms {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const getRoomById = gql`
  query GetRoomById($roomId: String!) {
    rooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;

export const setTemperatureSetpointMutation = gql`
  mutation SetTemperatureSetpointForRoom($temperature: Float!) {
    setRoomTemperatureSetpoints(temperature: $temperature) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setTemperatureSetpointForRoomMutation = gql`
  mutation SetTemperatureSetpointForRoom($ids: [ID!]!, $temperature: Float!) {
    setRoomTemperatureSetpoints(ids: $ids, temperature: $temperature) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setAmplifierMutation = gql`
  mutation SetAmplifier($on: Boolean!) {
    setAmplifiers(on: $on) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setAmplifierForRoomMutation = gql`
  mutation SetAmplifier($ids: [ID!]!, $on: Boolean!) {
    setAmplifiers(ids: $ids, on: $on) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setHumiditySetpointMutation = gql`
  mutation SetRoomHumiditySetpoints($ids: [ID!]!, $humidity: Float!) {
    setRoomHumiditySetpoints(ids: $ids, humidity: $humidity) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setCO2SetpointMutation = gql`
  mutation SetRoomCo2Setpoint($ids: [ID!]!, $co2: Float!) {
    setRoomCo2Setpoint(ids: $ids, co2: $co2) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;
