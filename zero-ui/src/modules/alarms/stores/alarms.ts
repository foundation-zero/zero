import type { CombinedError } from "@urql/vue";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import client from "../graphql/client";
import { ALARM_LIST } from "../graphql/queries/alarm-list";
import { isActive, skipWhilePending } from "../lib/utils";
import type { Alarm, AlarmListQueryResponse, AlarmPriority } from "../types";

const DEFAULT_WINDOW_MINUTES = 60;

/** The AMCS hierarchy; an unknown priority ranks as a warning, as ntfy does. */
const PRIORITY_RANK: Record<AlarmPriority, number> = {
  GEA: 5,
  EMERGENCY: 4,
  ALARM: 3,
  WARNING: 2,
  UNKNOWN: 2,
  CAUTION: 1,
  EVENT: 0,
};

const rank = (alarm: Alarm) => PRIORITY_RANK[alarm.priority ?? "UNKNOWN"];

const time = (timestamp: string | null) => (timestamp ? Date.parse(timestamp) : 0);

/** Unacknowledged first, then the highest priority, then the most recent. */
const byUrgency = (a: Alarm, b: Alarm) =>
  Number(!!a.acknowledged) - Number(!!b.acknowledged) ||
  rank(b) - rank(a) ||
  time(b.activatedAt ?? b.lastChangeAt) - time(a.activatedAt ?? a.lastChangeAt);

const byLastChange = (a: Alarm, b: Alarm) => time(b.lastChangeAt) - time(a.lastChangeAt);

export const useAlarmsStore = defineStore("alarms", () => {
  const data = ref<AlarmListQueryResponse>();
  const error = ref<CombinedError>();

  const refresh = skipWhilePending(async () => {
    const result = await client
      .query<AlarmListQueryResponse>(ALARM_LIST, {}, { requestPolicy: "network-only" })
      .toPromise();
    error.value = result.error;
    if (result.data) {
      data.value = result.data;
    }
  });
  void refresh();

  const loaded = computed(() => data.value !== undefined);
  const alarmList = computed(() => data.value?.alerts?.alarmList ?? null);
  /** The API answers, but the forwarder no longer publishes the list. */
  const offline = computed(() => loaded.value && !alarmList.value);

  const alarms = computed(() =>
    (alarmList.value?.alarms ?? []).filter((alarm): alarm is Alarm => alarm !== null),
  );
  const activeAlarms = computed(() => alarms.value.filter(isActive).toSorted(byUrgency));
  const endedAlarms = computed(() =>
    alarms.value.filter((alarm) => !isActive(alarm)).toSorted(byLastChange),
  );
  const windowMinutes = computed(
    () => alarmList.value?.recentWindowMinutes ?? DEFAULT_WINDOW_MINUTES,
  );

  return {
    loaded,
    offline,
    activeAlarms,
    endedAlarms,
    windowMinutes,
    error,
    refresh,
  };
});
