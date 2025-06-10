import { Blinds, LightingGroups } from "@/gql/graphql";

export interface Room {
  id: string;
  name: string;
  group: RoomGroup;
  amplifierOn: boolean;
  temperatureSetpoint: number;
  actualTemperature: number;
  actualHumidity: number;
  actualCO2: number;
  lights: LightGroup[];
  blinds: BlindsGroup[];
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

export type LightGroup = ControlGroup<LightingGroups>;
export type BlindsGroup = ControlGroup<Blinds>;

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
