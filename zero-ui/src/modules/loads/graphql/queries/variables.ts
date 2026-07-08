import { gql } from "@urql/vue";

export const VARIABLE_REFERENCE_VALUES = gql`
  query GetVariableReferenceValues(
    $variables: [ID!]!
    $sailset: [ID!]!
    $awaRange: AwaRange!
    $awsRange: AwsRange!
    $windDirection: WindDirection!
  ) {
    variables(variables: $variables) {
      id
      reference(
        case: {
          sailset: $sailset
          awaRange: $awaRange
          awsRange: $awsRange
          windDirection: $windDirection
        }
      ) {
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
        scaleMin
        scaleMax
        scaleMinLabel
        scaleMaxLabel
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
