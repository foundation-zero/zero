import {
  ChartDataType,
  Entries,
  MapEntries,
  Stamped,
  StampedWithSource,
  TimeSeriesData,
} from "@common/types";
import { useTimeoutFn } from "@vueuse/core";
import { type ClassValue, clsx } from "clsx";
import { Maybe } from "graphql/jsutils/Maybe";
import { twMerge } from "tailwind-merge";
import { computed, isRef, MaybeRef, onMounted, Ref, unref } from "vue";
import { NamedValue, useI18n } from "vue-i18n";

export * from "./numbers";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isDefined = <T>(value: T | undefined | null): value is T =>
  value !== undefined && value !== null;

export const compareByName = <T extends { name?: string | null }>(a: T, b: T) =>
  (a.name ?? "").localeCompare(b.name ?? "");

export const capitalizeFirst = (a: string) => {
  const f = a.substring(0, 1).toUpperCase();
  return `${f}${a.substring(1)}`;
};

export function ratioAsPercentage(ratio: MaybeRef<Maybe<number>>): Ref<number | undefined>;
export function ratioAsPercentage(ratio: MaybeRef<Maybe<number>>, defaultToZero: true): Ref<number>;
export function ratioAsPercentage(
  ratio: MaybeRef<Maybe<number>>,
  defaultToZero?: boolean,
): Ref<number | undefined> {
  return computed({
    get() {
      const value = unref(ratio);
      return value !== undefined ? Number(value) * 100 : defaultToZero ? 0 : undefined;
    },
    set(percentage: number) {
      if (isRef(ratio)) {
        ratio.value = percentage / 100;
      }
    },
  });
}

export const toInversedPercentage = (percentage: MaybeRef<number>) => 100 - unref(percentage);

export const separateDecimals = (
  value: Ref<Maybe<number>>,
  digits: number = 1,
): { integer: Ref<number>; decimal: Ref<number> } => {
  return {
    integer: computed(() => Math.floor(value.value ?? 0)),
    decimal: computed(() => Math.round(((value.value ?? 0) % 1) * 10 ** digits)),
  };
};

export const valueWithValidation = <T>(val: Ref<T>, validateFn: (next: T) => boolean) =>
  computed({
    get() {
      return val.value;
    },
    set(next: T) {
      if (validateFn(next)) {
        val.value = next;
      }
    },
  });

export const valueAsArray = <T>(value: Ref<T>) =>
  computed({
    get() {
      return [value.value];
    },
    set(next: T[]) {
      if (next.length === 0) throw new Error("Array cannot be empty");

      value.value = next[0];
    },
  });

export const writeProtected = <T>(value: Ref<T>, writeAllowed: Ref<boolean>) =>
  computed({
    get() {
      return value.value;
    },
    set(next: T) {
      if (writeAllowed.value) {
        value.value = next;
      }
    },
  });

export const toUpperCamelCase = (str: string) => str.replace(/([A-Z])/g, " $1").trim();
export const toCapitalized = (str: string) =>
  `${str.charAt(0).toLocaleUpperCase()}${str.slice(1).toLocaleLowerCase()}`;

export const tScoped = (scope: string) => {
  const { t } = useI18n();

  return (key: string, value?: NamedValue) => {
    return value ? t(`${scope}.${key}`, value) : t(`${scope}.${key}`);
  };
};

export const toTimeSeriesData = <T extends ChartDataType>({
  timestamp,
  value,
}: Stamped<T>): TimeSeriesData<T> => [new Date(timestamp), value];

export type LogEntry = {
  timestamp: Date | string | number;
};

export const logToSeries = <T extends LogEntry, K extends keyof T>(
  log: T[] | undefined,
  key: K,
): TimeSeriesData<Extract<T[K], ChartDataType>>[] =>
  log?.map((entry) => [
    entry.timestamp instanceof Date ? entry.timestamp : new Date(entry.timestamp),
    entry[key] as Extract<T[K], ChartDataType>,
  ]) ?? [];

export function isStamped<T>(input: unknown[] | Stamped<T>[]): input is Stamped<T>[];
export function isStamped<T>(
  input: unknown[] | StampedWithSource<T>[],
): input is StampedWithSource<T>[];
export function isStamped<T>(input: unknown | Stamped<T>): input is Stamped<T>;
export function isStamped<T>(input: unknown | StampedWithSource<T>): input is StampedWithSource<T>;
export function isStamped(input: unknown): input is Stamped<number>;
export function isStamped(input: unknown): boolean {
  if (Array.isArray(input)) return isStamped(input[0]);

  return typeof input === "object" && input !== null && "value" in input && "timestamp" in input;
}

export const isStampedWithSource = <T>(input: unknown): input is StampedWithSource<T> =>
  isStamped(input) && (input as StampedWithSource<T>).source != null;

