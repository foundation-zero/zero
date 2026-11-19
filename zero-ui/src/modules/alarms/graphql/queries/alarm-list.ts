import { gql } from "@urql/vue";

export const ALARM_LIST = gql`
  query GetAlarmList {
    alerts {
      alarmList {
        publishedAt
        recentWindowMinutes
        alarms {
          system
          tag
          location
          description
          priority
          active
          acknowledged
          activatedAt
          lastChangeAt
          lastUpdate
        }
      }
    }
  }
`;
