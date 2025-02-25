import { gql } from "@urql/vue";

export const LightGroupFragment = gql`
  fragment LightGroupItem on LightingGroups {
    id
    name
    level
    roomId
  }
`;

export const byRoomId = gql`
  subscription GetLightGroupsByRoom($roomId: String!) {
    lightingGroups(where: { roomId: { _eq: $roomId } }) {
      ...LightGroupItem
    }
  }

  ${LightGroupFragment}
`;

export const setLightLevelMutation = gql`
  mutation SetLightLevel($id: ID!, $level: Float!) {
    setLightingGroup(id: $id, level: $level)
  }
`;
