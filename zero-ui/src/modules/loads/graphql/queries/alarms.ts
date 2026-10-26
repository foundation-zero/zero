import { gql } from "@urql/vue";

export const ALARMS = gql`
  query GetAlarms($active: Boolean) {
    alarms(active: $active) {
      id
      name
      unit
      active
      actualValue
      thresholdValue
      actual {
        variable {
          id
        }
      }
    }
  }
`;
