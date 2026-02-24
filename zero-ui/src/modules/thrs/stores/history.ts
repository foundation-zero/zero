import { defineStore } from "pinia";

import { keysOf, toTimeSeriesData, tuple } from "@/modules/common/lib/utils";
import { ChartDataType, SeriesChart, Stamped, TimeSeriesData } from "@/modules/common/types";
import { context } from "@/modules/thrs/graphql/client";
import { useQuery } from "@urql/vue";
import { objectEntries, useLocalStorage } from "@vueuse/core";
import { useObservable } from "@vueuse/rxjs";
import { Subject, tap } from "rxjs";
import { timer } from "rxjs/internal/observable/timer";
import { scan } from "rxjs/internal/operators/scan";
import { startWith } from "rxjs/internal/operators/startWith";
import { switchMap } from "rxjs/internal/operators/switchMap";
import { computed, Ref } from "vue";
import { QUERY_ALL, THRS } from "../lib/consts";
import { SchemaDefinition, SchemaDefinitions } from "../types";

export const AMOUNT_OF_ENTRIES_TO_CACHE = 1_000;

type Component = Record<string, Stamped<ChartDataType>>;
type Components = Record<string, Component>;

export type HistoryRootKey = keyof THRS["modules"] | "simulation";
export type HistoryKey = `${HistoryRootKey}/${string}/${string}`;
type ModuleHistory = Record<HistoryKey, TimeSeriesData[]>;

type TypelessRecord<T extends Record<string, unknown>> = Omit<T, "__typename">;

const toTypelessRecord = <T extends Record<string, unknown>>(record: T): TypelessRecord<T> => {
  const { __typename, ...rest } = record;
  return rest;
};

export const extractHistory = (source: THRS, currentHistory: ModuleHistory): ModuleHistory => {
  const newHistory: ModuleHistory = { ...currentHistory };

  const extract = (moduleName: HistoryRootKey, components: Components | null) => {
    if (!components) return;

    objectEntries(components).forEach(([componentKey, component]) => {
      objectEntries(toTypelessRecord(component)).forEach(([fieldKey, stampedValue]) => {
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

  if (source == null) return newHistory;

  objectEntries(source.modules).forEach(([moduleName, module]) => {
    extract(moduleName, module.controlValues);
    extract(moduleName, module.sensorValues);
  });

  extract("simulation", toTypelessRecord(source.simulation.outputs));
  extract("simulation", toTypelessRecord(source.simulation.inputs));

  return newHistory;
};

export const useThrsHistory = defineStore("thrsHistory", () => {
  const lastUpdate = useLocalStorage<number | null>("thrs-history-last-update", null);
  const cachedData = useLocalStorage<ModuleHistory>("thrs-history", {});

  const restartTrigger$ = new Subject<void>();

  const clear = () => {
    cachedData.value = {};
    lastUpdate.value = null;
    restartTrigger$.next();
  };

  const { data, executeQuery: update } = useQuery<THRS>({
    query: QUERY_ALL,
    context,
    requestPolicy: "network-only",
  });

  const history: Ref<ModuleHistory> = useObservable(
    restartTrigger$.pipe(
      startWith(null),
      switchMap(() => timer(0, 5000)),
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
    module: HistoryRootKey,
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
