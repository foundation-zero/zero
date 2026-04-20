export const enum ControlType {
  LIGHT = "lights",
  BLIND = "blinds",
  AMPLIFIER = "amplifier",
  TEMPERATURE = "temperature",
  HUMIDITY = "humidity",
  CO2 = "co2",
}

export const enum SensorType {
  TEMPERATURE = "temperature",
  HUMIDITY = "humidity",
  CO2 = "co2",
  PRESENCE = "presence",
}

export interface ValueWithTime {
  time: Date;
  value: number;
}

export interface Meta<T extends Record<string, unknown>> {
  meta: T;
}

export type BlindsType = "blind" | "shear";

export type BlindsMeta = {
  opacity: BlindsType;
  group: string;
};

export type LightingGroup = {
  id: string;
  name: string;
  level: number;
};

export type Blind = {
  id: string;
  name: string;
  level: number;
  group: string;
};

export type AirConditioning = {
  temperatureSetpoint: number;
  humiditySetpoint: number;
  actualTemperature: number;
  actualHumidity: number;
};

export type Ventilation = {
  co2Setpoint: number;
  actualCo2: number;
};

export type Amplifier = {
  on: boolean;
};

export interface Room {
  id: string;
  name: string;
  group: RoomGroup;
  lightingGroups: LightingGroup[];
  blinds: Blind[];
  airConditioning?: AirConditioning;
  ventilation?: Ventilation;
  amplifier?: Amplifier;
}

export interface ShipArea {
  name: string;
  group: RoomGroup;
  rooms: Room[];
}

export const enum RoomGroup {
  AFT = "AFT",
  MID = "MID",
  FORE = "FORE",
  UPPERDECK = "UPPERDECK",
  HALLWAYS = "HALLWAYS",
}

export interface Breakpoints {
  tablet: boolean;
  phone: boolean;
  landscape: boolean;
  portrait: boolean;
  touch: boolean;
  desktop: boolean;
}

export interface ControlGroup<T> {
  name: string;
  controls: T[];
}

export type LightGroup = ControlGroup<LightingGroup>;
export type BlindsGroup = ControlGroup<Blind>;

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

export const enum ValidationStatus {
  OK = "ok",
  WARN = "warn",
  FAIL = "fail",
  UNKNOWN = "unknown",
}

export const enum Units {
  PPM = "ppm",
}

export type ValidateFn<T> = (value: T) => ValidationStatus;

export interface ValueObject<V> {
  value: V;
}

export interface TimeValueObject<V> extends ValueObject<V> {
  time: Date;
}

export type TimeValueTuple<V> = [time: Date, value: V];

export type NumValueObject = ValueObject<number>;

export type Thresholds = [lower: number, upper: number, ...other: number[]];
export type SafeRangeThresholds = [min: number, max: number];

export interface RoomState {
  co2: ValidationStatus;
  temperature: ValidationStatus;
  humidity: ValidationStatus;
  overall: ValidationStatus;
}

export interface RoomWithState {
  room: Room;
  state: RoomState;
}

export const enum ChartPeriod {
  HOUR = "hour",
  DAY = "day",
  WEEK = "week",
  MONTH = "month",
  YEAR = "year",
}

export type PromiseFn<T = unknown> = () => Promise<T> | T;
