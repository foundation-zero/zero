import { gql } from "@urql/vue";

export const VARIABLE_REFERENCE_VALUES = gql`
  query GetVariableReferenceValues(
    $variables: [ID!]!
    $sailset: [Sails!]!
    $awaRange: AwaRange!
    $awsRange: AwsRange!
  ) {
    variables(variables: $variables) {
      id
      reference(case: { sailset: $sailset, awaRange: $awaRange, awsRange: $awsRange }) {
        alarmHigh
        alarmLow
        target
        warningHigh
        warningLow
      }
    }
  }
`;

export const VARIABLE_DEFINITIONS = gql`
  query GetVariableDefinitions {
    variables {
      id
      variable {
        name
        unit
        minimum
        maximum
      }
    }
  }
`;

export const VARIABLE_ACTUALS = gql`
  query GetVariableActuals($variables: [ID!]!) {
    variables(variables: $variables) {
      id
      actual {
        value
      }
    }
  }
`;
