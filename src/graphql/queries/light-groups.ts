import { gql } from "@urql/vue";

export const LightGroupFragment = gql`
  fragment LightGroupItem on lighting_groups {
    id
    name
    level
    room_id
  }
`;

export const byRoomId = gql`
  query GetLightGroupsByRoom($roomId: String!) {
    lighting_groups(where: { room_id: { _eq: $roomId } }) {
      ...LightGroupItem
    }
  }

  ${LightGroupFragment}
`;
