import {
  Room,
  RoomState,
  SafeRangeThresholds,
  Thresholds,
  TimeValueObject,
  TimeValueTuple,
  ValidationStatus,
  ValueObject,
} from "@/modules/domestic/types";

import {
  ChartDataType,
  Entries,
  History,
  MapEntries,
  SeriesChart,
  Stamped,
  StampedChart,
  TimeSeriesData,
} from "@common/types";
import { ArgumentsType, useIntervalFn, useTimeoutFn } from "@vueuse/core";
import { type ClassValue, clsx } from "clsx";
import { Maybe } from "graphql/jsutils/Maybe";
import { twMerge } from "tailwind-merge";
import {
  computed,
  ComputedRef,
  isRef,
  MaybeRef,
  onMounted,
  ref,
  Ref,
  unref,
  watch,
  WritableComputedRef,
} from "vue";
import { NamedValue, useI18n } from "vue-i18n";
import {
  CO2_THRESHOLDS,
  DEMO_MODE,
  HUMIDITY_THRESHOLDS,
  TEMPERATURE_THRESHOLDS,
} from "../../domestic/lib/consts";

export * from "./numbers";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const isDefined = <T>(value: T | undefined | null): value is T =>
  value !== undefined && value !== null;

export const compareByName = <T extends { name?: string | null }>(a: T, b: T) =>
  (a.name ?? "").localeCompare(b.name ?? "");

export const validationStatusToNumber: Record<ValidationStatus, number> = {
  [ValidationStatus.OK]: 0,
  [ValidationStatus.WARN]: 1,
  [ValidationStatus.FAIL]: 2,
  [ValidationStatus.UNKNOWN]: 0,
};

export const capitalizeFirst = (a: string) => {
  const f = a.substring(0, 1).toUpperCase();
  return `${f}${a.substring(1)}`;
};

export const compareByValidationStatus = (a: ValidationStatus, b: ValidationStatus) =>
  validationStatusToNumber[a] - validationStatusToNumber[b];

export const updateSetpointWhenControlsHaveChanged = <K extends string>(
  value: Ref<Maybe<number>>,
  controls: Ref<{ [key in K]?: Maybe<number> }[]>,
  key: K,
) =>
  watch(controls, ([next], [prev]) => {
    if (next?.[key] !== prev?.[key] && next !== undefined) {
      value.value = next[key];
    }
  });

export const ratioAsPercentage = (ratio: MaybeRef<Maybe<number>>) =>
  computed({
    get() {
      return Number(unref(ratio)) * 100;
    },
    set(percentage: number) {
      if (isRef(ratio)) {
        ratio.value = percentage / 100;
      }
    },
  });

export const toInversedPercentage = (percentage: number) => 100 - percentage;
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

export const generateRandomValues = (amount: number, min: number = 0, max: number = 1000) =>
  new Array(amount).fill(0).map(() => Math.random() * (max - min + 1) + min);

export type LiveValuesOptions = {
  min: number;
  max: number;
  timeout: number;
};

export function useLiveRandomValues(
  amount: number,
  options: Partial<LiveValuesOptions> = {},
): Ref<number[]> {
  const { min = 0, max = 1000, timeout = 5000 } = options;
  const randomValues = ref<number[]>(generateRandomValues(amount, min, max));

  useIntervalFn(() => {
    randomValues.value.shift();
    randomValues.value.push(...generateRandomValues(1, min, max));
  }, timeout);

  return randomValues;
}

const ONE_DAY = 24 * 3600 * 1000;

export const useDemoValues =
  (demoMode: boolean) =>
  <T extends TimeValueTuple<number>>(
    prodValuesFn: () => Ref<T[]>,
    ...args: ArgumentsType<typeof useLiveRandomValues>
  ): Ref<TimeValueTuple<number>[]> =>
    demoMode
      ? useTransform(
          useLiveRandomValues(...args),
          (val, index) => [new Date(Date.now() + index * ONE_DAY), val] as T,
        )
      : prodValuesFn();

export const useDemoControlValues = useDemoValues(DEMO_MODE);
export const useDemoSensorValues = useDemoValues(DEMO_MODE);

export const sortByTime = <T extends TimeValueTuple<unknown> | TimeValueObject<unknown>>(
  a: T,
  b: T,
): number => {
  if (Array.isArray(a) && Array.isArray(b)) return a[0].getTime() - b[0].getTime();
  else if ("time" in a && "time" in b) return a.time.getTime() - b.time.getTime();
  return 0;
};

