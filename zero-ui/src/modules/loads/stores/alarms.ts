import { useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed } from "vue";
import { LOADS_CONTEXT } from "../graphql/client";
import { ALARMS } from "../graphql/queries/alarms";
import { QueryAlarms } from "../types/queries";

const UPDATE_ALARMS_INTERVAL_MS = 1000;

export const useAlarmsStore = defineStore("loads-alarms", () => {
  const { data: activeAlarmsResult, executeQuery: updateAlarms } = useQuery<QueryAlarms>({
    query: ALARMS,
    variables: { active: true },
    requestPolicy: "network-only",
    context: LOADS_CONTEXT,
  });

  const { resume: startPolling, pause: stopPolling } = useIntervalFn(
    updateAlarms,
    UPDATE_ALARMS_INTERVAL_MS,
    {
      immediate: false,
    },
  );

  const activeAlarms = computed(() => activeAlarmsResult.value?.alarms ?? []);
  const status = computed(() => (activeAlarms.value.length === 0 ? "ok" : "alarm"));

  return {
    activeAlarms,
    startPolling,
    stopPolling,
    status,
  };
});
