import { useIntervalFn } from "@vueuse/core";
import { ref } from "vue";
import client from "../../graphql/client";
import { ACTIVE_ALARMS } from "../../graphql/queries/active-alarms";
import { POLL_INTERVAL_MS } from "../../lib/consts";
import { isActive, skipWhilePending } from "../../lib/utils";
import type { AlarmListQueryResponse } from "../../types";

/**
 * The number of active alarms, for outside the alarms app. Zero while the list is unavailable,
 * as the alarms app is where that is reported.
 */
export function useActiveAlarmCount(intervalMs = POLL_INTERVAL_MS) {
  const count = ref(0);

  // A slow bridge would otherwise collect a request every interval.
  const refresh = skipWhilePending(async () => {
    const { data } = await client
      .query<AlarmListQueryResponse>(ACTIVE_ALARMS, {}, { requestPolicy: "network-only" })
      .toPromise();
    count.value = (data?.alerts?.alarmList?.alarms ?? []).filter(isActive).length;
  });

  useIntervalFn(refresh, intervalMs, { immediateCallback: true });

  return count;
}
