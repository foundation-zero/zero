import {
  getRoomAirConditioningLog,
  getRoomVentilationLog,
} from "@/modules/domestic/graphql/queries/history";
import { useQuery } from "@urql/vue";
import { defineStore } from "pinia";

export const useHistoryStore = defineStore("history", () => {
  const { data: airConditioningLog } = useQuery<{
    rooms: {
      id: string;
      name: string;
      airConditioningLog: {
        timestamp: Date;
        actualTemperature: number;
        temperatureSetpoint: number;
        actualHumidity: number;
        humiditySetpoint: number;
      }[];
    }[];
  }>({
    query: getRoomAirConditioningLog,
    variables: { period: "DAY" },
    pause: false,
  });

  const { data: ventilationLog } = useQuery<{
    rooms: {
      id: string;
      name: string;
      ventilationLog: {
        timestamp: Date;
        actualCo2: number;
        co2Setpoint: number;
      }[];
    }[];
  }>({
    query: getRoomVentilationLog,
    variables: { period: "DAY" },
    pause: false,
  });

  return {
    airConditioningLog,
    ventilationLog,
  };
});