export const useTransform = <T>(
  values: Ref<number[]>,
  transformFn: (val: number, index: number) => T,
): ComputedRef<T[]> => computed(() => values.value.map(transformFn));

export const toValueObject = <T>(value: T): ValueObject<T> => ({ value });
export const toTimeValueObject = <T>([time, value]: TimeValueTuple<T>): TimeValueObject<T> => ({
  time,
  value,
});
export const toTimeValueTuple = <T>(value: TimeValueObject<T>): TimeValueTuple<T> => [
  new Date(value.time),
  value.value,
];

export const validateSafeRange = (
  thresholds: SafeRangeThresholds,
  value?: number | null,
): ValidationStatus => {
  if (value == undefined || isNaN(value)) {
    return ValidationStatus.UNKNOWN;
  } else if (value < thresholds[0] || value > thresholds[1]) {
    return ValidationStatus.WARN;
  } else {
    return ValidationStatus.OK;
  }
};

export const useSafeRange = (
  thresholds: SafeRangeThresholds,
  value: Ref<number>,
): Ref<ValidationStatus> => computed(() => validateSafeRange(thresholds, value.value));

export const validateThreshold = (
  thresholds: Thresholds,
  value?: number | null,
): ValidationStatus => {
  if (value == undefined || isNaN(value)) {
    return ValidationStatus.UNKNOWN;
  } else if (value >= thresholds[1]) {
    return ValidationStatus.FAIL;
  } else if (value >= thresholds[0]) {
    return ValidationStatus.WARN;
  } else {
    return ValidationStatus.OK;
  }
};

export const useThresholds = (thresholds: Thresholds, value: Ref<number>): Ref<ValidationStatus> =>
  computed(() => validateThreshold(thresholds, value.value));

export const getOverallState = (states: ValidationStatus[]): ValidationStatus => {
  if (states.some((state) => state === ValidationStatus.FAIL)) return ValidationStatus.FAIL;
  else if (states.some((state) => state === ValidationStatus.WARN)) return ValidationStatus.WARN;
  else return ValidationStatus.OK;
};

export const getRoomState = (room: Room): RoomState => {
  const stateCO2 = validateThreshold(CO2_THRESHOLDS, extractActualCO2(room));
  const stateTemperature = validateThreshold(
    TEMPERATURE_THRESHOLDS,
    extractActualTemperature(room),
  );
  const stateHumidity = validateSafeRange(HUMIDITY_THRESHOLDS, extractActualHumidity(room));

  return {
    co2: stateCO2,
    temperature: stateTemperature,
    humidity: stateHumidity,
    overall: getOverallState([stateTemperature, stateHumidity, stateCO2]),
  };
};

export const toElementRefs = <Items extends unknown[]>(items: Ref<Items>) =>
  items.value.map((_, index) =>
    computed({
      get() {
        return items.value[index];
      },
      set(next: Items[typeof index]) {
        const copy = items.value.slice();
        copy[index] = next;
        items.value = copy as Items;
      },
    }),
  ) as { [K in keyof Items]: WritableComputedRef<Items[K]> };

export const hasLightControl = (room: Room) => room.lightingGroups.length > 0;
export const hasBlindsControl = (room: Room) => room.blinds.length > 0;
export const hasTemperatureControl = (room: Room) => !!room.airConditioning;
export const hasHumidityControl = (room: Room) => !!room.airConditioning;
export const hasCO2Control = (room: Room) => !!room.ventilation;
export const hasAmplifierControl = (room: Room) => !!room.amplifier;

export const extractActualHumidity = (room: Room) => room.airConditioning?.actualHumidity;
export const extractActualTemperature = (room: Room) => room.airConditioning?.actualTemperature;
export const extractActualCO2 = (room: Room) => room.ventilation?.actualCo2;

export const extractTemperatureSetpoint = (room: Room) => room.airConditioning?.temperatureSetpoint;
export const extractAmplifierStatus = (room: Room) => room.amplifier?.on;
export const extractHumiditySetpoint = (room: Room) => room.airConditioning?.humiditySetpoint;
export const extractCO2Setpoint = (room: Room) => room.ventilation?.co2Setpoint;

export const toUpperCamelCase = (str: string) => str.replace(/([A-Z])/g, " $1").trim();
export const toCapitalized = (str: string) =>
  `${str.charAt(0).toLocaleUpperCase()}${str.slice(1).toLocaleLowerCase()}`;

