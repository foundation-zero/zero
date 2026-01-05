import { gql } from "@urql/vue";
import { mutationResponse } from ".";

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
    lightingGroups: domesticLightingGroups(where: { roomId: { _eq: $roomId } }) {
      ...LightGroupItem
    }
  }

  ${LightGroupFragment}
`;

export const setLightLevelMutation = gql`
  mutation SetLightLevel($id: ID!, $level: Float!) {
    setLightingGroup: domesticSetLightingGroups(id: $id, level: $level) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;

export const setLightingGroupsLevelMutation = gql`
  mutation SetGroupLightLevel($ids: [ID!]!, $level: Float!) {
    setLightingGroups: domesticSetLightingGroups(ids: $ids, level: $level) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;
