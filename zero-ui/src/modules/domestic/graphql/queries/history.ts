import { gql } from "@urql/vue";
import { ControlsLogItem, SensorsLogItem } from ".";

export const getControlLogs = gql`
  query GetControlLogs($type: String) {
    controlsLog(where: { control: { type: { _eq: $type } } }) {
      ...ControlsLogItem
    }
  }

  ${ControlsLogItem}
`;

export const getSensorLogs = gql`
  query GetSensorLogs($type: String) {
    sensorsLog(where: { sensor: { type: { _eq: $type } } }) {
      ...SensorsLogItem
    }
  }

  ${SensorsLogItem}
`;
