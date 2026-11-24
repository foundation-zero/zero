import {
  DEFAULT_REFRESH_INTERVAL,
  DEFAULT_SPAN,
} from "@/modules/thrapp/monitoring/monitoring.consts";
import type { TimeRange } from "@/modules/thrapp/monitoring/monitoring.types";
import {
  isLive,
  resolveRange,
  shiftRange,
  zoomOut as zoomedOut,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import { useIntervalFn } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";

/** The time range every chart on the monitoring page shares, and when they refresh. */
export const useMonitoringStore = defineStore("monitoring", () => {
  const range = ref<TimeRange>({ span: DEFAULT_SPAN, end: null });
  const refreshInterval = ref<number>(DEFAULT_REFRESH_INTERVAL);

  // Charts reload the whole range when `version` changes, and only the newest
  // part when just `now` moves on.
  const now = ref(Date.now());
  const version = ref(0);

  const resolved = computed(() => resolveRange(range.value, now.value));
  const live = computed(() => isLive(range.value));

  const setRange = (next: TimeRange) => {
    range.value = next;
    now.value = Date.now();
    version.value++;
  };

  const shift = (direction: -1 | 1) => setRange(shiftRange(range.value, direction, Date.now()));
  const zoomOut = () => setRange(zoomedOut(range.value));
  const reload = () => setRange(range.value);

  const tick = () => {
    now.value = Date.now();
  };

  const timer = useIntervalFn(tick, refreshInterval, { immediate: false });
  watch(
    [refreshInterval, live],
    ([interval, isLiveRange]) => {
      if (interval > 0 && isLiveRange) timer.resume();
      else timer.pause();
    },
    { immediate: true },
  );

  return { range, refreshInterval, now, version, resolved, live, setRange, shift, zoomOut, reload };
});
