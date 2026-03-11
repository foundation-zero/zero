import { gql } from "@urql/vue";

export const ALL_SAILS = gql`
  query GetAllSails {
    sails {
      abbreviation
      id
      name
      positionId
      variantName
    }
  }
`;
