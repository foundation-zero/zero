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

export type ControlLog<Type extends ControlType = ControlType> = ValueWithTime & {
  id: string;
  control: RoomControl<Type>;
};

export type SensorLog<Type extends SensorType = SensorType> = ValueWithTime & {
  id: string;
  sensor: RoomSensor<Type>;
};

export interface RoomControl<Type extends ControlType = ControlType> {
  id: string;
  type: Type;
  time: number;
  value: number;
  name: string;
}

export interface RoomSensor<Type extends SensorType = SensorType> {
  id: string;
  type: Type;
  time: number;
  value: number;
  name?: string;
}

export interface Meta<T extends Record<string, unknown>> {
  meta: T;
}

export type BlindsType = "blind" | "shear";

export type BlindsMeta = {
  opacity: BlindsType;
  group: string;
};

export type LightingControl = RoomControl<ControlType.LIGHT>;
export type BlindsControl = RoomControl<ControlType.BLIND> & Meta<BlindsMeta>;
export type AmplifierControl = RoomControl<ControlType.AMPLIFIER>;
export type TemperatureControl = RoomControl<ControlType.TEMPERATURE>;
export type HumidityControl = RoomControl<ControlType.HUMIDITY>;
export type CO2Control = RoomControl<ControlType.CO2>;

export type TemperatureSensor = RoomSensor<SensorType.TEMPERATURE>;
export type HumiditySensor = RoomSensor<SensorType.HUMIDITY>;
export type CO2Sensor = RoomSensor<SensorType.CO2>;
export type PresenceSensor = RoomSensor<SensorType.PRESENCE>;

export type ControlTypeMap = {
  [ControlType.CO2]: CO2Control;
  [ControlType.TEMPERATURE]: TemperatureControl;
  [ControlType.HUMIDITY]: HumidityControl;
  [ControlType.AMPLIFIER]: AmplifierControl;
  [ControlType.BLIND]: BlindsControl;
  [ControlType.LIGHT]: LightingControl;
};

export type SensorTypeMap = {
  [SensorType.CO2]: CO2Sensor;
  [SensorType.TEMPERATURE]: TemperatureSensor;
  [SensorType.HUMIDITY]: HumiditySensor;
  [SensorType.PRESENCE]: PresenceSensor;
};

export interface Room {
  id: string;
  name: string;
  group: RoomGroup;
  roomsControls: RoomControl[];
  roomsSensors: RoomSensor[];
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

export type LightGroup = ControlGroup<LightingControl>;
export type BlindsGroup = ControlGroup<BlindsControl>;

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
