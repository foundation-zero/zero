import { gql } from "@urql/vue";

export const ACTIVE_ALARMS = gql`
  query GetActiveAlarms {
    alerts {
      alarmList {
        alarms {
          active
        }
      }
    }
  }
`;
