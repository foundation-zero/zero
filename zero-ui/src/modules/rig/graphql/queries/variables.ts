import { gql } from "@urql/vue";

export const VARIABLE_DEFINITIONS = gql`
  query GetRigVariableDefinitions {
    variables {
      id
      variable {
        name
        unit
      }
    }
  }
`;

export const VARIABLE_ACTUALS = gql`
  query GetRigVariableActuals($variables: [ID!]!) {
    variables(variables: $variables) {
      id
      actual {
        value
      }
    }
  }
`;
