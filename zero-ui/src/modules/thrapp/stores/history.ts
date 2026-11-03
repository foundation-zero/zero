import { defineStore } from "pinia";

import { entriesOf } from "@/modules/common/lib/utils";
import { ChartDataType, TimeSeriesData } from "@/modules/common/types";
import { DocumentInput, TypedDocumentNode } from "@urql/vue";
import { useIntervalFn, useLocalStorage } from "@vueuse/core";
import { ref, shallowRef, watch } from "vue";
import { client, context } from "../graphql/client";
import { ComponentRecord, THRS } from "../lib/consts";

export const useThrsHistory = defineStore("thrsHistory", () => {
  const lastUpdate = useLocalStorage<number | null>("thrs-history-last-update", null);
  const data = ref<THRS>();

  /** Query of the active view (see `queries.consts.ts`); nothing is queried without one. */
  const activeQuery = shallowRef<TypedDocumentNode>();

  // Responses to a request made before the active query changed are dropped.
  let latestRequest = 0;

  const refresh = async () => {
    if (!activeQuery.value) return data.value;

    const request = ++latestRequest;
    const result = await client
      .query<THRS>(
        activeQuery.value,
        {},
        {
          ...context,
          requestPolicy: "network-only",
        },
      )
      .toPromise();

    if (request === latestRequest) {
      data.value = result.data;
      lastUpdate.value = Date.now();
    }
    return data.value;
  };

  const { pause, resume } = useIntervalFn(refresh, 5000);

  // The data of another view's query lacks what this view shows, so drop it before refreshing.
  // Pending responses are dropped too, also when the query is cleared.
  watch(activeQuery, () => {
    latestRequest++;
    data.value = undefined;
    refresh();
  });

  const mutate = (query: DocumentInput, variables: Record<string, unknown>) => {
    return client.mutation(query, variables).toPromise();
  };

  const getHistory = <Type extends ChartDataType = ChartDataType>(
    data: Record<string, ComponentRecord> | undefined,
    field: string,
  ) => {
    if (!data) return [];
    else {
      return entriesOf(data)
        .filter(([_, componentData]) => componentData[field] !== undefined)
        .map(([componentName, componentData]) => ({
          name: componentName,
          data: [
            [componentData[field].timestamp, componentData[field].value],
          ] as TimeSeriesData<Type>[],
        }));
    }
  };

  return {
    data,
    lastUpdate,
    activeQuery,
    refresh,
    pause,
    resume,
    mutate,
    getHistory,
  };
});
