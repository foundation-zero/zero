import { ChartPeriod, ControlLog, ControlType, SensorLog, SensorType } from "@/@types";
import { getControlLogs, getSensorLogs } from "@/graphql/queries/history";
import { sortByTime, toTimeValueTuple } from "@/lib/utils";
import { useQuery } from "@urql/vue";
import { subDays, subHours, subMonths, subWeeks, subYears } from "date-fns";
import { defineStore } from "pinia";
import { computed, ref, Ref } from "vue";

const SUB_FN: Record<ChartPeriod, typeof subDays> = {
  [ChartPeriod.DAY]: subDays,
  [ChartPeriod.HOUR]: subHours,
  [ChartPeriod.WEEK]: subWeeks,
  [ChartPeriod.MONTH]: subMonths,
  [ChartPeriod.YEAR]: subYears,
};

export const useHistoryStore = defineStore("history", () => {
  const currentPeriod = ref(ChartPeriod.DAY);
  const offset = ref(0);
  const currentControlType: Ref<ControlType> = ref(ControlType.TEMPERATURE);
  const currentSensorType: Ref<SensorType> = ref(SensorType.TEMPERATURE);
  const between = computed(() => {
    const sub = SUB_FN[currentPeriod.value];
    const endDate = sub(Date.now(), offset.value);
    const startDate = sub(endDate, 1);
    return [startDate, endDate];
  });

  const controlHistory = useQuery<{ controlsLog: ControlLog[] }>({
    query: getControlLogs,
    variables: { type: currentControlType },
    pause: false,
  });

  const useControlHistory = (controlId?: string) =>
    computed(
      () =>
        controlHistory.data.value?.controlsLog
          .filter((item) => item.id === controlId)
          .map(toTimeValueTuple)
          .toSorted(sortByTime) ?? [],
    );

  const sensorHistory = useQuery<{ sensorsLog: SensorLog[] }>({
    query: getSensorLogs,
    variables: { type: currentSensorType },
    pause: false,
  });

  const useSensorHistory = (sensorId?: string) =>
    computed(
      () =>
        sensorHistory.data.value?.sensorsLog
          .filter((item) => item.id === sensorId)
          .map(toTimeValueTuple)
          .toSorted(sortByTime) ?? [],
    );

  const setControlType = (type: ControlType) => {
    currentControlType.value = type;
  };

  const setSensorType = (type: SensorType) => {
    currentSensorType.value = type;
  };

  const setPeriod = (period: ChartPeriod) => {
    currentPeriod.value = period;
  };

  const setOffset = (newOffset: number = 0) => {
    offset.value = newOffset;
  };

  return {
    currentPeriod,
    currentControlType,
    currentSensorType,
    between,
    offset,
    controlHistory,
    sensorHistory,
    useControlHistory,
    useSensorHistory,
    setControlType,
    setSensorType,
    setOffset,
    setPeriod,
  };
});
