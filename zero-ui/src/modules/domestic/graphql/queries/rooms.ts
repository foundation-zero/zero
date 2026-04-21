import { gql } from "@urql/vue";
import { mutationResponse } from ".";

export const RoomFragment = gql`
  fragment RoomItem on DomesticRooms {
    id
    name
    group
    lightingGroups(orderBy: { id: ASC }) {
      id
      name
      level
    }
    blinds(orderBy: { id: ASC }) {
      id
      name
      level
      opacity
      group
    }
    airConditioning {
      temperatureSetpoint
      humiditySetpoint
      actualTemperature
      actualHumidity
    }
    ventilation {
      co2Setpoint
      actualCo2
    }
    amplifier {
      on
    }
  }
`;

export const getAll = gql`
  query GetAllRooms {
    rooms: domesticRooms {
      id
      name
      group
    }
  }
`;

export const subscribeToRooms = gql`
  subscription SubscribeToRooms {
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
  mutation SetRoomCo2Setpoints($ids: [ID!]!, $co2: Float!) {
    setRoomCo2Setpoints: domesticSetRoomCo2Setpoints(ids: $ids, co2: $co2) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;
