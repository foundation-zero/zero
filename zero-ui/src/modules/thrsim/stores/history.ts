import { defineStore } from "pinia";

import { entriesOf } from "@/modules/common/lib/utils";
import { ChartDataType, TimeSeriesData } from "@/modules/common/types";
import { client, context } from "@/modules/thrsim/graphql/client";
import { DocumentInput, useQuery } from "@urql/vue";
import { useIntervalFn, useLocalStorage } from "@vueuse/core";
import { ComponentRecord, QUERY_ALL, THRS } from "../lib/consts";

export const useThrsHistory = defineStore("thrsHistory", () => {
  const lastUpdate = useLocalStorage<number | null>("thrs-history-last-update", null);

  const { data, executeQuery: update } = useQuery<THRS>({
    query: QUERY_ALL,
    context,
    requestPolicy: "network-only",
  });

  const refresh = async () => {
    await update();
    lastUpdate.value = Date.now();
    return data.value;
  };

  const { pause, resume } = useIntervalFn(refresh, 5000, { immediate: true });

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
    refresh,
    pause,
    resume,
    mutate,
    getHistory,
  };
});
