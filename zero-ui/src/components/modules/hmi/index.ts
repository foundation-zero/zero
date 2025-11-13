import { ChartDataType, Entries, StampedChart } from "@/@types";
import { Stamped } from "@/@types/thrs";
import { THRS, THRSModules } from "@/lib/consts";
import { isStamped, mapFromObject, toEntries, toMap } from "@/lib/utils";
import { useQuery } from "@urql/vue";
import { Serializer, useLocalStorage } from "@vueuse/core";
import { useObservable } from "@vueuse/rxjs";
import { scan, switchMap, tap, timer } from "rxjs";
import { computed, Ref } from "vue";

export type ComponentWithType<T extends string> = {
  componentType: T;
};

export const queryFor = <
  Module extends keyof THRSModules,
  Values extends keyof THRSModules[Module],
>(
  module: Module,
  fieldName: Values,
  componentsQuery: string,
) =>
  computed(() => {
    return `query ${module}Values {
    modules {
      ${module} {
        ${String(fieldName)} {
          ${componentsQuery}
        }
      }
    }
  }`;
  });

type DeepQuery<T> = {
  update: () => Promise<T>;
  data: Ref<T | undefined>;
};

export const queryDeep = <TSelect>(
  query: Ref<string>,
  select: (data?: THRS) => TSelect,
): DeepQuery<TSelect> => {
  const q = useQuery<THRS>({ query });
  const data = computed<TSelect>(() => select(q.data.value));

  return {
    update: async () => {
      await q.executeQuery();
      return data.value;
    },
    data,
  };
};

export const AMOUNT_OF_ENTRIES_TO_CACHE = 1_000;

export const useHistory = <
  FieldName extends string,
  T extends Record<string, Partial<Record<FieldName, Stamped<string | number | boolean>>>>,
  Q extends DeepQuery<T | undefined>,
>(
  query: Q,
  fieldNames: FieldName[],
  storageKey: string,
) => {
  type FieldHistory = Map<FieldName, Stamped<string | number | boolean>[]>;
  type ComponentHistory = Map<string, FieldHistory>;
  type FieldSeries<Type extends ChartDataType = ChartDataType> = [FieldName, StampedChart<Type>[]];

  const historySerializer: Serializer<ComponentHistory> = {
    read: (v) => {
      if (v === null) return new Map();

      const parsed = JSON.parse(v) as Entries<ComponentHistory>[];
      return toMap(parsed, (_, fields) => new Map(fields));
    },
    write: (v) => {
      return JSON.stringify(v ? toEntries(v) : []);
    },
  };

  const cachedData = useLocalStorage<ComponentHistory>(storageKey, new Map(), {
    serializer: historySerializer,
  });

  // Post-process query results to filter by unique timestamps
  const extractUniqueEntries = (
    newData: T,
    existingHistory: ComponentHistory,
  ): ComponentHistory => {
    return mapFromObject(newData, (componentName, component) =>
      mapFromObject(component, (fieldName, value) => {
        const fieldHistory: FieldHistory = existingHistory.get(componentName) ?? new Map();
        const entries = fieldHistory.get(fieldName) ?? [];

        const lastEntry = entries[entries.length - 1];

        if (lastEntry?.timestamp === value.timestamp) {
          return entries;
        }

        return entries.concat(value).slice(-AMOUNT_OF_ENTRIES_TO_CACHE);
      }),
    );
  };

  // RxJS stream to accumulate query results
  const history: Ref<ComponentHistory> = useObservable(
    timer(0, 1000).pipe(
      switchMap(async () => {
        await query.update();
        return query.data.value;
      }),
      scan(
        (acc, newData) => (newData === undefined ? acc : extractUniqueEntries(newData, acc)),
        cachedData.value,
      ),
      tap((data) => {
        cachedData.value = data;
      }),
    ),
  );

  const series = computed<FieldSeries[]>(() =>
    fieldNames
      .map<FieldSeries>((fieldName) => [
        fieldName,
        Array.from(history.value?.entries() ?? [])
          .filter(([, component]) => component.has(fieldName))
          .map(([componentName, component]) => ({
            name: componentName,
            data: component.get(fieldName)!.filter(isStamped),
          })),
      ])
      .filter(([, entries]) => entries.length > 0),
  );

  return { history, series, query };
};
