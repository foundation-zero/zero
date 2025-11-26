export type Stamped<T> = { value: T; timestamp: Date };
export type Unstamp<T> = T extends Stamped<infer U> ? U : never;

export type Field<T> = Record<string, Stamped<T>>;
export type Component = Record<string, Field<number>>;

export type ChartDataType = number | boolean | string;
export type TimeSeriesData<T extends ChartDataType = ChartDataType> = [time: Date, value: T];
export type SeriesData = { value: number };

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

export type Entries<T> =
  T extends Map<infer K, infer V>
    ? V extends Map<unknown, unknown>
      ? [key: K, value: Entries<V>[]]
      : [key: K, value: V]
    : never;
