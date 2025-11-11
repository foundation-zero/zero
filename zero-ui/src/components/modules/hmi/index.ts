import { Entries, TimeBasedChart } from "@/@types";
import { Stamped } from "@/@types/thrs";
import { THRS, THRSModules } from "@/lib/consts";
import { isStampedNumber, mapFromObject, toEntries, toMap } from "@/lib/utils";
import { useQuery } from "@urql/vue";
import { Serializer, useLocalStorage } from "@vueuse/core";
import { useObservable } from "@vueuse/rxjs";
import { scan, switchMap, timer } from "rxjs";
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
  update: () => Promise<void>;
  data: Ref<T | undefined>;
};

export const queryDeep = <TSelect>(
  query: Ref<string>,
  select: (data?: THRS) => TSelect,
): DeepQuery<TSelect> => {
  const q = useQuery<THRS>({ query });

  return {
    update: async () => {
      await q.executeQuery();
    },
    data: computed<TSelect>(() => select(q.data.value)),
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
  type ComponentHistory = Map<string, FieldHistory>;
  type FieldHistory = Map<FieldName, Stamped<string | number | boolean>[]>;
  type FieldSeries = [FieldName, TimeBasedChart[]];

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

        return entries
          .toSorted((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
          .concat(value)
          .slice(-AMOUNT_OF_ENTRIES_TO_CACHE);
      }),
    );
  };

  // RxJS stream to accumulate query results
  const history: Ref<ComponentHistory> = useObservable(
    timer(0, 1000).pipe(
      switchMap(async () => {
        await query.update();
        return query.data.value as T | undefined;
      }),
      scan(
        (acc, newData) =>
          (cachedData.value = newData === undefined ? acc : extractUniqueEntries(newData, acc)),
        cachedData.value,
      ),
    ),
  );

  const series = computed<FieldSeries[]>(() =>
    fieldNames.map<FieldSeries>((fieldName) => [
      fieldName,
      Array.from(history.value?.entries() ?? [])
        .filter(([, component]) => component.has(fieldName))
        .map(([componentName, component]) => ({
          name: componentName,
          data: component.get(fieldName)!.filter(isStampedNumber),
        })),
    ]),
  );

  return { history, series, query };
};
