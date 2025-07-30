import { gql } from "@urql/vue";

export const getVersion = gql`
  query GetVersion {
    version
  }
`;
