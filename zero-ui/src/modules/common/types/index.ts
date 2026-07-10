import { PID } from "@/modules/thrs/types";
import { Ref } from "vue";

export type Stamped<T> = { value: T; timestamp: Date };
export type Unstamp<T> = T extends Stamped<infer U> ? U : never;
export type History<T> =
  T extends Stamped<infer U extends ChartDataType>
    ? TimeSeriesData<U>[]
    : T extends Record<string, unknown>
      ? { [K in keyof T as History<T[K]> extends never ? never : K]: History<T[K]> }
      : T;

export type Field<T> = Record<string, Stamped<T>>;
export type Component = Record<string, Field<number>>;

export type ChartDataType = number | boolean | string | undefined | PID;
export type TimeSeriesData<T extends ChartDataType = ChartDataType> = [time: Date, value: T];
export type SeriesData = { value: number };

export type RecordIndex = string | number | symbol;

export type StringKeyOf<T> = Extract<keyof T, string>;

export interface Chart<
  Type extends ChartDataType,
  Value extends Stamped<Type> | TimeSeriesData<Type>,
> {
  name: string;
  data: Value[];
}

export type StampedChart<Type extends ChartDataType = ChartDataType> = Chart<Type, Stamped<Type>>;
export type SeriesChart<Type extends ChartDataType = ChartDataType> = Chart<
  Type,
  TimeSeriesData<Type>
>;

export type MapEntries<T> =
  T extends Map<infer K, infer V>
    ? V extends Map<unknown, unknown>
      ? [key: K, value: MapEntries<V>[]]
      : [key: K, value: V]
    : never;

export type Refs<T extends object> = {
  [K in keyof T]: Ref<T[K]>;
};
export type Entries<K, V> = [key: K, value: V][];

export type NavItem = {
  title: string;
  to: string;
};