export const stamp = <T>(value: MaybeRef<T>, timestamp = new Date()): Stamped<T> => ({
  value: unref(value),
  timestamp,
});
export const stampWithSource = <T>(
  value: MaybeRef<T>,
  source: string,
  timestamp = new Date(),
): StampedWithSource<T> => ({
  value: unref(value),
  timestamp,
  source,
});

export const unstamp = <T>(input: T | Stamped<T>): T => (isStamped(input) ? input.value : input);

export function tuple<K, V>(key: K, value: V): [K, V];
export function tuple<Entries extends unknown[]>(
  ...entries: Entries
): { [K in keyof Entries]: Entries[K] };
export function tuple(...args: unknown[]) {
  return args;
}

export const isTuple =
  (size: number) =>
  (input: unknown): input is unknown[] =>
    Array.isArray(input) && input.length === size;

export const isEntry = isTuple(2);

export type MapFrom<K, V> =
  | [K, V][]
  | K[]
  | readonly K[]
  | Map<K, V>
  | (K extends string | number | symbol ? Record<K, V> : never);

export function entriesOf<K, V>(map: Map<K, V>): MapEntries<Map<K, V>>[];
export function entriesOf<K extends string | number | symbol, V>(
  map: Record<K, V>,
): MapEntries<Map<K, V>>[];
export function entriesOf<K, V>(input: MapFrom<K, V>): [K, V][];
export function entriesOf<K, V>(obj?: MapFrom<K, V>) {
  if (obj == undefined) {
    return [];
  } else if (Array.isArray(obj)) {
    if (obj.every(isEntry)) {
      return obj as [K, V][];
    } else {
      return obj.map((key) => [key] as [K]);
    }
  } else if (obj instanceof Map) {
    const entries = Array.from(obj.entries());

    return entries.map(([key, value]) =>
      tuple(key, value instanceof Map ? entriesOf(value) : value),
    ) as MapEntries<Map<K, V>>[];
  } else return Object.entries(obj) as [K, V][];
}

export type EntryMapFn<K, V, T> = (key: K, value: V) => T;
export type KeyMapFn<K, V> = (key: K) => V;

export function toEntries<K extends string | number | symbol, V>(
  input: K[],
  mapFn: KeyMapFn<K, V>,
): [K, V][];
export function toEntries<K, V, T>(input: MapFrom<K, V>, mapFn: EntryMapFn<K, V, T>): [K, T][];
export function toEntries<K, V, T>(input: MapFrom<K, V>, mapFn: EntryMapFn<K, V, T>): [K, T][] {
  return entriesOf(input).map(([k, v]) => [k, mapFn(k, v)]);
}

export function toRecord<K extends string | number | symbol, V>(
  keys: K[] | readonly K[],
  mapFn: KeyMapFn<K, V>,
): Record<K, V>;
export function toRecord<K extends string | number | symbol, V, T>(
  input: Record<K, V> | Map<K, V> | Entries<K, V>,
  mapFn: EntryMapFn<K, V, T>,
): Record<K, T>;
export function toRecord<K extends string | number | symbol, V, T>(
  input: MapFrom<K, V>,
  mapFn: EntryMapFn<K, V, T>,
): Record<K, T> {
  return Object.fromEntries(toEntries(input, mapFn)) as Record<K, T>;
}

export function keysOf<T extends Record<string, unknown>>(obj: T): (keyof T)[];
export function keysOf<T extends Record<string, unknown>>(obj?: T): (keyof T)[] | undefined;
export function keysOf<T extends Record<string, unknown>>(obj?: T) {
  return obj ? (Object.keys(obj) as (keyof T)[]) : undefined;
}

export const cast = <T>(input: unknown): T => input as T;

export const mmath = {
  avg: (...numbers: number[]) => numbers.reduce((sum, num) => sum + num, 0) / numbers.length,
  normalizeDegrees: (angle: number) => ((angle % 360) + 360) % 360,
};

export const generateRandomId = (prefix: string = "") =>
  `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
export const extractProperty =
  <K extends string | number | symbol>(property: K) =>
  <V>(item: { [key in K]: V }): V =>
    item[property];

export const useFixed = (value: MaybeRef<number | undefined | null>, digits: MaybeRef<number>) =>
  computed<[number | undefined, number[] | undefined]>(() => {
    const unrefValue = unref(value);
    if (unrefValue == undefined) {
      return [undefined, undefined];
    } else {
      const [integer, fraction] = unrefValue.toFixed(unref(digits)).split(".");
      return [
        Number(integer),
        fraction != undefined ? Array.from(fraction).map(Number) : undefined,
      ];
    }
  });

export const refValue = unref;

export const useAutoFocus = <T extends HTMLElement>(
  ref: Ref<{ $el: T } | null>,
  enabled: MaybeRef<boolean> = true,
) => onMounted(() => unref(enabled) && useTimeoutFn(() => ref.value?.$el?.focus(), 100));
