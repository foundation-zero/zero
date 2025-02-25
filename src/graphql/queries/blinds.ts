import { gql } from "@urql/vue";

export const BlindsFragment = gql`
  fragment BlindsItem on Blinds {
    id
    name
    level
    roomId
    opacity
    group
  }
`;

export const setBlindsLevelMutation = gql`
  mutation SetBlindsLevel($id: ID!, $level: Float!) {
    setBlind(id: $id, level: $level)
  }
`;
