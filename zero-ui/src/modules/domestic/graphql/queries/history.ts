import { gql } from "@urql/vue";

export const getRoomAirConditioningLog = gql`
  query GetRoomAirConditioningLog($period: TimePeriod!) {
    rooms: domesticRooms {
      id
      name
      airConditioningLog(period: $period) {
        timestamp
        actualTemperature
        temperatureSetpoint
        actualHumidity
        humiditySetpoint
      }
    }
  }
`;

export const getRoomVentilationLog = gql`
  query GetRoomVentilationLog($period: TimePeriod!) {
    rooms: domesticRooms {
      id
      name
      ventilationLog(period: $period) {
        timestamp
        actualCo2
        co2Setpoint
      }
    }
  }
`;
