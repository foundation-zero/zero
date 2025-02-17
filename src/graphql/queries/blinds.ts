import { gql } from "@urql/vue";

export const BlindsFragment = gql`
  fragment BlindsItem on blinds {
    id
    name
    level
    room_id
    opacity
    group
  }
`;

export const byRoomId = gql`
  query GetBlindsByRoom($roomId: String!) {
    blinds(where: { room_id: { _eq: $roomId } }) {
      ...BlindsItem
    }
  }

  ${BlindsFragment}
`;
