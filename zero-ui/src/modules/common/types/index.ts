import { Ref } from "vue";

export type Nullable<T> = T | null;
export type PromiseFn<T = unknown> = () => Promise<T> | T;
export type PID = [proportional: number, integral: number, derivative: number];

export type Stamped<T> = { value: T; timestamp: Date };
export type StampedWithSource<T> = { value: T; timestamp: Date; source: string };
export type Unstamp<T> =
  T extends Stamped<infer U>
    ? U
    : T extends StampedWithSource<infer U>
      ? U
      : T extends Record<string, Stamped<unknown>>
        ? { [K in keyof T]: Unstamp<T[K]> }
        : never;

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

export type TupleIndices<T extends readonly unknown[]> =
  Extract<keyof T, `${number}`> extends `${infer N extends number}` ? N : never;

export interface Breakpoints {
  tablet: boolean;
  phone: boolean;
  landscape: boolean;
  portrait: boolean;
  touch: boolean;
  desktop: boolean;
}

export const enum Roles {
  User = "user",
  Admin = "admin",
}

export interface HasuraJWTToken {
  "https://hasura.io/jwt/claims": {
    "x-hasura-default-role": Roles;
    "x-hasura-allowed-roles": Array<Roles>;
    "x-hasura-cabin"?: string;
  };
}
