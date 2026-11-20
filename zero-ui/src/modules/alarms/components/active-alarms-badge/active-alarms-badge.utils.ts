import { useIntervalFn } from "@vueuse/core";
import { ref } from "vue";
import client from "../../graphql/client";
import { ACTIVE_ALARMS } from "../../graphql/queries/active-alarms";
import { POLL_INTERVAL_MS } from "../../lib/consts";
import { isActive } from "../../lib/utils";
import type { AlarmListQueryResponse } from "../../types";

/**
 * The number of active alarms, for outside the alarms app. It queries the alarms client itself,
 * as `useQuery` would go through the app-wide Hasura client and send its token to the bridge.
 * Zero while the list is unavailable, as the alarms app is where that is reported.
 */
export function useActiveAlarmCount(intervalMs = POLL_INTERVAL_MS) {
  const count = ref(0);
  // A slow bridge would otherwise collect a request every interval.
  let pending = false;

  const refresh = async () => {
    if (pending) {
      return;
    }
    pending = true;
    try {
      const { data } = await client
        .query<AlarmListQueryResponse>(ACTIVE_ALARMS, {}, { requestPolicy: "network-only" })
        .toPromise();
      count.value = (data?.alerts?.alarmList?.alarms ?? []).filter(isActive).length;
    } finally {
      pending = false;
    }
  };

  useIntervalFn(refresh, intervalMs, { immediateCallback: true });

  return count;
}
