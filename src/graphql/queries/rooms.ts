import { gql } from "@urql/vue";
import { BlindsFragment } from "./blinds";
import { LightGroupFragment } from "./light-groups";

export const RoomFragment = gql`
  fragment RoomItem on Rooms {
    id
    amplifierOn
    actualTemperature
    actualHumidity
    temperatureSetpoint
    thermalComfortIndex
    name
    group
    lastMovement
  }
`;

export const getAll = gql`
  query GetAllRooms {
    rooms {
      id
      name
      group
    }
  }
`;

export const subscribeToRoom = gql`
  subscription SubscribeToRoom($roomId: String!) {
    rooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
      blinds {
        ...BlindsItem
      }
      lightingGroups {
        ...LightGroupItem
      }
    }
  }

  ${RoomFragment}
  ${BlindsFragment}
  ${LightGroupFragment}
`;

export const getRoomById = gql`
  query GetRoomById($roomId: String!) {
    rooms(where: { id: { _eq: $roomId } }) {
      ...RoomItem
      blinds {
        ...BlindsItem
      }
      lightingGroups {
        ...LightGroupItem
      }
    }
  }

  ${RoomFragment}
  ${BlindsFragment}
  ${LightGroupFragment}
`;

export const setTemperatureSetpointMutation = gql`
  mutation SetTemperatureSetpointForRoom($temperature: Int!) {
    setRoomTemperatureSetpoint(temperature: $temperature)
  }
`;

export const setTemperatureSetpointForRoomMutation = gql`
  mutation SetTemperatureSetpointForRoom($id: ID!, $temperature: Int!) {
    setRoomTemperatureSetpoint(id: $id, temperature: $temperature)
  }
`;

export const setAmplifierMutation = gql`
  mutation SetAmplifier($on: Boolean!) {
    setAmplifier(on: $on)
  }
`;

export const setAmplifierForRoomMutation = gql`
  mutation SetAmplifier($id: ID!, $on: Boolean!) {
    setAmplifier(id: $id, on: $on)
  }
`;