export const tScoped = (scope: string) => {
  const { t } = useI18n();

  return (key: string, value?: NamedValue) => {
    return value ? t(`${scope}.${key}`, value) : t(`${scope}.${key}`);
  };
};

export const objectFilter = <T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  predicate: (entry: [key: K, value: T[K]]) => boolean,
): Partial<T> =>
  Object.fromEntries(
    Object.entries(obj).filter((entry) => predicate(entry as [K, T[K]])),
  ) as Partial<T>;

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
export function isStamped<T>(input: unknown | Stamped<T>): input is Stamped<T>;
export function isStamped(input: unknown): input is Stamped<number>;
export function isStamped(input: unknown): boolean {
  if (Array.isArray(input)) return isStamped(input[0]);

  return typeof input === "object" && input !== null && "value" in input && "timestamp" in input;
}

export const stamp = <T>(value: MaybeRef<T>, timestamp = new Date()): Stamped<T> => ({
  value: unref(value),
  timestamp,
});
export const unstamp = <T>(input: T | Stamped<T>): T => (isStamped(input) ? input.value : input);

export const isStampedNumber = (item: unknown): item is Stamped<number> =>
  isStamped(item) && typeof item.value === "number";

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

export function toMap<K, V>(keys: K[] | readonly K[], mapFn: KeyMapFn<K, V>): Map<K, V>;
export function toMap<K extends string | number | symbol, V, T>(
  obj: Record<K, V>,
  mapFn: EntryMapFn<K, V, T>,
): Map<K, T>;
export function toMap<K, V, T>(
  input: Map<K, V> | Entries<K, V>,
  mapFn: EntryMapFn<K, V, T>,
): Map<K, T>;
export function toMap<K, V, T>(input: MapFrom<K, V>, mapFn: EntryMapFn<K, V, T>) {
  return new Map(toEntries(input, mapFn));
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

function isChartType<T extends ChartDataType>(type: string) {
  function isChart(chart: StampedChart): chart is StampedChart<T>;
  function isChart(chart: SeriesChart): chart is SeriesChart<T>;
  function isChart(chart: StampedChart[]): chart is StampedChart<T>[];
  function isChart(chart: SeriesChart[]): chart is SeriesChart<T>[];
  function isChart(chart: StampedChart | StampedChart[] | SeriesChart | SeriesChart[]): boolean;
  function isChart(chart: StampedChart | StampedChart[] | SeriesChart | SeriesChart[]): boolean {
    if (!chart) return false;

    if (Array.isArray(chart)) {
      return chart.length > 0 && chart.every(isChart);
    }

    const [firstDataPoint] = chart.data;

    if (isStamped(firstDataPoint)) {
      return typeof firstDataPoint.value === type;
    }

    if (Array.isArray(firstDataPoint)) {
      const [, value] = firstDataPoint;
      return typeof value === type;
    }

    return false;
  }

  return isChart;
}
export const isNumberChart = isChartType<number>("number");
export const isStringChart = isChartType<string>("string");
export const isBooleanChart = isChartType<boolean>("boolean");

export const isRecord = <T extends Record<string, unknown>>(input: unknown): input is T =>
  typeof input === "object" && input !== null && !Array.isArray(input);

export const isHistoryOf = <T extends Record<string, unknown>>(
  source: T,
  target: unknown,
): target is History<T> => {
  if (!isRecord(source) || !isRecord(target)) return false;

  return Object.keys(source).some((key) => {
    const sourceValue = source[key as keyof T];
    const targetValue = (target as History<T>)[key as keyof History<T>];

    if (isStamped<ChartDataType>(sourceValue)) {
      return Array.isArray(targetValue) && targetValue.every(isStamped<ChartDataType>);
    } else if (isRecord(sourceValue)) {
      return isHistoryOf(sourceValue as T, targetValue);
    } else {
      return true;
    }
  });
};

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

export const useFixed = (value: Ref<number | undefined | null>, digits: number) =>
  computed(() => {
    if (value.value == undefined) {
      return [undefined, undefined];
    } else {
      return value.value.toFixed(digits).split(".").map(Number);
    }
  });

export const refValue = unref;

export const useAutoFocus = <T extends HTMLElement>(
  ref: Ref<{ $el: T } | null>,
  enabled: MaybeRef<boolean> = true,
) => onMounted(() => unref(enabled) && useTimeoutFn(() => ref.value?.$el?.focus(), 100));
