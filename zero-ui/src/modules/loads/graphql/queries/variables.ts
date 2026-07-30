import { gql } from "@urql/vue";

export const VARIABLE_REFERENCE_VALUES = gql`
  query GetVariableReferenceValues(
    $variables: [ID!]!
    $sailset: [ID!]!
    $awaRange: AwaRange!
    $awsRange: AwsRange!
    $tack: Tack!
  ) {
    variables(variables: $variables) {
      id
      reference(
        case: { sailset: $sailset, awaRange: $awaRange, awsRange: $awsRange, tack: $tack }
      ) {
        alarmHigh
        alarmLow
        target
        warningHigh
        warningLow
      }
    }
    loadCase(case: { sailset: $sailset, awaRange: $awaRange, awsRange: $awsRange, tack: $tack }) {
      id
      name
      awa
      aws
      heel
      twa
      tws
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
