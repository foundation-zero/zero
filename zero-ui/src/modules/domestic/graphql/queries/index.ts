import { gql } from "@urql/vue";

export const mutationResponse = gql`
  fragment MutationResponse on MutationResponse {
    code
    success
    message
  }
`;
