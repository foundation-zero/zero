import { defineStore } from "pinia";

import { keysOf, toTimeSeriesData, tuple } from "@/modules/common/lib/utils";
import { ChartDataType, SeriesChart, Stamped, TimeSeriesData } from "@/modules/common/types";
import { context } from "@/modules/thrs/graphql/client";
import { useQuery } from "@urql/vue";
import { objectEntries, useLocalStorage } from "@vueuse/core";
import { useObservable } from "@vueuse/rxjs";
import { tap } from "rxjs";
import { timer } from "rxjs/internal/observable/timer";
import { scan } from "rxjs/internal/operators/scan";
import { switchMap } from "rxjs/internal/operators/switchMap";
import { computed, Ref } from "vue";
import { QUERY_ALL, THRS } from "../lib/consts";
import { SchemaDefinition, SchemaDefinitions } from "../types";

export const AMOUNT_OF_ENTRIES_TO_CACHE = 1_000;

type Component = Record<string, Stamped<ChartDataType>>;
type Components = Record<string, Component>;
type HistoryKey = `${keyof THRS["modules"]}/${string}/${string}`;
type ModuleHistory = Record<HistoryKey, TimeSeriesData[]>;

const EXCLUDED_FIELDS = ["__typename"];

export const extractHistory = (source: THRS, currentHistory: ModuleHistory): ModuleHistory => {
  const newHistory: ModuleHistory = { ...currentHistory };

  const extract = (moduleName: keyof THRS["modules"], components: Components | null) => {
    if (!components) return;

    objectEntries(components).forEach(([componentKey, component]) => {
      objectEntries(component).forEach(([fieldKey, stampedValue]) => {
        if (EXCLUDED_FIELDS.includes(fieldKey) || EXCLUDED_FIELDS.includes(componentKey)) {
          return;
        }

        const history = (newHistory[`${moduleName}/${fieldKey}/${componentKey}`] ??= []);
        const lastItem = history[history.length - 1];

        // Avoid pushing duplicate entries
        if (lastItem) {
          const [previousTimestamp] = lastItem;

          if (new Date(previousTimestamp).getTime() === new Date(stampedValue.timestamp).getTime())
            return;
        }

        history.push(toTimeSeriesData(stampedValue));

        // Limit the amount of cached entries
        if (history.length > AMOUNT_OF_ENTRIES_TO_CACHE) {
          history.shift();
        }
      });
    });
  };

  objectEntries(source.modules).forEach(([moduleName, module]) => {
    extract(moduleName, module.controlValues);
    extract(moduleName, module.sensorValues);
    extract(moduleName, module.simulation?.outputs);
  });

  return newHistory;
};

export const useThrsHistory = defineStore("thrsHistory", () => {
  const lastUpdate = useLocalStorage<number | null>("thrs-history-last-update", null);

  const cachedData = useLocalStorage<ModuleHistory>(
    "thrs-history",
    {},
    {
      serializer: {
        read: (v) => (v ? JSON.parse(v) : {}),
        write: (v) => JSON.stringify(v),
      },
    },
  );

  const clear = () => {
    cachedData.value = {};
    lastUpdate.value = null;
  };

  const { data, executeQuery: update } = useQuery<THRS>({
    query: QUERY_ALL,
    context,
    requestPolicy: "network-only",
  });

  const history: Ref<ModuleHistory> = useObservable(
    timer(0, 5000).pipe(
      switchMap(async () => {
        await update();

        return data.value;
      }),
      scan(
        (acc, newData) =>
          newData === undefined ? acc : extractHistory(newData, lastUpdate.value ? acc : {}),
        cachedData.value,
      ),
      tap((data) => {
        cachedData.value = data;
        lastUpdate.value = Date.now();
      }),
    ),
  );

  const useHistory = <Type extends ChartDataType = ChartDataType>(
    module: keyof THRS["modules"],
    field: string,
    definition: SchemaDefinitions<SchemaDefinition<unknown>>,
  ) =>
    computed<SeriesChart<Type>[]>(() => {
      if (!cachedData.value) return [];

      const historyKeys = keysOf(definition)
        .map((componentName) =>
          tuple(componentName, `${module}/${field}/${componentName}` as HistoryKey),
        )
        .filter(([, key]) => key in cachedData.value);

      return historyKeys.map(([componentName, key]) => ({
        name: componentName,
        data: cachedData.value[key] as TimeSeriesData<Type>[],
      }));
    });

  return {
    data,
    history,
    lastUpdate,
    useHistory,
    clear,
  };
});
