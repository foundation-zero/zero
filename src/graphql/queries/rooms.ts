import { gql } from "@urql/vue";
import { BlindsFragment } from "./blinds";
import { LightGroupFragment } from "./light-groups";

export const RoomFragment = gql`
  fragment RoomItem on rooms {
    id
    amplifier_on
    actual_temperature
    actual_humidity
    temperature_setpoint
    thermal_comfort_index
    name
    group
    last_movement
    blinds {
      ...BlindsItem
    }
    lighting_groups {
      ...LightGroupItem
    }

    ${BlindsFragment}
    ${LightGroupFragment}
  }
`;

export const getAll = gql`
  query GetAllRooms {
    rooms {
      ...RoomItem
    }
  }

  ${RoomFragment}
`;
