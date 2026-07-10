import { gql } from "@urql/vue";
import { mutationResponse } from ".";

export const BlindsFragment = gql`
  fragment BlindsItem on DomesticBlinds {
    id
    name
    level
    roomId
    opacity
    group
  }
`;

export const setBlindsLevelMutation = gql`
  mutation SetBlindsLevel($ids: [ID!]!, $level: Float!) {
    setBlinds: domesticSetBlinds(ids: $ids, level: $level) {
      ...MutationResponse
    }
  }

  ${mutationResponse}
`;
